import pytest
from src.orchestrator import EndToEndPipelineOrchestrator
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EnrichedChunkVectorDTO,
    SparseVectorDTO,
)
from src.features.authz_rewrite.contracts.authz_rewrite_types import ConversationTurn


@pytest.mark.asyncio
async def test_full_rag_pipeline_execution():
    seeded_chunk = EnrichedChunkVectorDTO(
        chunkId="doc-policy:v1:c0000",
        documentId="doc-policy",
        tenantId="tenant-corp",
        version=1,
        sectionTitle="Travel Expense",
        content="According to the corporate policy, all travel expenses must be submitted within 30 days.",
        denseVector=[0.1] * 128,
        sparseVector=SparseVectorDTO(indices=[1, 2], values=[1.0, 1.0]),
        aclTags=["INTERNAL", "PUBLIC"],
        metadata={},
        createdAt="2026-10-23T12:00:00Z"
    )

    orchestrator = EndToEndPipelineOrchestrator(seeded_points=[seeded_chunk])

    res = await orchestrator.execute_query(
        tenant_id="tenant-corp",
        user_id="user-ops",
        query="What is the travel expense submission deadline?",
        conversation_history=(),
        request_id="req-e2e-001",
        trace_id="4bf92f3577b34da6a3ce929d0e0e4736"
    )

    assert res.is_ok is True
    data = res.value
    assert data["tenantId"] == "tenant-corp"
    assert "30 days" in data["answer"]
    assert "doc-policy:v1:c0000" in data["citedChunkIds"]
    assert data["abstained"] is False
    assert data["isGrounded"] is True
    assert data["totalDurationMs"] > 0.0

    # Verify telemetry trace was exported
    assert len(orchestrator.obs_collector.exported_envelopes) == 1
    telemetry = orchestrator.obs_collector.exported_envelopes[0]
    assert telemetry.traceId == "4bf92f3577b34da6a3ce929d0e0e4736"
    assert len(telemetry.stages) == 7
