import pytest
from src.features.parse.contracts.parse_types import (
    ParsedBlockDTO,
    BlockType,
    DocumentFormat,
)
from src.features.parse.domain.rules.parse_rules import (
    contains_tabular_content,
    has_valid_structural_headings,
)
from src.features.parse.domain.machines.parse_machine import (
    ParseState,
    ParseEvent,
    transition_state,
)


def test_parse_rules():
    blocks = [
        ParsedBlockDTO(
            blockId="b1",
            blockType=BlockType.HEADING,
            content="Architecture Overview",
            headingLevel=1
        ),
        ParsedBlockDTO(
            blockId="b2",
            blockType=BlockType.TABLE,
            content="| Field | Type |",
            tableMatrix=[["Field", "Type"]]
        ),
    ]
    assert contains_tabular_content(blocks) is True
    assert has_valid_structural_headings(blocks) is True


def test_parse_state_transitions():
    t1 = transition_state(ParseState.INITIALIZED, ParseEvent.INGEST)
    assert t1.is_ok is True
    assert t1.value == ParseState.INGESTED

    t2 = transition_state(t1.value, ParseEvent.PARSE)
    assert t2.is_ok is True
    assert t2.value == ParseState.PARSING

    t3 = transition_state(t2.value, ParseEvent.STRUCTURE)
    assert t3.is_ok is True
    assert t3.value == ParseState.STRUCTURED

    t4 = transition_state(t3.value, ParseEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == ParseState.COMPLETED


def test_semantic_ast_chunking():
    doc = """# Data Contract

## 1. Entity Field Contract
Every column is declared before migration.

| name | type | null |
| id | uuid | no |
| amount | numeric | no |

## 2. Identifier Contract
Mandatory identifiers carry five roles.

```sql
SELECT id, tenant_id FROM orders;
```
"""
    from src.features.parse.domain.rules.parse_rules import chunk_document_by_semantic_ast
    chunks = chunk_document_by_semantic_ast(
        tenant_id="tenant-corp",
        document_id="doc-rules",
        raw_content=doc
    )
    assert len(chunks) >= 3
    table_chunk = next(c for c in chunks if c.nodeType == BlockType.TABLE)
    assert "| id | uuid | no |" in table_chunk.content
    assert "Data Contract > 1. Entity Field Contract" in table_chunk.sectionPath

    code_chunk = next(c for c in chunks if c.nodeType == BlockType.CODE)
    assert "SELECT id, tenant_id FROM orders;" in code_chunk.content
    assert "Data Contract > 2. Identifier Contract" in code_chunk.sectionPath


def test_semantic_ast_code_chunking():
    from src.features.parse.domain.rules.parse_rules import chunk_document_by_semantic_ast
    py_code = """class VectorStore:
    def search(self, query: str):
        return []

def embed_text(text: str):
    return [0.1, 0.2]
"""
    chunks = chunk_document_by_semantic_ast(
        tenant_id="tenant-corp",
        document_id="doc-py-ast",
        raw_content=py_code,
        doc_format=DocumentFormat.PYTHON
    )
    assert len(chunks) == 2
    assert chunks[0].nodeType == BlockType.CLASS
    assert chunks[1].nodeType == BlockType.FUNCTION

    go_code = """func HandleRequest() error {
    return nil
}
"""
    go_chunks = chunk_document_by_semantic_ast(
        tenant_id="tenant-corp",
        document_id="doc-go-ast",
        raw_content=go_code,
        doc_format=DocumentFormat.GO
    )
    assert len(go_chunks) >= 1
    assert go_chunks[0].nodeType == BlockType.FUNCTION

