from typing import Dict, Any
from pydantic import ValidationError as PydanticValidationError
from src.features.chunk_dedup.contracts.chunk_dedup_types import (
    ChunkingRequestDTO,
    ChunkingResultDTO,
    ChunkDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ValidationError


def map_input_from_api(payload: Dict[str, Any]) -> Result[ChunkingRequestDTO, ValidationError]:
    try:
        dto = ChunkingRequestDTO.model_validate(payload)
        if not dto.documentId.strip():
            return Err(ValidationError("documentId must not be empty"))
        if not dto.tenantId.strip():
            return Err(ValidationError("tenantId must not be empty"))
        if dto.version <= 0:
            return Err(ValidationError("version must be greater than zero"))
        if len(dto.blocks) == 0:
            return Err(ValidationError("blocks must contain at least one block"))
        return Ok(dto)
    except PydanticValidationError as err:
        return Err(ValidationError(f"Invalid chunking request payload: {str(err)}"))
    except Exception as err:
        return Err(ValidationError(f"Invalid chunking request payload: {str(err)}"))


def map_output_to_api(dto: ChunkingResultDTO) -> Dict[str, Any]:
    return {
        "documentId": dto.documentId,
        "tenantId": dto.tenantId,
        "version": dto.version,
        "totalChunks": dto.totalChunks,
        "deduplicatedCount": dto.deduplicatedCount,
        "chunks": [
            {
                "chunkId": c.chunkId,
                "documentId": c.documentId,
                "tenantId": c.tenantId,
                "version": c.version,
                "offsetIndex": c.offsetIndex,
                "sectionTitle": c.sectionTitle,
                "content": c.content,
                "tokenCount": c.tokenCount,
                "contentHash": c.contentHash,
                "isCurrent": c.isCurrent,
                "metadata": c.metadata
            }
            for c in dto.chunks
        ],
        "correlationId": dto.correlationId
    }
