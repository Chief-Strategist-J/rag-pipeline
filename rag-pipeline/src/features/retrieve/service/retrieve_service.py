from typing import Protocol
from src.features.retrieve.contracts.retrieve_types import (
    RetrieveRequestDTO,
    RetrieveResultDTO,
)
from src.features.retrieve.infrastructure.ports.retrieve_ports import HybridVectorSearchPort
from src.features.retrieve.domain.workflows.retrieve_workflow import RetrieveWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class RetrieveServiceDeps(Protocol):
    search_port: HybridVectorSearchPort


class RetrieveService:
    def __init__(self, deps: RetrieveServiceDeps) -> None:
        self._workflow = RetrieveWorkflow(search_port=deps.search_port)

    async def retrieve_candidates(
        self,
        request: RetrieveRequestDTO
    ) -> Result[RetrieveResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="RETRIEVE_SERVICE_ERROR", status_code=500))
