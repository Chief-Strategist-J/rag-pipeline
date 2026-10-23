from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.features.rerank.contracts.rerank_types import RerankedChunkDTO


class GenerationRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    contextChunks: Sequence[RerankedChunkDTO]
    temperature: float = 0.0
    maxTokens: int = 512
    correlationId: str


class GenerationResponseDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    answer: str
    abstained: bool
    citedChunkIds: Sequence[str]
    inputTokens: int
    outputTokens: int
    modelName: str
    correlationId: str
