import pytest
from src.features.retrieve.service.retrieve_service import (
    RetrieveService,
    RetrieveServiceDeps,
)
from src.features.retrieve.infrastructure.adapters.retrieve_adapters import (
    MemoryHybridVectorSearchAdapter,
)
from src.features.retrieve.contracts.retrieve_types import (
    RetrieveRequestDTO,
)
from src.features.authz_rewrite.contracts.authz_rewrite_types import PermissionScope
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EnrichedChunkVectorDTO,
    SparseVectorDTO,
)


class MockRetrieveDeps:
    def __init__(self, seeded_points=()):
        self.search_port = MemoryHybridVectorSearchAdapter(seeded_points)


@pytest.mark.asyncio
async def test_hybrid_retrieve_with_acl_filtering_and_rrf():
    chunk1 = EnrichedChunkVectorDTO(
        chunkId="c1",
        documentId="doc1",
        tenantId="tenant-corp",
        version=1,
        sectionTitle="Finance",
        content="Corporate travel meal limit is $75 per day.",
        denseVector=[0.1] * 128,
        sparseVector=SparseVectorDTO(indices=[1], values=[1.0]),
        aclTags=["INTERNAL"],
        metadata={},
        createdAt="2026-10-23T12:00:00Z"
    )
    chunk2_confidential = EnrichedChunkVectorDTO(
        chunkId="c2",
        documentId="doc2",
        tenantId="tenant-corp",
        version=1,
        sectionTitle="HR",
        content="Confidential executive compensation data.",
        denseVector=[0.2] * 128,
        sparseVector=SparseVectorDTO(indices=[2], values=[1.0]),
        aclTags=["EXECUTIVE_ONLY"],
        metadata={},
        createdAt="2026-10-23T12:00:00Z"
    )

    deps = MockRetrieveDeps([chunk1, chunk2_confidential])
    service = RetrieveService(deps)

    req = RetrieveRequestDTO(
        tenantId="tenant-corp",
        query="meal limit per day",
        denseVector=[0.1] * 128,
        sparseIndices=[1],
        sparseValues=[1.0],
        permissionScope=PermissionScope(
            tenantId="tenant-corp",
            userId="user-worker",
            allowedAcls=["INTERNAL", "PUBLIC"],
            allowedPartitions=["tenant-corp"]
        ),
        candidatePoolSize=10,
        correlationId="corr-ret-1"
    )

    res = await service.retrieve_candidates(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.totalRetrieved == 1
    assert dto.candidates[0].chunkId == "c1"
    assert dto.candidates[0].rrfScore > 0.0
