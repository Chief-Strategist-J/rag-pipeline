from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.observability.contracts.observability_types import (
    RequestTelemetryEnvelopeDTO,
    PipelineStageMetricsDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[RequestTelemetryEnvelopeDTO, ValidationError]:
    try:
        dto = RequestTelemetryEnvelopeDTO.model_validate(payload)
        if not dto.requestId.strip():
            return Err(ValidationError("requestId must not be empty"))
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.traceId.strip():
            return Err(ValidationError("traceId must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid telemetry envelope: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid telemetry envelope: {str(err)}"))


def map_output_to_api(dto: RequestTelemetryEnvelopeDTO) -> Dict[str, Any]:
    return {
        "requestId": dto.requestId,
        "tenantId": dto.tenantId,
        "userId": dto.userId,
        "traceId": dto.traceId,
        "stages": [
            {
                "stageName": s.stageName,
                "durationMs": round(s.durationMs, 2),
                "status": s.status,
                "attributes": s.attributes
            }
            for s in dto.stages
        ],
        "totalDurationMs": round(dto.totalDurationMs, 2),
        "rewrittenQuery": dto.rewrittenQuery,
        "retrievedChunkCount": dto.retrievedChunkCount,
        "rerankedChunkCount": dto.rerankedChunkCount,
        "promptTokens": dto.promptTokens,
        "generatedTokens": dto.generatedTokens,
        "hasError": dto.hasError,
        "timestamp": dto.timestamp,
        "correlationId": dto.correlationId
    }
