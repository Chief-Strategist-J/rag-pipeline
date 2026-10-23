from enum import Enum
from typing import Sequence, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ChangeOperation(str, Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    ACL_UPDATE = "ACL_UPDATE"


class DocumentChangeEventDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eventId: str
    tenantId: str
    documentId: str
    operation: ChangeOperation
    version: int
    source: str
    content: Optional[str] = None
    aclTags: Sequence[str] = Field(default_factory=tuple)
    metadata: Dict[str, str] = Field(default_factory=dict)
    timestamp: str
    correlationId: str


class ChangeProcessingResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    eventId: str
    tenantId: str
    documentId: str
    operation: ChangeOperation
    status: str
    downstreamNotified: bool
    affectedChunksCount: int
    correlationId: str
