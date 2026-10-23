from typing import Protocol
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    RewrittenQueryOutputDTO,
)
from src.features.authz_rewrite.infrastructure.ports.authz_rewrite_repository_port import (
    AuthzPermissionPort,
    QueryRewriteLlmPort,
)
from src.features.authz_rewrite.domain.rules.authz_rewrite_rules import can_skip_rewrite
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class AuthzRewriteServiceDeps(Protocol):
    authz_port: AuthzPermissionPort
    rewrite_port: QueryRewriteLlmPort


class AuthzRewriteService:
    def __init__(self, deps: AuthzRewriteServiceDeps) -> None:
        self._authz_port = deps.authz_port
        self._rewrite_port = deps.rewrite_port

    async def execute(
        self,
        input_dto: RewriteInputDTO
    ) -> Result[RewrittenQueryOutputDTO, ApplicationError]:
        try:
            scope_result = await self._authz_port.get_permission_scope(
                tenant_id=input_dto.tenantId,
                user_id=input_dto.userId
            )
            if not scope_result.is_ok:
                return Err(scope_result.error)

            scope = scope_result.value

            if can_skip_rewrite(input_dto):
                return Ok(
                    RewrittenQueryOutputDTO(
                        originalQuery=input_dto.query,
                        rewrittenQuery=input_dto.query,
                        wasRewritten=False,
                        permissionScope=scope,
                        resolvedTenantId=input_dto.tenantId
                    )
                )

            rewrite_result = await self._rewrite_port.rewrite_query(
                query=input_dto.query,
                history=input_dto.conversationHistory
            )

            final_query = rewrite_result.value if rewrite_result.is_ok else input_dto.query
            was_rewritten = rewrite_result.is_ok and (final_query != input_dto.query)

            return Ok(
                RewrittenQueryOutputDTO(
                    originalQuery=input_dto.query,
                    rewrittenQuery=final_query,
                    wasRewritten=was_rewritten,
                    permissionScope=scope,
                    resolvedTenantId=input_dto.tenantId
                )
            )
        except Exception as err:
            return Err(ApplicationError(str(err), code="AUTHZ_REWRITE_SERVICE_ERROR", status_code=500))
