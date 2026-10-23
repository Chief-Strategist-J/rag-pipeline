from typing import Sequence, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class SecurityThreatSeverity(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DetectedThreatDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    threatType: str
    severity: str
    matchedPattern: str
    spanOffset: int


class SecurityInspectionRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    content: str
    sourceType: str = "RETRIEVED_DOCUMENT"
    correlationId: str


class SecurityInspectionResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    isSafe: bool
    sanitizedContent: str
    threats: Sequence[DetectedThreatDTO]
    threatCount: int
    correlationId: str
