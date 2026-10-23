from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeProcessingResultDTO,
    ChangeOperation,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[DocumentChangeEventDTO, ValidationError]:
    try:
        dto = DocumentChangeEventDTO.model_validate(payload)
        if not dto.eventId.strip():
            return Err(ValidationError("eventId must not be empty"))
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.documentId.strip():
            return Err(ValidationError("documentId must not be empty"))
        if dto.operation in (ChangeOperation.INSERT, ChangeOperation.UPDATE) and not dto.content:
            return Err(ValidationError("content is required for INSERT or UPDATE operations"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid change event payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid change event payload: {str(err)}"))


def map_output_to_api(dto: ChangeProcessingResultDTO) -> Dict[str, Any]:
    return {
        "eventId": dto.eventId,
        "tenantId": dto.tenantId,
        "documentId": dto.documentId,
        "operation": dto.operation.value,
        "status": dto.status,
        "downstreamNotified": dto.downstreamNotified,
        "affectedChunksCount": dto.affectedChunksCount,
        "correlationId": dto.correlationId
    }
