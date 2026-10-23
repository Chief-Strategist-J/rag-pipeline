import pytest
from src.features.chunk_dedup.service.chunk_dedup_service import (
    ChunkDedupService,
    ChunkDedupServiceDeps,
)
from src.features.chunk_dedup.infrastructure.adapters.chunk_dedup_adapters import (
    MemoryFingerprintStorageAdapter,
)
from src.features.chunk_dedup.contracts.chunk_dedup_types import (
    ChunkingRequestDTO,
)
from src.features.parse.contracts.parse_types import (
    ParsedBlockDTO,
    BlockType,
)


class MockChunkDedupDeps:
    def __init__(self):
        self.fingerprint_port = MemoryFingerprintStorageAdapter()


@pytest.mark.asyncio
async def test_structure_aware_chunking_with_deterministic_ids():
    deps = MockChunkDedupDeps()
    service = ChunkDedupService(deps)
    blocks = [
        ParsedBlockDTO(
            blockId="b0",
            blockType=BlockType.HEADING,
            content="Security Governance",
            headingLevel=1,
            sectionTitle="Security Governance"
        ),
        ParsedBlockDTO(
            blockId="b1",
            blockType=BlockType.PARAGRAPH,
            content="All access tokens must rotate within 24 hours.",
            sectionTitle="Security Governance"
        ),
        ParsedBlockDTO(
            blockId="b2",
            blockType=BlockType.TABLE,
            content="| Role | Permission |",
            sectionTitle="Security Governance"
        )
    ]
    req = ChunkingRequestDTO(
        documentId="sec-policy",
        tenantId="tenant-corp",
        version=1,
        blocks=blocks,
        correlationId="corr-chunk-1"
    )

    res = await service.process_chunks(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.totalChunks == 3
    assert dto.chunks[0].chunkId == "sec-policy:v1:c0000"
    assert dto.chunks[0].sectionTitle == "Security Governance"
    assert dto.chunks[1].chunkId == "sec-policy:v1:c0001"
    assert dto.chunks[2].chunkId == "sec-policy:v1:c0002"
    assert dto.deduplicatedCount == 0


@pytest.mark.asyncio
async def test_near_duplicate_version_preference():
    deps = MockChunkDedupDeps()
    service = ChunkDedupService(deps)
    duplicate_content = "Constant static clause across multiple document versions."

    newer_blocks = [
        ParsedBlockDTO(
            blockId="nb1",
            blockType=BlockType.PARAGRAPH,
            content=duplicate_content,
            sectionTitle="Terms"
        )
    ]
    req_v2 = ChunkingRequestDTO(
        documentId="terms-v2",
        tenantId="tenant-corp",
        version=2,
        blocks=newer_blocks,
        correlationId="corr-v2"
    )
    res_v2 = await service.process_chunks(req_v2)
    assert res_v2.is_ok is True
    assert res_v2.value.chunks[0].isCurrent is True

    older_blocks = [
        ParsedBlockDTO(
            blockId="ob1",
            blockType=BlockType.PARAGRAPH,
            content=duplicate_content,
            sectionTitle="Terms"
        )
    ]
    req_v1 = ChunkingRequestDTO(
        documentId="terms-v1",
        tenantId="tenant-corp",
        version=1,
        blocks=older_blocks,
        correlationId="corr-v1"
    )
    res_v1 = await service.process_chunks(req_v1)
    assert res_v1.is_ok is True
    assert res_v1.value.deduplicatedCount == 1
    assert res_v1.value.chunks[0].isCurrent is False
