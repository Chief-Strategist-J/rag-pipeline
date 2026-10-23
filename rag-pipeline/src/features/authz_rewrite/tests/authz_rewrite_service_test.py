import pytest
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    ConversationTurn,
    PermissionScope,
)
from src.features.authz_rewrite.service.authz_rewrite_service import (
    AuthzRewriteService,
    AuthzRewriteServiceDeps,
)
from src.features.authz_rewrite.infrastructure.ports.authz_rewrite_repository_port import (
    AuthzPermissionPort,
    QueryRewriteLlmPort,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MockAuthzPort(AuthzPermissionPort):
    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail

    async def get_permission_scope(
        self,
        tenant_id: str,
        user_id: str
    ) -> Result[PermissionScope, ApplicationError]:
        if self.should_fail:
            return Err(ApplicationError("DB error", code="DB_FAIL", status_code=500))
        return Ok(
            PermissionScope(
                tenantId=tenant_id,
                userId=user_id,
                allowedAcls=("INTERNAL",),
                allowedPartitions=(tenant_id,)
            )
        )


class MockRewritePort(QueryRewriteLlmPort):
    def __init__(self, rewritten_value: str = "rewritten search query") -> None:
        self.rewritten_value = rewritten_value

    async def rewrite_query(
        self,
        query: str,
        history
    ) -> Result[str, ApplicationError]:
        return Ok(self.rewritten_value)


class MockDeps:
    def __init__(self, authz_port, rewrite_port) -> None:
        self.authz_port = authz_port
        self.rewrite_port = rewrite_port


@pytest.mark.asyncio
async def test_authz_rewrite_service_bypasses_first_turn():
    deps = MockDeps(MockAuthzPort(), MockRewritePort())
    service = AuthzRewriteService(deps)

    input_dto = RewriteInputDTO(
        query="Original query",
        tenantId="t1",
        userId="u1",
        conversationHistory=(),
        skipRewriteIfFirstTurn=True
    )

    result = await service.execute(input_dto)
    assert result.is_ok is True
    assert result.value.wasRewritten is False
    assert result.value.rewrittenQuery == "Original query"


@pytest.mark.asyncio
async def test_authz_rewrite_service_rewrites_with_history():
    deps = MockDeps(MockAuthzPort(), MockRewritePort("contextual query"))
    service = AuthzRewriteService(deps)

    input_dto = RewriteInputDTO(
        query="Follow up",
        tenantId="t1",
        userId="u1",
        conversationHistory=(ConversationTurn(role="user", content="prior context"),),
        skipRewriteIfFirstTurn=True
    )

    result = await service.execute(input_dto)
    assert result.is_ok is True
    assert result.value.wasRewritten is True
    assert result.value.rewrittenQuery == "contextual query"


@pytest.mark.asyncio
async def test_authz_rewrite_service_handles_authz_failure():
    deps = MockDeps(MockAuthzPort(should_fail=True), MockRewritePort())
    service = AuthzRewriteService(deps)

    input_dto = RewriteInputDTO(
        query="Test query",
        tenantId="t1",
        userId="u1",
        conversationHistory=()
    )

    result = await service.execute(input_dto)
    assert result.is_ok is False
    assert result.error.code == "DB_FAIL"
