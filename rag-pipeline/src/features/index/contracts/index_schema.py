from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.index.contracts.index_types import (
    IndexUpsertRequestDTO,
    IndexUpsertResultDTO,
    IndexCollectionMetaDTO,
    CollectionStatus,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[IndexUpsertRequestDTO, ValidationError]:
    try:
        dto = IndexUpsertRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.collectionVersion.strip():
            return Err(ValidationError("collectionVersion must not be empty"))
        if len(dto.vectors) == 0:
            return Err(ValidationError("vectors must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid index upsert payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid index upsert payload: {str(err)}"))


def map_output_to_api(dto: IndexUpsertResultDTO) -> Dict[str, Any]:
    return {
        "collectionName": dto.collectionName,
        "tenantId": dto.tenantId,
        "upsertedCount": dto.upsertedCount,
        "status": dto.status,
        "correlationId": dto.correlationId
    }
