import pytest
from src.features.index.service.index_service import (
    IndexService,
    IndexServiceDeps,
)
from src.features.index.infrastructure.adapters.index_adapters import (
    MemoryQdrantCollectionAdapter,
    MemoryIndexMetadataRegistryAdapter,
)
from src.features.index.contracts.index_types import (
    IndexUpsertRequestDTO,
)
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EnrichedChunkVectorDTO,
    SparseVectorDTO,
)


class MockIndexDeps:
    def __init__(self):
        self.qdrant_port = MemoryQdrantCollectionAdapter()
        self.registry_port = MemoryIndexMetadataRegistryAdapter()


@pytest.mark.asyncio
async def test_index_upsert_and_collection_versioning():
    deps = MockIndexDeps()
    service = IndexService(deps)

    points = [
        EnrichedChunkVectorDTO(
            chunkId="doc-policy:v1:c0000",
            documentId="doc-policy",
            tenantId="tenant-corp",
            version=1,
            sectionTitle="Compliance",
            content="Maintain GDPR compliant storage boundaries.",
            denseVector=[0.1] * 1024,
            sparseVector=SparseVectorDTO(indices=[101, 202], values=[1.5, 2.0]),
            aclTags=["INTERNAL", "LEGAL"],
            metadata={"origin": "handbook"},
            createdAt="2026-10-23T12:00:00Z"
        )
    ]

    req = IndexUpsertRequestDTO(
        tenantId="tenant-corp",
        collectionVersion="v1",
        vectors=points,
        correlationId="corr-idx-1"
    )

    res = await service.upsert_vectors(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.collectionName == "rag-col-tenant-corp-v1"
    assert dto.upsertedCount == 1
    assert dto.status == "ACTIVE"

    meta_res = await deps.registry_port.get_collection_meta(dto.collectionName)
    assert meta_res.is_ok is True
    meta = meta_res.value
    assert meta is not None
    assert meta.isPrimary is True
    assert meta.totalPoints == 1
