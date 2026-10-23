from typing import Sequence
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    ConversationTurn,
)


def can_skip_rewrite(input_dto: RewriteInputDTO) -> bool:
    if not input_dto.skipRewriteIfFirstTurn:
        return False
    if len(input_dto.conversationHistory) == 0:
        return True
    return False


def is_valid_scope(tenant_id: str, allowed_tenants: Sequence[str]) -> bool:
    if not tenant_id:
        return False
    return tenant_id in allowed_tenants
