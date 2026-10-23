from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.evals.contracts.evals_types import (
    RetrievalEvalInputDTO,
    AnswerEvalInputDTO,
    EvaluationReportDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_retrieval_eval_from_api(payload: Dict[str, Any]) -> Result[RetrievalEvalInputDTO, ValidationError]:
    try:
        dto = RetrievalEvalInputDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.queryId.strip():
            return Err(ValidationError("queryId must not be empty"))
        if dto.k <= 0:
            return Err(ValidationError("k must be greater than zero"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid retrieval eval payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid retrieval eval payload: {str(err)}"))


def map_output_to_api(dto: EvaluationReportDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "queryId": dto.queryId,
        "recallAtK": round(dto.recallAtK, 4),
        "mrr": round(dto.mrr, 4),
        "faithfulnessScore": round(dto.faithfulnessScore, 4),
        "isAbstainAppropriate": dto.isAbstainAppropriate,
        "evaluationStatus": dto.evaluationStatus,
        "correlationId": dto.correlationId
    }
