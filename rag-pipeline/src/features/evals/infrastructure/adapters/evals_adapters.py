from typing import List
from src.features.evals.infrastructure.ports.evals_ports import EvalMetricStoragePort
from src.features.evals.contracts.evals_types import EvaluationReportDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryEvalMetricStorageAdapter(EvalMetricStoragePort):
    def __init__(self) -> None:
        self.reports: List[EvaluationReportDTO] = []

    async def record_eval_report(
        self,
        report: EvaluationReportDTO
    ) -> Result[bool, ApplicationError]:
        self.reports.append(report)
        return Ok(True)
