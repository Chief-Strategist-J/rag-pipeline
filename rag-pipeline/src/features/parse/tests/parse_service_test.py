import pytest
from src.features.parse.service.parse_service import (
    ParseService,
    ParseServiceDeps,
)
from src.features.parse.infrastructure.adapters.parse_adapters import (
    StructuralDocumentParserAdapter,
    MemoryStorageArtifactAdapter,
)
from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    DocumentFormat,
    BlockType,
)


class MockParseDeps:
    def __init__(self):
        self.parser_port = StructuralDocumentParserAdapter()
        self.storage_port = MemoryStorageArtifactAdapter()


@pytest.mark.asyncio
async def test_parse_markdown_with_tables_and_headings():
    deps = MockParseDeps()
    service = ParseService(deps)
    raw = """
# System Configuration
Here is the baseline configuration.
| Parameter | Value |
| workers | 4 |
"""
    req = ParseRequestDTO(
        documentId="doc-cfg-1",
        tenantId="tenant-corp",
        format=DocumentFormat.MARKDOWN,
        rawContent=raw,
        correlationId="corr-parse-1"
    )

    res = await service.parse(req)
    assert res.is_ok is True
    dto = res.value
    assert dto.totalBlocks >= 3
    assert dto.hasTables is True
    assert dto.blocks[0].blockType == BlockType.HEADING
    assert dto.blocks[0].content == "System Configuration"
    assert "tenant-corp:doc-cfg-1" in deps.storage_port.artifacts


@pytest.mark.asyncio
async def test_parse_plain_paragraphs():
    deps = MockParseDeps()
    service = ParseService(deps)
    raw = "Just a single paragraph without any tables."
    req = ParseRequestDTO(
        documentId="doc-plain-1",
        tenantId="tenant-corp",
        format=DocumentFormat.TEXT,
        rawContent=raw,
        correlationId="corr-parse-2"
    )
    res = await service.parse(req)
    assert res.is_ok is True
    assert res.value.hasTables is False
    assert len(res.value.blocks) == 1
    assert res.value.blocks[0].blockType == BlockType.PARAGRAPH
