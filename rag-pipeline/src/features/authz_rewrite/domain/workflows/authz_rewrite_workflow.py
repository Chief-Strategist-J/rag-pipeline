from typing import Tuple
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    RewrittenQueryOutputDTO,
    PermissionScope,
)
from src.features.authz_rewrite.infrastructure.ports.authz_rewrite_repository_port import (
    AuthzPermissionPort,
    QueryRewriteLlmPort,
)
from src.features.authz_rewrite.domain.rules.authz_rewrite_rules import can_skip_rewrite
from src.features.authz_rewrite.domain.machines.authz_rewrite_machine import (
    RewriteState,
    RewriteEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class AuthzRewriteWorkflow:
    def __init__(
        self,
        authz_port: AuthzPermissionPort,
        rewrite_port: QueryRewriteLlmPort
    ) -> None:
        self._authz_port = authz_port
        self._rewrite_port = rewrite_port

    async def run(
        self,
        input_dto: RewriteInputDTO
    ) -> Result[RewrittenQueryOutputDTO, ApplicationError]:
        state = RewriteState.UNPROCESSED

        scope_res = await self._authz_port.get_permission_scope(
            tenant_id=input_dto.tenantId,
            user_id=input_dto.userId
        )
        if not scope_res.is_ok:
            return Err(scope_res.error)

        t1 = transition_state(state, RewriteEvent.RESOLVE_SCOPE)
        if not t1.is_ok:
            return Err(t1.error)
        state = t1.value
        scope = scope_res.value

        if can_skip_rewrite(input_dto):
            t_bypass = transition_state(state, RewriteEvent.BYPASS)
            if not t_bypass.is_ok:
                return Err(t_bypass.error)
            state = t_bypass.value
            final_query = input_dto.query
            was_rewritten = False
        else:
            rewrite_res = await self._rewrite_port.rewrite_query(
                query=input_dto.query,
                history=input_dto.conversationHistory
            )
            t_rew = transition_state(state, RewriteEvent.REWRITE)
            if not t_rew.is_ok:
                return Err(t_rew.error)
            state = t_rew.value

            final_query = rewrite_res.value if rewrite_res.is_ok else input_dto.query
            was_rewritten = rewrite_res.is_ok and (final_query != input_dto.query)

        t_comp = transition_state(state, RewriteEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            RewrittenQueryOutputDTO(
                originalQuery=input_dto.query,
                rewrittenQuery=final_query,
                wasRewritten=was_rewritten,
                permissionScope=scope,
                resolvedTenantId=input_dto.tenantId
            )
        )
