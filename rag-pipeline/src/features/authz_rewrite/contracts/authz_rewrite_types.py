from typing import Sequence
from pydantic import BaseModel, Field, ConfigDict


class ConversationTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: str
    content: str


class RewriteInputDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    query: str
    tenantId: str
    userId: str
    conversationHistory: Sequence[ConversationTurn] = Field(default_factory=tuple)
    skipRewriteIfFirstTurn: bool = True


class PermissionScope(BaseModel):
    model_config = ConfigDict(extra="forbid")
    tenantId: str
    userId: str
    allowedAcls: Sequence[str]
    allowedPartitions: Sequence[str]


class RewrittenQueryOutputDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    originalQuery: str
    rewrittenQuery: str
    wasRewritten: bool
    permissionScope: PermissionScope
    resolvedTenantId: str
