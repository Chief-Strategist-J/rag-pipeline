from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedDocumentDTO,
    DocumentFormat,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[ParseRequestDTO, ValidationError]:
    try:
        dto = ParseRequestDTO.model_validate(payload)
        if not dto.documentId.strip():
            return Err(ValidationError("documentId must not be empty"))
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.rawContent.strip():
            return Err(ValidationError("rawContent must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid parse request payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid parse request payload: {str(err)}"))


def map_output_to_api(dto: ParsedDocumentDTO) -> Dict[str, Any]:
    return {
        "documentId": dto.documentId,
        "tenantId": dto.tenantId,
        "totalBlocks": dto.totalBlocks,
        "hasTables": dto.hasTables,
        "blocks": [
            {
                "blockId": b.blockId,
                "blockType": b.blockType.value,
                "content": b.content,
                "headingLevel": b.headingLevel,
                "sectionTitle": b.sectionTitle,
                "pageNumber": b.pageNumber,
                "tableMatrix": b.tableMatrix,
                "metadata": b.metadata
            }
            for b in dto.blocks
        ],
        "correlationId": dto.correlationId
    }
