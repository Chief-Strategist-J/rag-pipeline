from enum import Enum
from typing import Sequence, Optional, Dict, List
from pydantic import BaseModel, Field, ConfigDict


class DocumentFormat(str, Enum):
    PDF = "PDF"
    DOCX = "DOCX"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    TEXT = "TEXT"


class BlockType(str, Enum):
    HEADING = "HEADING"
    PARAGRAPH = "PARAGRAPH"
    TABLE = "TABLE"
    CODE = "CODE"
    LIST_ITEM = "LIST_ITEM"


class ParsedBlockDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    blockId: str
    blockType: BlockType
    content: str
    headingLevel: Optional[int] = None
    sectionTitle: Optional[str] = None
    pageNumber: Optional[int] = None
    tableMatrix: Optional[List[List[str]]] = None
    metadata: Dict[str, str] = Field(default_factory=dict)


class ParseRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documentId: str
    tenantId: str
    format: DocumentFormat
    rawContent: str
    contentEncoding: str = "utf-8"
    correlationId: str


class ParsedDocumentDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")
    documentId: str
    tenantId: str
    totalBlocks: int
    hasTables: bool
    blocks: Sequence[ParsedBlockDTO]
    correlationId: str
