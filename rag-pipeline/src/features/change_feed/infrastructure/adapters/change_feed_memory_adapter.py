from typing import Optional, Dict
from src.features.change_feed.infrastructure.ports.change_feed_ports import (
    ChangeFeedRepositoryPort,
    DownstreamInvalidationPort,
)
from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryChangeFeedRepositoryAdapter(ChangeFeedRepositoryPort):
    def __init__(self) -> None:
        self._events: Dict[str, DocumentChangeEventDTO] = {}
        self._doc_versions: Dict[str, int] = {}

    async def record_event(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[bool, ApplicationError]:
        try:
            self._events[event.eventId] = event
            key = f"{event.tenantId}:{event.documentId}"
            self._doc_versions[key] = max(self._doc_versions.get(key, 0), event.version)
            return Ok(True)
        except Exception as err:
            return Err(ApplicationError(str(err), code="RECORD_EVENT_FAILED", status_code=500))

    async def get_document_version(
        self,
        tenant_id: str,
        document_id: str
    ) -> Result[Optional[int], ApplicationError]:
        try:
            key = f"{tenant_id}:{document_id}"
            return Ok(self._doc_versions.get(key))
        except Exception as err:
            return Err(ApplicationError(str(err), code="GET_VERSION_FAILED", status_code=500))


class MemoryDownstreamInvalidationAdapter(DownstreamInvalidationPort):
    def __init__(self) -> None:
        self.purged_documents = []
        self.invalidated_caches = []
        self.dispatched_jobs = []

    async def purge_document_chunks(
        self,
        tenant_id: str,
        document_id: str,
        correlation_id: str
    ) -> Result[int, ApplicationError]:
        self.purged_documents.append((tenant_id, document_id, correlation_id))
        return Ok(12)

    async def invalidate_answer_cache(
        self,
        tenant_id: str,
        document_id: str,
        correlation_id: str
    ) -> Result[bool, ApplicationError]:
        self.invalidated_caches.append((tenant_id, document_id, correlation_id))
        return Ok(True)

    async def dispatch_ingestion_job(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[bool, ApplicationError]:
        self.dispatched_jobs.append(event)
        return Ok(True)
