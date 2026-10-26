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
        try:
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
        except Exception as err:
            return Err(ApplicationError(str(err), code="PARSING_FAILED", status_code=500))


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
