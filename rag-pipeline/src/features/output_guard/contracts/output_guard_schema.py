from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.output_guard.contracts.output_guard_types import (
    GuardInspectionRequestDTO,
    GuardInspectionResultDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[GuardInspectionRequestDTO, ValidationError]:
    try:
        dto = GuardInspectionRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.rawAnswer.strip():
            return Err(ValidationError("rawAnswer must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid output guard payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid output guard payload: {str(err)}"))


def map_output_to_api(dto: GuardInspectionResultDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "sanitizedAnswer": dto.sanitizedAnswer,
        "action": dto.action,
        "validCitationIds": list(dto.validCitationIds),
        "hallucinatedCitationIds": list(dto.hallucinatedCitationIds),
        "removedLinksCount": dto.removedLinksCount,
        "isGrounded": dto.isGrounded,
        "correlationId": dto.correlationId
    }
