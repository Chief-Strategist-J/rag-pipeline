from typing import Protocol
from src.features.output_guard.contracts.output_guard_types import (
    GuardInspectionRequestDTO,
    GuardInspectionResultDTO,
)
from src.features.output_guard.infrastructure.ports.output_guard_ports import GuardAuditPort
from src.features.output_guard.domain.workflows.output_guard_workflow import OutputGuardWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class OutputGuardServiceDeps(Protocol):
    audit_port: GuardAuditPort


class OutputGuardService:
    def __init__(self, deps: OutputGuardServiceDeps) -> None:
        self._workflow = OutputGuardWorkflow(audit_port=deps.audit_port)

    async def inspect_and_sanitize(
        self,
        request: GuardInspectionRequestDTO
    ) -> Result[GuardInspectionResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="OUTPUT_GUARD_SERVICE_ERROR", status_code=500))
