from typing import Protocol
from src.features.evals.contracts.evals_types import EvaluationReportDTO
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class EvalMetricStoragePort(Protocol):
    async def record_eval_report(
        self,
        report: EvaluationReportDTO
    ) -> Result[bool, ApplicationError]:
        ...
