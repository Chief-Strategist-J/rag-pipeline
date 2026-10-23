from abc import ABC, abstractmethod
from typing import Sequence
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    PermissionScope,
    ConversationTurn,
)
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class AuthzPermissionPort(ABC):
    @abstractmethod
    async def get_permission_scope(
        self,
        tenant_id: str,
        user_id: str
    ) -> Result[PermissionScope, ApplicationError]:
        pass


class QueryRewriteLlmPort(ABC):
    @abstractmethod
    async def rewrite_query(
        self,
        query: str,
        history: Sequence[ConversationTurn]
    ) -> Result[str, ApplicationError]:
        pass
