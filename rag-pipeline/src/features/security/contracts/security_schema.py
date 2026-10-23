from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.security.contracts.security_types import (
    SecurityInspectionRequestDTO,
    SecurityInspectionResultDTO,
    DetectedThreatDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[SecurityInspectionRequestDTO, ValidationError]:
    try:
        dto = SecurityInspectionRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.content.strip():
            return Err(ValidationError("content must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid security inspection payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid security inspection payload: {str(err)}"))


def map_output_to_api(dto: SecurityInspectionResultDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "isSafe": dto.isSafe,
        "sanitizedContent": dto.sanitizedContent,
        "threats": [
            {
                "threatType": t.threatType,
                "severity": t.severity,
                "matchedPattern": t.matchedPattern,
                "spanOffset": t.spanOffset
            }
            for t in dto.threats
        ],
        "threatCount": dto.threatCount,
        "correlationId": dto.correlationId
    }
