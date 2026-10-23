from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EmbeddingRequestDTO,
    EmbeddingResultDTO,
    EnrichedChunkVectorDTO,
    SparseVectorDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[EmbeddingRequestDTO, ValidationError]:
    try:
        dto = EmbeddingRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.documentId.strip():
            return Err(ValidationError("documentId must not be empty"))
        if len(dto.chunks) == 0:
            return Err(ValidationError("chunks must not be empty"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid embedding request payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid embedding request payload: {str(err)}"))


def map_output_to_api(dto: EmbeddingResultDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "documentId": dto.documentId,
        "version": dto.version,
        "totalVectors": dto.totalVectors,
        "vectors": [
            {
                "chunkId": v.chunkId,
                "documentId": v.documentId,
                "tenantId": v.tenantId,
                "version": v.version,
                "sectionTitle": v.sectionTitle,
                "content": v.content,
                "denseVector": list(v.denseVector),
                "sparseVector": {
                    "indices": list(v.sparseVector.indices),
                    "values": list(v.sparseVector.values)
                },
                "aclTags": list(v.aclTags),
                "metadata": v.metadata,
                "createdAt": v.createdAt
            }
            for v in dto.vectors
        ],
        "correlationId": dto.correlationId
    }
