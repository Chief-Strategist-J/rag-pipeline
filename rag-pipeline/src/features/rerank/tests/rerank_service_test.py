import pytest
from src.features.rerank.service.rerank_service import (
    RerankService,
    RerankServiceDeps,
)
from src.features.rerank.infrastructure.adapters.rerank_adapters import (
    BgeRerankerAdapter,
)
from src.features.rerank.contracts.rerank_types import (
    RerankRequestDTO,
)
from src.features.retrieve.contracts.retrieve_types import ScoredChunkDTO


class MockRerankDeps:
    def __init__(self):
        self.model_port = BgeRerankerAdapter()


@pytest.mark.asyncio
async def test_cross_encoder_rerank_and_top_k_selection():
    deps = MockRerankDeps()
    service = RerankService(deps)

    candidates = [
        ScoredChunkDTO(
            chunkId=f"c{i}",
            documentId="doc1",
            tenantId="tenant-corp",
            version=1,
            sectionTitle="Policy",
            content=f"Irrelevant content number {i}",
            rrfScore=0.015
        )
        for i in range(10)
    ]
    candidates.append(
        ScoredChunkDTO(
            chunkId="c_exact",
            documentId="doc1",
            tenantId="tenant-corp",
            version=1,
            sectionTitle="Policy",
            content="Specific answer for the question query about travel expenses",
            rrfScore=0.012
        )
    )

    req = RerankRequestDTO(
        tenantId="tenant-corp",
        query="travel expenses",
        candidates=candidates,
        topK=5,
        correlationId="corr-rerank-1"
    )

    res = await service.rerank_candidates(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.totalEvaluated == 11
    assert dto.selectedCount == 5
    assert dto.rankedChunks[0].chunkId == "c_exact"
    assert dto.rankedChunks[0].relevanceScore > 0.8
    assert dto.latencyMs >= 0.0
