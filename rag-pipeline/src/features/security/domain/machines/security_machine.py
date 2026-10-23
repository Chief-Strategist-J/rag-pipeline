from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class SecurityState(str, Enum):
    INITIALIZED = "INITIALIZED"
    SCANNING_INJECTIONS = "SCANNING_INJECTIONS"
    NEUTRALIZING_PAYLOAD = "NEUTRALIZING_PAYLOAD"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SecurityEvent(str, Enum):
    SCAN = "SCAN"
    NEUTRALIZE = "NEUTRALIZE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[SecurityState, Set[SecurityState]] = {
    SecurityState.INITIALIZED: {SecurityState.SCANNING_INJECTIONS, SecurityState.FAILED},
    SecurityState.SCANNING_INJECTIONS: {SecurityState.NEUTRALIZING_PAYLOAD, SecurityState.FAILED},
    SecurityState.NEUTRALIZING_PAYLOAD: {SecurityState.COMPLETED, SecurityState.FAILED},
    SecurityState.COMPLETED: set(),
    SecurityState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[SecurityEvent, SecurityState] = {
    SecurityEvent.SCAN: SecurityState.SCANNING_INJECTIONS,
    SecurityEvent.NEUTRALIZE: SecurityState.NEUTRALIZING_PAYLOAD,
    SecurityEvent.COMPLETE: SecurityState.COMPLETED,
    SecurityEvent.FAIL: SecurityState.FAILED,
}


def transition_state(
    current: SecurityState,
    event: SecurityEvent
) -> Result[SecurityState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown security event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
