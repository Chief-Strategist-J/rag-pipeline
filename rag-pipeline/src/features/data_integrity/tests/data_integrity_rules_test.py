import pytest
from src.features.data_integrity.contracts.data_integrity_types import (
    EntityPayloadDTO,
    GateLevel,
)
from src.features.data_integrity.contracts.data_integrity_schema import (
    normalize_and_parse_entity,
)
from src.features.data_integrity.domain.rules.data_integrity_rules import (
    evaluate_domain_invariants,
)
from src.features.data_integrity.domain.machines.data_integrity_machine import (
    IntegrityState,
    IntegrityEvent,
    transition_state,
)


def test_ingress_normalization_and_rejection():
    raw_invalid = {
        "tenantId": "t-1",
        "source": "erp",
        "externalId": "   ",
        "correlationId": "c-1",
        "status": "draft",
        "amount": "not-a-number",
        "currency": "usd"
    }
    res = normalize_and_parse_entity(raw_invalid)
    assert res.is_ok is False
    violations = res.error
    assert any(v.field == "externalId" for v in violations)
    assert any(v.field == "amount" for v in violations)


def test_ingress_successful_normalization():
    raw_valid = {
        "tenantId": "t-1",
        "source": "erp",
        "externalId": "  ext-1001  ",
        "correlationId": "c-1",
        "status": "draft",
        "amount": 149.99,
        "currency": "usd"
    }
    res = normalize_and_parse_entity(raw_valid)
    assert res.is_ok is True
    entity = res.value
    assert entity.externalId == "ext-1001"
    assert entity.currency == "USD"


def test_domain_invariants_evaluation():
    entity_invalid = EntityPayloadDTO(
        tenantId="t-1",
        source="erp",
        externalId="ext-1",
        correlationId="c-1",
        status="shipped",
        amount=-10.0,
        currency="USD",
        shippedAt=None
    )
    violations = evaluate_domain_invariants(entity_invalid)
    assert len(violations) == 2
    assert any(v.field == "amount" for v in violations)
    assert any(v.field == "shippedAt" for v in violations)


def test_integrity_state_machine():
    s1 = transition_state(IntegrityState.INITIALIZED, IntegrityEvent.VALIDATE_INGRESS)
    assert s1.is_ok is True
    assert s1.value == IntegrityState.INGRESS_VALIDATION

    s2 = transition_state(s1.value, IntegrityEvent.INSPECT_DOMAIN)
    assert s2.is_ok is True
    assert s2.value == IntegrityState.DOMAIN_INSPECTION

    s3 = transition_state(s2.value, IntegrityEvent.ENFORCE_STORAGE)
    assert s3.is_ok is True
    assert s3.value == IntegrityState.STORAGE_ENFORCEMENT

    s4 = transition_state(s3.value, IntegrityEvent.COMMIT)
    assert s4.is_ok is True
    assert s4.value == IntegrityState.COMMITTED
