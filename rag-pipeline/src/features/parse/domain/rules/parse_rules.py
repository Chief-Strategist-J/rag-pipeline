from typing import List, Tuple
from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedBlockDTO,
    BlockType,
    SemanticChunkDTO,
    DocumentFormat,
)


def contains_tabular_content(blocks: list[ParsedBlockDTO]) -> bool:
    return any(b.blockType == BlockType.TABLE for b in blocks)


def has_valid_structural_headings(blocks: list[ParsedBlockDTO]) -> bool:
    return any(b.blockType == BlockType.HEADING for b in blocks)


def chunk_document_by_semantic_ast(
    tenant_id: str,
    document_id: str,
    raw_content: str,
    doc_format: DocumentFormat = DocumentFormat.MARKDOWN,
    max_chunk_chars: int = 1500
) -> Tuple[SemanticChunkDTO, ...]:
    lines = raw_content.splitlines()
    chunks: List[SemanticChunkDTO] = []
    
    current_headers: List[str] = []
    current_content: List[str] = []
    start_line = 1
    current_node_type = BlockType.PARAGRAPH
    in_code_block = False
    in_table = False

    def _flush_chunk(end_line: int, node_type: BlockType):
        text = "\n".join(current_content).strip()
        if text:
            section_path = " > ".join(current_headers) if current_headers else "Root"
            chunk_idx = len(chunks)
            cid = f"{document_id}:c{chunk_idx:04d}"
            chunks.append(
                SemanticChunkDTO(
                    chunkId=cid,
                    documentId=document_id,
                    tenantId=tenant_id,
                    sectionPath=section_path,
                    nodeType=node_type,
                    content=text,
                    startLine=start_line,
                    endLine=end_line,
                    metadata={"format": doc_format.value}
                )
            )
        current_content.clear()

    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                current_content.append(line)
                in_code_block = False
                _flush_chunk(idx, BlockType.CODE)
                start_line = idx + 1
                continue
            else:
                if current_content:
                    _flush_chunk(idx - 1, current_node_type)
                in_code_block = True
                current_node_type = BlockType.CODE
                start_line = idx
                current_content.append(line)
                continue

        if in_code_block:
            current_content.append(line)
            continue

        if stripped.startswith("#"):
            if current_content:
                _flush_chunk(idx - 1, current_node_type)
            header_level = len(stripped) - len(stripped.lstrip("#"))
            header_title = stripped.lstrip("#").strip()
            if header_level <= len(current_headers):
                current_headers = current_headers[:header_level - 1]
            current_headers.append(header_title)
            start_line = idx
            current_node_type = BlockType.HEADING
            current_content.append(line)
            continue

        if "|" in stripped and (stripped.startswith("|") or stripped.endswith("|")):
            if not in_table:
                if current_content:
                    _flush_chunk(idx - 1, current_node_type)
                in_table = True
                start_line = idx
                current_node_type = BlockType.TABLE
            current_content.append(line)
            continue
        elif in_table:
            in_table = False
            _flush_chunk(idx - 1, BlockType.TABLE)
            start_line = idx

        if not stripped:
            if current_content and len("\n".join(current_content)) >= max_chunk_chars:
                _flush_chunk(idx, current_node_type)
                start_line = idx + 1
            elif current_content:
                current_content.append(line)
            continue

        if not current_content:
            start_line = idx
            current_node_type = BlockType.PARAGRAPH

        current_content.append(line)

    if current_content:
        _flush_chunk(len(lines), current_node_type)

    return tuple(chunks)
