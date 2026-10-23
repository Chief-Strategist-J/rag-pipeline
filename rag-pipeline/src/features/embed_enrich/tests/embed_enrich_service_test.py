import pytest
from src.features.embed_enrich.service.embed_enrich_service import (
    EmbedEnrichService,
    EmbedEnrichServiceDeps,
)
from src.features.embed_enrich.infrastructure.adapters.embed_enrich_adapters import (
    BgeM3EmbeddingAdapter,
    LexicalSparseEncodingAdapter,
)
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EmbeddingRequestDTO,
)


class MockEmbedDeps:
    def __init__(self):
        self.dense_port = BgeM3EmbeddingAdapter(dimension=128)
        self.sparse_port = LexicalSparseEncodingAdapter()


@pytest.mark.asyncio
async def test_embed_enrich_hybrid_vectors_and_acl_metadata():
    deps = MockEmbedDeps()
    service = EmbedEnrichService(deps)
    chunks = [
        {
            "chunkId": "doc-ops:v1:c0000",
            "sectionTitle": "Troubleshooting",
            "content": "Verify error ERR_KUBE_500 in namespace production"
        },
        {
            "chunkId": "doc-ops:v1:c0001",
            "sectionTitle": "Remediation",
            "content": "Restart worker node if status remains NotReady"
        }
    ]
    req = EmbeddingRequestDTO(
        tenantId="tenant-corp",
        documentId="doc-ops",
        version=1,
        aclTags=["INTERNAL", "SECURITY_OPS"],
        chunks=chunks,
        correlationId="corr-embed-1"
    )

    res = await service.generate_embeddings(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.totalVectors == 2
    assert len(dto.vectors[0].denseVector) == 128
    assert len(dto.vectors[0].sparseVector.indices) > 0
    assert dto.vectors[0].aclTags == ("INTERNAL", "SECURITY_OPS")
    assert dto.vectors[0].tenantId == "tenant-corp"
