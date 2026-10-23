import pytest
from src.features.observability.domain.rules.observability_rules import (
    sanitize_sensitive_attributes,
    validate_trace_id_format,
)
from src.features.observability.domain.machines.observability_machine import (
    ObservabilityState,
    ObservabilityEvent,
    transition_state,
)


def test_observability_rules():
    attrs = {
        "tenant.id": "tenant-corp",
        "authorization": "Bearer sec_123456",
        "apikey": "secret-xyz",
        "stage": "retrieval"
    }
    cleaned = sanitize_sensitive_attributes(attrs)
    assert cleaned["authorization"] == "[REDACTED]"
    assert cleaned["apikey"] == "[REDACTED]"
    assert cleaned["tenant.id"] == "tenant-corp"
    assert cleaned["stage"] == "retrieval"

    assert validate_trace_id_format("4bf92f3577b34da6a3ce929d0e0e4736") is True
    assert validate_trace_id_format("invalid-trace-id") is False


def test_observability_state_machine():
    t1 = transition_state(ObservabilityState.INITIALIZED, ObservabilityEvent.SANITIZE)
    assert t1.is_ok is True
    assert t1.value == ObservabilityState.SANITIZING_ATTRIBUTES

    t2 = transition_state(t1.value, ObservabilityEvent.RECORD)
    assert t2.is_ok is True
    assert t2.value == ObservabilityState.RECORDING_SPANS

    t3 = transition_state(t2.value, ObservabilityEvent.COMPLETE)
    assert t3.is_ok is True
    assert t3.value == ObservabilityState.COMPLETED
