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
    CODE_FORMATS = (
        DocumentFormat.PYTHON,
        DocumentFormat.TYPESCRIPT,
        DocumentFormat.JAVASCRIPT,
        DocumentFormat.GO,
        DocumentFormat.RUST,
        DocumentFormat.JAVA,
        DocumentFormat.KOTLIN,
        DocumentFormat.SWIFT,
        DocumentFormat.DART,
        DocumentFormat.C,
        DocumentFormat.CPP,
        DocumentFormat.CSHARP,
        DocumentFormat.SQL,
    )
    if doc_format in CODE_FORMATS:
        return _chunk_code_by_semantic_ast(tenant_id, document_id, raw_content, doc_format)
    return _chunk_markdown_by_semantic_ast(tenant_id, document_id, raw_content, doc_format, max_chunk_chars)


def _chunk_code_by_semantic_ast(
    tenant_id: str,
    document_id: str,
    raw_content: str,
    doc_format: DocumentFormat
) -> Tuple[SemanticChunkDTO, ...]:
    import tree_sitter_languages
    from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

    lang_map = {
        DocumentFormat.PYTHON: "python",
        DocumentFormat.TYPESCRIPT: "typescript",
        DocumentFormat.JAVASCRIPT: "javascript",
        DocumentFormat.GO: "go",
        DocumentFormat.RUST: "rust",
        DocumentFormat.JAVA: "java",
        DocumentFormat.KOTLIN: "kotlin",
        DocumentFormat.C: "c",
        DocumentFormat.CPP: "cpp",
        DocumentFormat.CSHARP: "c_sharp",
        DocumentFormat.SQL: "sql",
    }
    lang_name = lang_map.get(doc_format)
    chunks: List[SemanticChunkDTO] = []

    if lang_name:
        parser = tree_sitter_languages.get_parser(lang_name)
        source_bytes = raw_content.encode("utf-8")
        tree = parser.parse(source_bytes)
        root = tree.root_node

        for idx, child in enumerate(root.children):
            node_bytes = source_bytes[child.start_byte:child.end_byte]
            content = node_bytes.decode("utf-8").strip()
            if not content:
                continue

            node_type = child.type
            if "function" in node_type or "method" in node_type:
                b_type = BlockType.FUNCTION
            elif "class" in node_type or "struct" in node_type or "interface" in node_type:
                b_type = BlockType.CLASS
            elif "statement" in node_type or "query" in node_type or doc_format == DocumentFormat.SQL:
                b_type = BlockType.SQL_STATEMENT if doc_format == DocumentFormat.SQL else BlockType.CODE
            else:
                b_type = BlockType.CODE

            cid = f"{document_id}:c{idx:04d}"
            chunks.append(
                SemanticChunkDTO(
                    chunkId=cid,
                    documentId=document_id,
                    tenantId=tenant_id,
                    sectionPath=f"{lang_name.capitalize()} > {node_type}",
                    nodeType=b_type,
                    content=content,
                    startLine=child.start_point[0] + 1,
                    endLine=child.end_point[0] + 1,
                    metadata={"format": doc_format.value, "ast_node": node_type}
                )
            )
    else:
        lc_lang = Language.SWIFT if doc_format == DocumentFormat.SWIFT else None
        if lc_lang:
            splitter = RecursiveCharacterTextSplitter.from_language(
                language=lc_lang,
                chunk_size=1000,
                chunk_overlap=50
            )
        else:
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=50,
                separators=["\nclass ", "\nvoid ", "\nFuture ", "\nWidget ", "\n\n", "\n", " "]
            )
        split_texts = splitter.split_text(raw_content)
        for idx, text in enumerate(split_texts):
            cid = f"{document_id}:c{idx:04d}"
            chunks.append(
                SemanticChunkDTO(
                    chunkId=cid,
                    documentId=document_id,
                    tenantId=tenant_id,
                    sectionPath=f"{doc_format.value.capitalize()} > Chunk",
                    nodeType=BlockType.CODE,
                    content=text.strip(),
                    startLine=1,
                    endLine=len(text.splitlines()) or 1,
                    metadata={"format": doc_format.value}
                )
            )

    if not chunks:
        chunks.append(
            SemanticChunkDTO(
                chunkId=f"{document_id}:c0000",
                documentId=document_id,
                tenantId=tenant_id,
                sectionPath=f"{doc_format.value.capitalize()} > Root",
                nodeType=BlockType.CODE,
                content=raw_content.strip(),
                startLine=1,
                endLine=len(raw_content.splitlines()) or 1,
                metadata={"format": doc_format.value}
            )
        )
    return tuple(chunks)


def _chunk_markdown_by_semantic_ast(
    tenant_id: str,
    document_id: str,
    raw_content: str,
    doc_format: DocumentFormat,
    max_chunk_chars: int
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
