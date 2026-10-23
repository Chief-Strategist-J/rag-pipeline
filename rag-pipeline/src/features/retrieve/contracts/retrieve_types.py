from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.features.authz_rewrite.contracts.authz_rewrite_types import PermissionScope


class ScoredChunkDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    chunkId: str
    documentId: str
    tenantId: str
    version: int
    sectionTitle: str
    content: str
    rrfScore: float
    denseRank: Optional[int] = None
    sparseRank: Optional[int] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class RetrieveRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    denseVector: Sequence[float]
    sparseIndices: Sequence[int]
    sparseValues: Sequence[float]
    permissionScope: PermissionScope
    candidatePoolSize: int = 50
    correlationId: str


class RetrieveResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    totalRetrieved: int
    candidates: Sequence[ScoredChunkDTO]
    correlationId: str
