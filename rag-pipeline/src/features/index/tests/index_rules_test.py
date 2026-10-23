import pytest
from src.features.index.domain.rules.index_rules import (
    format_collection_name,
    is_dimension_compliant,
)
from src.features.index.domain.machines.index_machine import (
    IndexLifecycleState,
    IndexLifecycleEvent,
    transition_state,
)


def test_index_rules():
    name = format_collection_name(tenant_id="Tenant_Alpha", version="V1_Model_BGE")
    assert name == "rag-col-tenant-alpha-v1-model-bge"
    assert is_dimension_compliant(1024, 1024) is True
    assert is_dimension_compliant(512, 1024) is False


def test_index_state_machine():
    t1 = transition_state(IndexLifecycleState.INITIALIZED, IndexLifecycleEvent.VALIDATE)
    assert t1.is_ok is True
    assert t1.value == IndexLifecycleState.VALIDATING_COLLECTION

    t2 = transition_state(t1.value, IndexLifecycleEvent.UPSERT)
    assert t2.is_ok is True
    assert t2.value == IndexLifecycleState.UPSERTING_BATCH

    t3 = transition_state(t2.value, IndexLifecycleEvent.SYNC)
    assert t3.is_ok is True
    assert t3.value == IndexLifecycleState.REGISTRY_SYNCED

    t4 = transition_state(t3.value, IndexLifecycleEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == IndexLifecycleState.COMPLETED
