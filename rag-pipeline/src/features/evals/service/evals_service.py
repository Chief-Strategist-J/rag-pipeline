from typing import Protocol
from src.features.evals.contracts.evals_types import (
    RetrievalEvalInputDTO,
    AnswerEvalInputDTO,
    EvaluationReportDTO,
)
from src.features.evals.infrastructure.ports.evals_ports import EvalMetricStoragePort
from src.features.evals.domain.workflows.evals_workflow import EvalsWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class EvalsServiceDeps(Protocol):
    storage_port: EvalMetricStoragePort


class EvalsService:
    def __init__(self, deps: EvalsServiceDeps) -> None:
        self._workflow = EvalsWorkflow(storage_port=deps.storage_port)

    async def evaluate_turn(
        self,
        retrieval_input: RetrievalEvalInputDTO,
        answer_input: AnswerEvalInputDTO
    ) -> Result[EvaluationReportDTO, ApplicationError]:
        try:
            return await self._workflow.execute(retrieval_input, answer_input)
        except Exception as err:
            return Err(ApplicationError(str(err), code="EVALS_SERVICE_ERROR", status_code=500))
