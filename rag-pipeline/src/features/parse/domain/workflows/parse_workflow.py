from src.features.parse.contracts.parse_types import (
    ParseRequestDTO,
    ParsedDocumentDTO,
)
from src.features.parse.infrastructure.ports.parse_ports import (
    DocumentParserPort,
    StorageArtifactPort,
)
from src.features.parse.domain.rules.parse_rules import contains_tabular_content
from src.features.parse.domain.machines.parse_machine import (
    ParseState,
    ParseEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class ParseWorkflow:
    def __init__(
        self,
        parser_port: DocumentParserPort,
        storage_port: StorageArtifactPort
    ) -> None:
        self._parser = parser_port
        self._storage = storage_port

    async def execute(
        self,
        request: ParseRequestDTO
    ) -> Result[ParsedDocumentDTO, ApplicationError]:
        state = ParseState.INITIALIZED

        t_ingest = transition_state(state, ParseEvent.INGEST)
        if not t_ingest.is_ok:
            return Err(t_ingest.error)
        state = t_ingest.value

        t_parse = transition_state(state, ParseEvent.PARSE)
        if not t_parse.is_ok:
            return Err(t_parse.error)
        state = t_parse.value

        parse_res = await self._parser.parse_document(request)
        if not parse_res.is_ok:
            return Err(parse_res.error)

        blocks = parse_res.value
        has_tables = contains_tabular_content(list(blocks))

        t_struct = transition_state(state, ParseEvent.STRUCTURE)
        if not t_struct.is_ok:
            return Err(t_struct.error)
        state = t_struct.value

        store_res = await self._storage.persist_parsed_artifact(
            tenant_id=request.tenantId,
            document_id=request.documentId,
            blocks=blocks,
            correlation_id=request.correlationId
        )
        if not store_res.is_ok:
            return Err(store_res.error)

        t_comp = transition_state(state, ParseEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            ParsedDocumentDTO(
                documentId=request.documentId,
                tenantId=request.tenantId,
                totalBlocks=len(blocks),
                hasTables=has_tables,
                blocks=blocks,
                correlationId=request.correlationId
            )
        )
