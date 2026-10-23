from typing import Protocol
from src.features.rerank.contracts.rerank_types import (
    RerankRequestDTO,
    RerankResultDTO,
)
from src.features.rerank.infrastructure.ports.rerank_ports import CrossEncoderModelPort
from src.features.rerank.domain.workflows.rerank_workflow import RerankWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class RerankServiceDeps(Protocol):
    model_port: CrossEncoderModelPort


class RerankService:
    def __init__(self, deps: RerankServiceDeps) -> None:
        self._workflow = RerankWorkflow(model_port=deps.model_port)

    async def rerank_candidates(
        self,
        request: RerankRequestDTO
    ) -> Result[RerankResultDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="RERANK_SERVICE_ERROR", status_code=500))
