from typing import Protocol
from src.features.security.contracts.security_types import (
    SecurityInspectionRequestDTO,
    SecurityInspectionResultDTO,
)
from src.features.security.infrastructure.ports.security_ports import ThreatDetectionPort
from src.features.security.domain.workflows.security_workflow import SecurityWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class SecurityServiceDeps(Protocol):
    threat_port: ThreatDetectionPort


class SecurityService:
    def __init__(self, deps: SecurityServiceDeps) -> None:
        self._workflow = SecurityWorkflow(threat_port=deps.threat_port)

    async def inspect_content(
        self,
        request: SecurityInspectionRequestDTO
    ) -> Result[SecurityInspectionResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="SECURITY_SERVICE_ERROR", status_code=500))
