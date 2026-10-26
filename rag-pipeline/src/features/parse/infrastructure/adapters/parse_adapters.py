from typing import Sequence, Dict, List
from src.features.parse.infrastructure.ports.parse_ports import (
    DocumentParserPort,
    StorageArtifactPort,
)
from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedBlockDTO,
    BlockType,
    DocumentFormat,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class TreeSitterASTDocumentParserAdapter(DocumentParserPort):
    def __init__(self) -> None:
        pass

    async def parse_document(
        self,
        request: ParseRequestDTO
    ) -> Result[Sequence[ParsedBlockDTO], ApplicationError]:
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
        try:
            if request.format in CODE_FORMATS:
                return self._parse_code_ast(request)
            return self._parse_markdown_ast(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="PARSING_FAILED", status_code=500))

    def _parse_code_ast(
        self,
        request: ParseRequestDTO
    ) -> Result[Sequence[ParsedBlockDTO], ApplicationError]:
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
        lang_name = lang_map.get(request.format)
        blocks: List[ParsedBlockDTO] = []

        if lang_name:
            parser = tree_sitter_languages.get_parser(lang_name)
            source_bytes = request.rawContent.encode("utf-8")
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
                elif "statement" in node_type or "query" in node_type or request.format == DocumentFormat.SQL:
                    b_type = BlockType.SQL_STATEMENT if request.format == DocumentFormat.SQL else BlockType.CODE
                else:
                    b_type = BlockType.CODE

                block_id = f"{request.documentId}#ast_code_{idx:04d}"
                blocks.append(
                    ParsedBlockDTO(
                        blockId=block_id,
                        blockType=b_type,
                        content=content,
                        sectionTitle=f"{lang_name.capitalize()}:{node_type}",
                        pageNumber=1,
                        metadata={
                            "ast_type": node_type,
                            "start_point": str(child.start_point),
                            "end_point": str(child.end_point),
                            "language": lang_name,
                        }
                    )
                )
        else:
            lc_lang = Language.SWIFT if request.format == DocumentFormat.SWIFT else None
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
            chunks = splitter.split_text(request.rawContent)
            for idx, text in enumerate(chunks):
                blocks.append(
                    ParsedBlockDTO(
                        blockId=f"{request.documentId}#code_{idx:04d}",
                        blockType=BlockType.CODE,
                        content=text.strip(),
                        sectionTitle=f"{request.format.value.capitalize()}:Chunk",
                        pageNumber=1,
                        metadata={"language": request.format.value.lower()}
                    )
                )

        if not blocks:
            blocks.append(
                ParsedBlockDTO(
                    blockId=f"{request.documentId}#ast_code_0000",
                    blockType=BlockType.CODE,
                    content=request.rawContent.strip(),
                    sectionTitle=f"{request.format.value.capitalize()}:Root",
                    pageNumber=1,
                    metadata={"language": request.format.value.lower()}
                )
            )
        return Ok(tuple(blocks))

    def _parse_markdown_ast(
        self,
        request: ParseRequestDTO
    ) -> Result[Sequence[ParsedBlockDTO], ApplicationError]:
        from langchain_text_splitters import MarkdownHeaderTextSplitter
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )
        splits = markdown_splitter.split_text(request.rawContent)

        blocks: List[ParsedBlockDTO] = []
        for idx, split in enumerate(splits):
            block_id = f"{request.documentId}#ast_{idx:04d}"
            metadata = split.metadata
            title_parts = [v for k, v in metadata.items() if k.startswith("Header")]
            section_title = " > ".join(title_parts) if title_parts else "General"
            content = split.page_content.strip()

            is_table = ("|" in content and "\n|-" in content)
            is_code = content.startswith("```")
            b_type = BlockType.TABLE if is_table else (BlockType.CODE if is_code else BlockType.PARAGRAPH)

            blocks.append(
                ParsedBlockDTO(
                    blockId=block_id,
                    blockType=b_type,
                    content=content,
                    sectionTitle=section_title,
                    pageNumber=1,
                    metadata={k: str(v) for k, v in metadata.items()}
                )
            )

        if not blocks:
            blocks.append(
                ParsedBlockDTO(
                    blockId=f"{request.documentId}#ast_0000",
                    blockType=BlockType.PARAGRAPH,
                    content=request.rawContent.strip(),
                    sectionTitle="General",
                    pageNumber=1
                )
            )
        return Ok(tuple(blocks))


class StructuralDocumentParserAdapter(DocumentParserPort):
    async def parse_document(
        self,
        request: ParseRequestDTO
    ) -> Result[Sequence[ParsedBlockDTO], ApplicationError]:
        try:
            lines = [line.strip() for line in request.rawContent.split("\n") if line.strip()]
            blocks: List[ParsedBlockDTO] = []
            current_section = "Overview"

            for idx, line in enumerate(lines):
                block_id = f"{request.documentId}#b{idx}"
                if line.startswith("#"):
                    level = len(line) - len(line.lstrip("#"))
                    title = line.lstrip("#").strip()
                    current_section = title
                    blocks.append(
                        ParsedBlockDTO(
                            blockId=block_id,
                            blockType=BlockType.HEADING,
                            content=title,
                            headingLevel=level,
                            sectionTitle=title,
                            pageNumber=1
                        )
                    )
                elif "|" in line:
                    cells = [c.strip() for c in line.split("|") if c.strip()]
                    blocks.append(
                        ParsedBlockDTO(
                            blockId=block_id,
                            blockType=BlockType.TABLE,
                            content=line,
                            sectionTitle=current_section,
                            pageNumber=1,
                            tableMatrix=[cells]
                        )
                    )
                else:
                    blocks.append(
                        ParsedBlockDTO(
                            blockId=block_id,
                            blockType=BlockType.PARAGRAPH,
                            content=line,
                            sectionTitle=current_section,
                            pageNumber=1
                        )
                    )
            return Ok(tuple(blocks))
        except Exception as err:
            return Err(ApplicationError(str(err), code="PARSING_FAILED", status_code=500))


class MemoryStorageArtifactAdapter(StorageArtifactPort):
    def __init__(self) -> None:
        self.artifacts: Dict[str, Sequence[ParsedBlockDTO]] = {}

    async def persist_parsed_artifact(
        self,
        tenant_id: str,
        document_id: str,
        blocks: Sequence[ParsedBlockDTO],
        correlation_id: str
    ) -> Result[bool, ApplicationError]:
        key = f"{tenant_id}:{document_id}"
        self.artifacts[key] = blocks
        return Ok(True)
