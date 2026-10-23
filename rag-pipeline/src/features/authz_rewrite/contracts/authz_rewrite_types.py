from typing import Sequence, Optional
from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    role: str
    content: str


class RewriteInputDTO(BaseModel):
    query: str
    tenantId: str
    userId: str
    conversationHistory: Sequence[ConversationTurn] = Field(default_factory=tuple)
    skipRewriteIfFirstTurn: bool = True


class PermissionScope(BaseModel):
    tenantId: str
    userId: str
    allowedAcls: Sequence[str]
    allowedPartitions: Sequence[str]


class RewrittenQueryOutputDTO(BaseModel):
    originalQuery: str
    rewrittenQuery: str
    wasRewritten: bool
    permissionScope: PermissionScope
    resolvedTenantId: str
