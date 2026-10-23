from typing import Protocol, Sequence
from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedBlockDTO,
)
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class DocumentParserPort(Protocol):
    async def parse_document(
        self,
        request: ParseRequestDTO
    ) -> Result[Sequence[ParsedBlockDTO], ApplicationError]:
        ...


class StorageArtifactPort(Protocol):
    async def persist_parsed_artifact(
        self,
        tenant_id: str,
        document_id: str,
        blocks: Sequence[ParsedBlockDTO],
        correlation_id: str
    ) -> Result[bool, ApplicationError]:
        ...
