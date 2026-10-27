import pytest
from src.features.change_feed.service.change_feed_service import (
    ChangeFeedService,
    ChangeFeedServiceDeps,
)
from src.features.change_feed.infrastructure.adapters.change_feed_adapters import (
    MemoryChangeFeedRepositoryAdapter,
    MemoryDownstreamInvalidationAdapter,
)
from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeOperation,
)


class MockDeps:
    def __init__(self):
        self.repository_port = MemoryChangeFeedRepositoryAdapter()
        self.invalidation_port = MemoryDownstreamInvalidationAdapter()


@pytest.mark.asyncio
async def test_insert_change_event_processing():
    deps = MockDeps()
    service = ChangeFeedService(deps)
    evt = DocumentChangeEventDTO(
        eventId="evt-100",
        tenantId="tenant-corp",
        documentId="policy-v1",
        operation=ChangeOperation.INSERT,
        version=1,
        source="pg-cdc",
        content="Corporate travel policy v1 details",
        aclTags=["INTERNAL"],
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-abc"
    )

    res = await service.process_change_event(evt)
    assert res.is_ok is True
    dto = res.value
    assert dto.status == "COMPLETED"
    assert dto.downstreamNotified is True
    assert len(deps.invalidation_port.dispatched_jobs) == 1
    assert len(deps.invalidation_port.purged_documents) == 0


@pytest.mark.asyncio
async def test_delete_change_event_purges_chunks_and_cache():
    deps = MockDeps()
    service = ChangeFeedService(deps)
    insert_evt = DocumentChangeEventDTO(
        eventId="evt-101",
        tenantId="tenant-corp",
        documentId="policy-v1",
        operation=ChangeOperation.INSERT,
        version=1,
        source="pg-cdc",
        content="Corporate travel policy v1 details",
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-abc"
    )
    await service.process_change_event(insert_evt)

    delete_evt = DocumentChangeEventDTO(
        eventId="evt-102",
        tenantId="tenant-corp",
        documentId="policy-v1",
        operation=ChangeOperation.DELETE,
        version=2,
        source="pg-cdc",
        timestamp="2026-10-23T12:01:00Z",
        correlationId="corr-xyz"
    )
    res = await service.process_change_event(delete_evt)
    assert res.is_ok is True
    dto = res.value
    assert dto.affectedChunksCount == 12
    assert len(deps.invalidation_port.purged_documents) == 1
    assert len(deps.invalidation_port.invalidated_caches) == 1


@pytest.mark.asyncio
async def test_stale_version_event_rejection():
    deps = MockDeps()
    service = ChangeFeedService(deps)
    evt1 = DocumentChangeEventDTO(
        eventId="evt-200",
        tenantId="tenant-corp",
        documentId="policy-v2",
        operation=ChangeOperation.INSERT,
        version=5,
        source="pg-cdc",
        content="Version 5 content",
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-1"
    )
    await service.process_change_event(evt1)

    stale_evt = DocumentChangeEventDTO(
        eventId="evt-201",
        tenantId="tenant-corp",
        documentId="policy-v2",
        operation=ChangeOperation.UPDATE,
        version=4,
        source="pg-cdc",
        content="Version 4 content",
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-2"
    )
    res = await service.process_change_event(stale_evt)
    assert res.is_ok is False
    assert res.error.status_code == 409


@pytest.mark.asyncio
async def test_kafka_producer_invalidation_adapter():
    from src.features.change_feed.infrastructure.adapters.change_feed_adapters import (
        KafkaDownstreamInvalidationAdapter,
    )
    fallback = MemoryDownstreamInvalidationAdapter()
    kafka_adapter = KafkaDownstreamInvalidationAdapter(
        bootstrap_servers="localhost:9092",
        topic_ingestion="rag.ingestion.v1",
        fallback_adapter=fallback
    )

    purge_res = await kafka_adapter.purge_document_chunks("tenant-1", "doc-1", "corr-1")
    assert purge_res.is_ok is True
    assert purge_res.value == 12

    cache_res = await kafka_adapter.invalidate_answer_cache("tenant-1", "doc-1", "corr-1")
    assert cache_res.is_ok is True

    evt = DocumentChangeEventDTO(
        eventId="evt-300",
        tenantId="tenant-corp",
        documentId="policy-v3",
        operation=ChangeOperation.INSERT,
        version=1,
        source="pg-cdc",
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-3"
    )
    dispatch_res = await kafka_adapter.dispatch_ingestion_job(evt)
    assert dispatch_res.is_ok is True
    assert len(fallback.dispatched_jobs) == 1

    await kafka_adapter.close()
