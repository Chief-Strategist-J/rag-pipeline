from typing import Sequence, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class SparseVectorDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    indices: Sequence[int]
    values: Sequence[float]


class EnrichedChunkVectorDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunkId: str
    documentId: str
    tenantId: str
    version: int
    sectionTitle: str
    content: str
    denseVector: Sequence[float]
    sparseVector: SparseVectorDTO
    aclTags: Sequence[str]
    metadata: Dict[str, str] = Field(default_factory=dict)
    createdAt: str


class EmbeddingRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    documentId: str
    version: int
    aclTags: Sequence[str] = Field(default_factory=tuple)
    chunks: Sequence[Dict[str, str]]
    correlationId: str


class EmbeddingResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    documentId: str
    version: int
    totalVectors: int
    vectors: Sequence[EnrichedChunkVectorDTO]
    correlationId: str
