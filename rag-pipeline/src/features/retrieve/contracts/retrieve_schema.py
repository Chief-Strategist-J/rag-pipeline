from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.retrieve.contracts.retrieve_types import (
    RetrieveRequestDTO,
    RetrieveResultDTO,
    ScoredChunkDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[RetrieveRequestDTO, ValidationError]:
    try:
        dto = RetrieveRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.query.strip():
            return Err(ValidationError("query must not be empty"))
        if len(dto.denseVector) == 0:
            return Err(ValidationError("denseVector must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid retrieve request payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid retrieve request payload: {str(err)}"))


def map_output_to_api(dto: RetrieveResultDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "query": dto.query,
        "totalRetrieved": dto.totalRetrieved,
        "candidates": [
            {
                "chunkId": c.chunkId,
                "documentId": c.documentId,
                "tenantId": c.tenantId,
                "version": c.version,
                "sectionTitle": c.sectionTitle,
                "content": c.content,
                "rrfScore": round(c.rrfScore, 6),
                "denseRank": c.denseRank,
                "sparseRank": c.sparseRank,
                "metadata": c.metadata
            }
            for c in dto.candidates
        ],
        "correlationId": dto.correlationId
    }
