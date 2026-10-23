from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class GuardrailAction(str):
    PASSED = "PASSED"
    SANITIZED = "SANITIZED"
    REJECTED = "REJECTED"


class GuardInspectionRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    query: str
    rawAnswer: str
    providedChunkIds: Sequence[str]
    stripLinks: bool = True
    correlationId: str


class GuardInspectionResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    sanitizedAnswer: str
    action: str
    validCitationIds: Sequence[str]
    hallucinatedCitationIds: Sequence[str]
    removedLinksCount: int
    isGrounded: bool
    correlationId: str
