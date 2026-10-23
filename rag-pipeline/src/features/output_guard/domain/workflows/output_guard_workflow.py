import re
from src.features.output_guard.contracts.output_guard_types import (
    GuardInspectionRequestDTO,
    GuardInspectionResultDTO,
    GuardrailAction,
)
from src.features.output_guard.infrastructure.ports.output_guard_ports import GuardAuditPort
from src.features.output_guard.domain.rules.output_guard_rules import (
    strip_markdown_images_and_links,
    validate_citations,
)
from src.features.output_guard.domain.machines.output_guard_machine import (
    OutputGuardState,
    OutputGuardEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class OutputGuardWorkflow:
    def __init__(self, audit_port: GuardAuditPort) -> None:
        self._audit = audit_port

    async def execute(
        self,
        request: GuardInspectionRequestDTO
    ) -> Result[GuardInspectionResultDTO, ApplicationError]:
        state = OutputGuardState.INITIALIZED

        t_san = transition_state(state, OutputGuardEvent.SANITIZE)
        if not t_san.is_ok:
            return Err(t_san.error)
        state = t_san.value

        sanitized_text = request.rawAnswer
        removed_links_count = 0
        if request.stripLinks:
            sanitized_text, removed_links_count = strip_markdown_images_and_links(sanitized_text)

        t_insp = transition_state(state, OutputGuardEvent.INSPECT_CITATIONS)
        if not t_insp.is_ok:
            return Err(t_insp.error)
        state = t_insp.value

        cited_in_text = re.findall(r"\[([a-zA-Z0-9_:\-#]+)\]", sanitized_text)
        valid_citations, hallucinated_citations = validate_citations(
            cited_chunk_ids=cited_in_text,
            allowed_chunk_ids=request.providedChunkIds
        )

        for bad_id in hallucinated_citations:
            sanitized_text = sanitized_text.replace(f"[{bad_id}]", "")

        t_eval = transition_state(state, OutputGuardEvent.EVALUATE)
        if not t_eval.is_ok:
            return Err(t_eval.error)
        state = t_eval.value

        is_grounded = len(hallucinated_citations) == 0
        action = GuardrailAction.PASSED
        if not is_grounded or removed_links_count > 0:
            action = GuardrailAction.SANITIZED

        audit_res = await self._audit.record_guard_event(
            tenant_id=request.tenantId,
            correlation_id=request.correlationId,
            action=action,
            hallucinated_citations=hallucinated_citations,
            removed_links_count=removed_links_count
        )
        if not audit_res.is_ok:
            return Err(audit_res.error)

        t_comp = transition_state(state, OutputGuardEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            GuardInspectionResultDTO(
                tenantId=request.tenantId,
                sanitizedAnswer=sanitized_text.strip(),
                action=action,
                validCitationIds=tuple(valid_citations),
                hallucinatedCitationIds=tuple(hallucinated_citations),
                removedLinksCount=removed_links_count,
                isGrounded=is_grounded,
                correlationId=request.correlationId
            )
        )
