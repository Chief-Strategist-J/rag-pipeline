from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.features.retrieve.contracts.retrieve_types import ScoredChunkDTO


class RerankedChunkDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunkId: str
    documentId: str
    tenantId: str
    version: int
    sectionTitle: str
    content: str
    relevanceScore: float
    originalRank: int
    rerankedRank: int
    metadata: Dict[str, str] = Field(default_factory=dict)


class RerankRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    candidates: Sequence[ScoredChunkDTO]
    topK: int = 5
    minScoreThreshold: float = 0.0
    correlationId: str


class RerankResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    totalEvaluated: int
    selectedCount: int
    rankedChunks: Sequence[RerankedChunkDTO]
    latencyMs: float
    correlationId: str
