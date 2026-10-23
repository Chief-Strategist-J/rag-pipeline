from typing import Protocol
from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedDocumentDTO,
)
from src.features.parse.infrastructure.ports.parse_ports import (
    DocumentParserPort,
    StorageArtifactPort,
)
from src.features.parse.domain.workflows.parse_workflow import ParseWorkflow
from src.shared.types.envelope import Result, Err
from src.shared.errors.exceptions import ApplicationError


class ParseServiceDeps(Protocol):
    parser_port: DocumentParserPort
    storage_port: StorageArtifactPort


class ParseService:
    def __init__(self, deps: ParseServiceDeps) -> None:
        self._workflow = ParseWorkflow(
            parser_port=deps.parser_port,
            storage_port=deps.storage_port
        )

    async def parse(
        self,
        request: ParseRequestDTO
    ) -> Result[ParsedDocumentDTO, ApplicationError]:
        try:
            return await self._workflow.execute(request)
        except Exception as err:
            return Err(ApplicationError(str(err), code="PARSE_SERVICE_ERROR", status_code=500))
