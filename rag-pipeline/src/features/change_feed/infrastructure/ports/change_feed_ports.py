from typing import Protocol, Optional
from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeOperation,
)
from src.shared.types.envelope import Result
from src.shared.errors.exceptions import ApplicationError


class ChangeFeedRepositoryPort(Protocol):
    async def record_event(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[bool, ApplicationError]:
        ...

    async def get_document_version(
        self,
        tenant_id: str,
        document_id: str
    ) -> Result[Optional[int], ApplicationError]:
        ...


class DownstreamInvalidationPort(Protocol):
    async def purge_document_chunks(
        self,
        tenant_id: str,
        document_id: str,
        correlation_id: str
    ) -> Result[int, ApplicationError]:
        ...

    async def invalidate_answer_cache(
        self,
        tenant_id: str,
        document_id: str,
        correlation_id: str
    ) -> Result[bool, ApplicationError]:
        ...

    async def dispatch_ingestion_job(
        self,
        event: DocumentChangeEventDTO
    ) -> Result[bool, ApplicationError]:
        ...
