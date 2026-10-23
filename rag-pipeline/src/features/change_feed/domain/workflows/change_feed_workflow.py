from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeProcessingResultDTO,
    ChangeOperation,
)
from src.features.change_feed.infrastructure.ports.change_feed_ports import (
    ChangeFeedRepositoryPort,
    DownstreamInvalidationPort,
)
from src.features.change_feed.domain.rules.change_feed_rules import (
    is_deletion_or_acl_change,
    requires_immediate_cache_purge,
    is_valid_version_sequence,
)
from src.features.change_feed.domain.machines.change_feed_machine import (
    ChangeFeedState,
    ChangeFeedEvent,
    transition_state,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError, ConflictError


class ChangeFeedWorkflow:
    def __init__(
        self,
        repository_port: ChangeFeedRepositoryPort,
        invalidation_port: DownstreamInvalidationPort
    ) -> None:
        self._repo = repository_port
        self._invalidation = invalidation_port

    async def execute(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[ChangeProcessingResultDTO, ApplicationError]:
        state = ChangeFeedState.RECEIVED

        curr_ver_res = await self._repo.get_document_version(event.tenantId, event.documentId)
        if not curr_ver_res.is_ok:
            return Err(curr_ver_res.error)

        curr_ver = curr_ver_res.value
        if curr_ver is not None and not is_valid_version_sequence(curr_ver, event.version):
            return Err(ConflictError(f"Stale event version {event.version} <= existing {curr_ver}"))

        t_val = transition_state(state, ChangeFeedEvent.VALIDATE)
        if not t_val.is_ok:
            return Err(t_val.error)
        state = t_val.value

        record_res = await self._repo.record_event(event)
        if not record_res.is_ok:
            return Err(record_res.error)

        t_proc = transition_state(state, ChangeFeedEvent.PROCESS)
        if not t_proc.is_ok:
            return Err(t_proc.error)
        state = t_proc.value

        affected_chunks = 0
        if is_deletion_or_acl_change(event):
            purge_res = await self._invalidation.purge_document_chunks(
                event.tenantId, event.documentId, event.correlationId
            )
            if not purge_res.is_ok:
                return Err(purge_res.error)
            affected_chunks = purge_res.value

            if requires_immediate_cache_purge(event):
                cache_res = await self._invalidation.invalidate_answer_cache(
                    event.tenantId, event.documentId, event.correlationId
                )
                if not cache_res.is_ok:
                    return Err(cache_res.error)
        else:
            dispatch_res = await self._invalidation.dispatch_ingestion_job(event)
            if not dispatch_res.is_ok:
                return Err(dispatch_res.error)

        t_notif = transition_state(state, ChangeFeedEvent.NOTIFY_DOWNSTREAM)
        if not t_notif.is_ok:
            return Err(t_notif.error)
        state = t_notif.value

        t_comp = transition_state(state, ChangeFeedEvent.COMPLETE)
        if not t_comp.is_ok:
            return Err(t_comp.error)

        return Ok(
            ChangeProcessingResultDTO(
                eventId=event.eventId,
                tenantId=event.tenantId,
                documentId=event.documentId,
                operation=event.operation,
                status="COMPLETED",
                downstreamNotified=True,
                affectedChunksCount=affected_chunks,
                correlationId=event.correlationId
            )
        )
