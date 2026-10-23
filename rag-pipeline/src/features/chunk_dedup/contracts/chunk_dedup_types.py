from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.features.parse.contracts.parse_types import ParsedBlockDTO


class ChunkDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunkId: str
    documentId: str
    tenantId: str
    version: int
    offsetIndex: int
    sectionTitle: str
    content: str
    tokenCount: int
    contentHash: str
    isCurrent: bool = True
    metadata: Dict[str, str] = Field(default_factory=dict)


class ChunkingRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documentId: str
    tenantId: str
    version: int
    blocks: Sequence[ParsedBlockDTO]
    targetMinTokens: int = 300
    targetMaxTokens: int = 800
    correlationId: str


class ChunkingResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documentId: str
    tenantId: str
    version: int
    totalChunks: int
    deduplicatedCount: int
    chunks: Sequence[ChunkDTO]
    correlationId: str
