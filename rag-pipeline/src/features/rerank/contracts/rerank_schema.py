from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.rerank.contracts.rerank_types import (
    RerankRequestDTO,
    RerankResultDTO,
    RerankedChunkDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[RerankRequestDTO, ValidationError]:
    try:
        dto = RerankRequestDTO.model_validate(payload)
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if not dto.query.strip():
            return Err(ValidationError("query must not be empty"))
        if dto.topK < 1 or dto.topK > 20:
            return Err(ValidationError("topK must be between 1 and 20"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid rerank request payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid rerank request payload: {str(err)}"))


def map_output_to_api(dto: RerankResultDTO) -> Dict[str, Any]:
    return {
        "tenantId": dto.tenantId,
        "query": dto.query,
        "totalEvaluated": dto.totalEvaluated,
        "selectedCount": dto.selectedCount,
        "rankedChunks": [
            {
                "chunkId": c.chunkId,
                "documentId": c.documentId,
                "tenantId": c.tenantId,
                "version": c.version,
                "sectionTitle": c.sectionTitle,
                "content": c.content,
                "relevanceScore": round(c.relevanceScore, 6),
                "originalRank": c.originalRank,
                "rerankedRank": c.rerankedRank,
                "metadata": c.metadata
            }
            for c in dto.rankedChunks
        ],
        "latencyMs": round(dto.latencyMs, 2),
        "correlationId": dto.correlationId
    }
