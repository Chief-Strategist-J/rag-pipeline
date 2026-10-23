import pytest
from src.features.generate.service.generate_service import (
    GenerateService,
    GenerateServiceDeps,
)
from src.features.generate.infrastructure.adapters.generate_adapters import (
    VllmQwenGeneratorAdapter,
)
from src.features.generate.contracts.generate_types import (
    GenerationRequestDTO,
)
from src.features.rerank.contracts.rerank_types import RerankedChunkDTO


class MockGenerateDeps:
    def __init__(self):
        self.llm_port = VllmQwenGeneratorAdapter()


@pytest.mark.asyncio
async def test_generation_with_citations():
    deps = MockGenerateDeps()
    service = GenerateService(deps)

    chunks = [
        RerankedChunkDTO(
            chunkId="doc-policy:v1:c0000",
            documentId="doc-policy",
            tenantId="tenant-corp",
            version=1,
            sectionTitle="Travel Expense",
            content="All travel expenses must be submitted within 30 days.",
            relevanceScore=0.98,
            originalRank=1,
            rerankedRank=1
        )
    ]
    req = GenerationRequestDTO(
        tenantId="tenant-corp",
        query="What is the submission window for travel expenses?",
        contextChunks=chunks,
        correlationId="corr-gen-1"
    )

    res = await service.generate_answer(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.abstained is False
    assert "doc-policy:v1:c0000" in dto.citedChunkIds
    assert dto.outputTokens > 0


@pytest.mark.asyncio
async def test_generation_abstain_when_context_empty():
    deps = MockGenerateDeps()
    service = GenerateService(deps)

    req = GenerationRequestDTO(
        tenantId="tenant-corp",
        query="What is the submission window?",
        contextChunks=(),
        correlationId="corr-gen-2"
    )
    res = await service.generate_answer(req)
    assert res.is_ok is True
    assert res.value.abstained is True
    assert len(res.value.citedChunkIds) == 0
