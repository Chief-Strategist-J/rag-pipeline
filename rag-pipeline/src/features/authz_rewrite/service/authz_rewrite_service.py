from typing import Protocol
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    RewrittenQueryOutputDTO,
)
from src.features.authz_rewrite.infrastructure.ports.authz_rewrite_repository_port import (
    AuthzPermissionPort,
    QueryRewriteLlmPort,
)
from src.features.authz_rewrite.domain.workflows.authz_rewrite_workflow import AuthzRewriteWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class AuthzRewriteServiceDeps(Protocol):
    authz_port: AuthzPermissionPort
    rewrite_port: QueryRewriteLlmPort


class AuthzRewriteService:
    def __init__(self, deps: AuthzRewriteServiceDeps) -> None:
        self._workflow = AuthzRewriteWorkflow(
            authz_port=deps.authz_port,
            rewrite_port=deps.rewrite_port
        )

    async def execute(
        self,
        input_dto: RewriteInputDTO
    ) -> Result[RewrittenQueryOutputDTO, ApplicationError]:
        try:
            return await self._workflow.run(input_dto)
        except Exception as err:
            return Err(ApplicationError(str(err), code="AUTHZ_REWRITE_SERVICE_ERROR", status_code=500))
