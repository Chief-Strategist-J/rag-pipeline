from typing import Protocol
from src.features.data_integrity.contracts.data_integrity_types import (
    IntegrityValidationRequestDTO,
    IntegrityValidationResultDTO,
)
from src.features.data_integrity.infrastructure.ports.data_integrity_ports import (
    DataIntegrityRepositoryPort,
)
from src.features.data_integrity.domain.workflows.data_integrity_workflow import (
    DataIntegrityWorkflow,
)
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class DataIntegrityServiceDeps(Protocol):
    repo_port: DataIntegrityRepositoryPort


class DataIntegrityService:
    def __init__(self, deps: DataIntegrityServiceDeps) -> None:
        self._workflow = DataIntegrityWorkflow(repo_port=deps.repo_port)

    async def validate_and_enforce(
        self,
        request: IntegrityValidationRequestDTO
    ) -> Result[IntegrityValidationResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="DATA_INTEGRITY_SERVICE_ERROR", status_code=500))
