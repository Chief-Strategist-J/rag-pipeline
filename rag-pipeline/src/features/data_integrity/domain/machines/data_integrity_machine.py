from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class IntegrityState(str, Enum):
    INITIALIZED = "INITIALIZED"
    INGRESS_VALIDATION = "INGRESS_VALIDATION"
    DOMAIN_INSPECTION = "DOMAIN_INSPECTION"
    STORAGE_ENFORCEMENT = "STORAGE_ENFORCEMENT"
    COMMITTED = "COMMITTED"
    REJECTED = "REJECTED"


class IntegrityEvent(str, Enum):
    VALIDATE_INGRESS = "VALIDATE_INGRESS"
    INSPECT_DOMAIN = "INSPECT_DOMAIN"
    ENFORCE_STORAGE = "ENFORCE_STORAGE"
    COMMIT = "COMMIT"
    REJECT = "REJECT"


ALLOWED_INTEGRITY_TRANSITIONS: Dict[IntegrityState, Set[IntegrityState]] = {
    IntegrityState.INITIALIZED: {IntegrityState.INGRESS_VALIDATION, IntegrityState.REJECTED},
    IntegrityState.INGRESS_VALIDATION: {IntegrityState.DOMAIN_INSPECTION, IntegrityState.REJECTED},
    IntegrityState.DOMAIN_INSPECTION: {IntegrityState.STORAGE_ENFORCEMENT, IntegrityState.REJECTED},
    IntegrityState.STORAGE_ENFORCEMENT: {IntegrityState.COMMITTED, IntegrityState.REJECTED},
    IntegrityState.COMMITTED: set(),
    IntegrityState.REJECTED: set(),
}

EVENT_TARGET_MAP: Dict[IntegrityEvent, IntegrityState] = {
    IntegrityEvent.VALIDATE_INGRESS: IntegrityState.INGRESS_VALIDATION,
    IntegrityEvent.INSPECT_DOMAIN: IntegrityState.DOMAIN_INSPECTION,
    IntegrityEvent.ENFORCE_STORAGE: IntegrityState.STORAGE_ENFORCEMENT,
    IntegrityEvent.COMMIT: IntegrityState.COMMITTED,
    IntegrityEvent.REJECT: IntegrityState.REJECTED,
}


def transition_state(
    current: IntegrityState,
    event: IntegrityEvent
) -> Result[IntegrityState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown integrity event {event}"))

    allowed = ALLOWED_INTEGRITY_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
