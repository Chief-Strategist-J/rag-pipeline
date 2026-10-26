from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class PipelineStageMetricsDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    stageName: str
    durationMs: float
    status: str
    attributes: Dict[str, str] = Field(default_factory=dict)


class RequestTelemetryEnvelopeDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    requestId: str
    tenantId: str
    userId: str
    traceId: str
    stages: Sequence[PipelineStageMetricsDTO]
    totalDurationMs: float
    rewrittenQuery: Optional[str] = None
    retrievedChunkCount: int = 0
    rerankedChunkCount: int = 0
    promptTokens: int = 0
    generatedTokens: int = 0
    generatedAnswer: Optional[str] = None
    hasError: bool = False
    timestamp: str
    correlationId: str
