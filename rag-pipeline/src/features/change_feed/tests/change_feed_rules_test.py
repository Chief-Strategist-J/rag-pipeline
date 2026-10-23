import pytest
from src.features.change_feed.contracts.change_feed_types import (
    DocumentChangeEventDTO,
    ChangeOperation,
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


def test_deletion_and_acl_rules():
    delete_evt = DocumentChangeEventDTO(
        eventId="evt-1",
        tenantId="tenant-1",
        documentId="doc-1",
        operation=ChangeOperation.DELETE,
        version=2,
        source="postgres-cdc",
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-1"
    )
    insert_evt = DocumentChangeEventDTO(
        eventId="evt-2",
        tenantId="tenant-1",
        documentId="doc-1",
        operation=ChangeOperation.INSERT,
        version=1,
        source="postgres-cdc",
        content="hello world",
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-2"
    )
    assert is_deletion_or_acl_change(delete_evt) is True
    assert requires_immediate_cache_purge(delete_evt) is True
    assert is_deletion_or_acl_change(insert_evt) is False
    assert requires_immediate_cache_purge(insert_evt) is False


def test_version_sequence_rules():
    assert is_valid_version_sequence(1, 2) is True
    assert is_valid_version_sequence(2, 2) is False
    assert is_valid_version_sequence(3, 2) is False


def test_state_machine_transitions():
    t1 = transition_state(ChangeFeedState.RECEIVED, ChangeFeedEvent.VALIDATE)
    assert t1.is_ok is True
    assert t1.value == ChangeFeedState.VALIDATED

    t2 = transition_state(t1.value, ChangeFeedEvent.PROCESS)
    assert t2.is_ok is True
    assert t2.value == ChangeFeedState.PROCESSING

    t_invalid = transition_state(ChangeFeedState.RECEIVED, ChangeFeedEvent.COMPLETE)
    assert t_invalid.is_ok is False
