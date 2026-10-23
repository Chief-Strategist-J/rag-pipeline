from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.generate.contracts.generate_types import (
    GenerationRequestDTO,
    GenerationResponseDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[GenerationRequestDTO, ValidationError]:
    try:
        dto = GenerationRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.query.strip():
            return Err(ValidationError("query must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid generation request payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid generation request payload: {str(err)}"))


def map_output_to_api(dto: GenerationResponseDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "query": dto.query,
        "answer": dto.answer,
        "abstained": dto.abstained,
        "citedChunkIds": list(dto.citedChunkIds),
        "inputTokens": dto.inputTokens,
        "outputTokens": dto.outputTokens,
        "modelName": dto.modelName,
        "correlationId": dto.correlationId
    }
