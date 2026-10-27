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


class KafkaDownstreamInvalidationAdapter(DownstreamInvalidationPort):
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic_ingestion: str = "rag.ingestion.v1",
        enabled: bool = True,
        fallback_adapter: Optional[DownstreamInvalidationPort] = None
    ) -> None:
        self._bootstrap_servers = bootstrap_servers
        self._topic_ingestion = topic_ingestion
        self._enabled = enabled
        self._fallback = fallback_adapter or MemoryDownstreamInvalidationAdapter()
        self._producer = None

    async def _get_producer(self):
        if not self._enabled:
            return None
        if self._producer is None:
            try:
                from aiokafka import AIOKafkaProducer
                self._producer = AIOKafkaProducer(
                    bootstrap_servers=self._bootstrap_servers,
                    request_timeout_ms=5000
                )
                await self._producer.start()
            except Exception:
                self._producer = None
        return self._producer

    async def purge_document_chunks(
        self,
        tenant_id: str,
        document_id: str,
        correlation_id: str
    ) -> Result[int, ApplicationError]:
        return await self._fallback.purge_document_chunks(tenant_id, document_id, correlation_id)

    async def invalidate_answer_cache(
        self,
        tenant_id: str,
        document_id: str,
        correlation_id: str
    ) -> Result[bool, ApplicationError]:
        return await self._fallback.invalidate_answer_cache(tenant_id, document_id, correlation_id)

    async def dispatch_ingestion_job(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[bool, ApplicationError]:
        try:
            if self._enabled:
                producer = await self._get_producer()
                if producer is not None:
                    payload = event.model_dump_json().encode("utf-8")
                    key = f"{event.tenantId}:{event.documentId}".encode("utf-8")
                    await producer.send_and_wait(self._topic_ingestion, value=payload, key=key)
            return await self._fallback.dispatch_ingestion_job(event)
        except Exception as err:
            fallback_res = await self._fallback.dispatch_ingestion_job(event)
            if fallback_res.is_ok:
                return fallback_res
            return Err(ApplicationError(str(err), code="KAFKA_DISPATCH_INGESTION_FAILED", status_code=500))

    async def close(self) -> None:
        if self._producer is not None:
            try:
                await self._producer.stop()
            except Exception:
                pass
            finally:
                self._producer = None

