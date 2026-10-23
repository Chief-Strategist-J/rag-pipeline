from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    ConversationTurn,
)
from src.features.authz_rewrite.domain.rules.authz_rewrite_rules import (
    can_skip_rewrite,
    is_valid_scope,
)


def test_can_skip_rewrite_on_empty_history():
    dto = RewriteInputDTO(
        query="What is the refund policy?",
        tenantId="tenant_1",
        userId="user_1",
        conversationHistory=(),
        skipRewriteIfFirstTurn=True
    )
    assert can_skip_rewrite(dto) is True


def test_cannot_skip_rewrite_when_history_present():
    dto = RewriteInputDTO(
        query="Can you summarize that?",
        tenantId="tenant_1",
        userId="user_1",
        conversationHistory=(
            ConversationTurn(role="user", content="Tell me about pricing"),
            ConversationTurn(role="assistant", content="Pricing starts at $10/mo"),
        ),
        skipRewriteIfFirstTurn=True
    )
    assert can_skip_rewrite(dto) is False


def test_is_valid_scope():
    allowed = ("tenant_1", "tenant_2")
    assert is_valid_scope("tenant_1", allowed) is True
    assert is_valid_scope("tenant_unknown", allowed) is False
    assert is_valid_scope("", allowed) is False
