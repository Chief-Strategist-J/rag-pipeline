from typing import Sequence, Dict, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class GateLevel(str, Enum):
    INGRESS = "INGRESS"
    DOMAIN = "DOMAIN"
    STORAGE = "STORAGE"


class IntegrityViolationDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    gate: GateLevel
    field: str
    ruleName: str
    message: str
    rejectedValue: Optional[str] = None


class EntityPayloadDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: Optional[str] = None
    publicId: Optional[str] = None
    tenantId: str
    source: str
    externalId: str
    correlationId: str
    status: str
    amount: float
    currency: str
    shippedAt: Optional[str] = None
    version: int = 1
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IntegrityValidationRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    tenantId: str
    correlationId: str
    entityName: str
    payload: Dict[str, Any]


class IntegrityValidationResultDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    tenantId: str
    correlationId: str
    isValid: bool
    normalizedEntity: Optional[EntityPayloadDTO] = None
    violations: Sequence[IntegrityViolationDTO] = Field(default_factory=tuple)
