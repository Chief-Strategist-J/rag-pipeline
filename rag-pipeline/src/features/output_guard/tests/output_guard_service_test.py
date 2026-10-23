import pytest
from src.features.output_guard.service.output_guard_service import (
    OutputGuardService,
    OutputGuardServiceDeps,
)
from src.features.output_guard.infrastructure.adapters.output_guard_adapters import (
    MemoryGuardAuditAdapter,
)
from src.features.output_guard.contracts.output_guard_types import (
    GuardInspectionRequestDTO,
    GuardrailAction,
)


class MockOutputGuardDeps:
    def __init__(self):
        self.audit_port = MemoryGuardAuditAdapter()


@pytest.mark.asyncio
async def test_output_guard_strips_links_and_flags_hallucinated_citations():
    deps = MockOutputGuardDeps()
    service = OutputGuardService(deps)

    raw_response = (
        "Expense limits are $75 [doc1:c0001]. "
        "Visit [portal](http://exfil.internal.corp/log) and see [doc_fake:c9999]."
    )

    req = GuardInspectionRequestDTO(
        tenantId="tenant-corp",
        query="meal limit",
        rawAnswer=raw_response,
        providedChunkIds=["doc1:c0001", "doc1:c0002"],
        stripLinks=True,
        correlationId="corr-guard-1"
    )

    res = await service.inspect_and_sanitize(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.action == GuardrailAction.SANITIZED
    assert dto.isGrounded is False
    assert dto.validCitationIds == ("doc1:c0001",)
    assert dto.hallucinatedCitationIds == ("doc_fake:c9999",)
    assert dto.removedLinksCount == 1
    assert "http://exfil.internal.corp" not in dto.sanitizedAnswer
    assert "[doc_fake:c9999]" not in dto.sanitizedAnswer
    assert len(deps.audit_port.audit_records) == 1
