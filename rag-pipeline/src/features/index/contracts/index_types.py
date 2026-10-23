from enum import Enum
from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.features.embed_enrich.contracts.embed_enrich_types import EnrichedChunkVectorDTO


class CollectionStatus(str, Enum):
    CREATING = "CREATING"
    ACTIVE = "ACTIVE"
    SHADOWING = "SHADOWING"
    DRAINING = "DRAINING"
    DEPRECATED = "DEPRECATED"


class IndexCollectionMetaDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    collectionName: str
    tenantId: str
    version: str
    dimension: int
    status: CollectionStatus
    isPrimary: bool
    totalPoints: int
    createdAt: str


class IndexUpsertRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    collectionVersion: str
    vectors: Sequence[EnrichedChunkVectorDTO]
    correlationId: str


class IndexUpsertResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    collectionName: str
    tenantId: str
    upsertedCount: int
    status: str
    correlationId: str
