from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class ObservabilityState(str, Enum):
    INITIALIZED = "INITIALIZED"
    SANITIZING_ATTRIBUTES = "SANITIZING_ATTRIBUTES"
    RECORDING_SPANS = "RECORDING_SPANS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ObservabilityEvent(str, Enum):
    SANITIZE = "SANITIZE"
    RECORD = "RECORD"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[ObservabilityState, Set[ObservabilityState]] = {
    ObservabilityState.INITIALIZED: {ObservabilityState.SANITIZING_ATTRIBUTES, ObservabilityState.FAILED},
    ObservabilityState.SANITIZING_ATTRIBUTES: {ObservabilityState.RECORDING_SPANS, ObservabilityState.FAILED},
    ObservabilityState.RECORDING_SPANS: {ObservabilityState.COMPLETED, ObservabilityState.FAILED},
    ObservabilityState.COMPLETED: set(),
    ObservabilityState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[ObservabilityEvent, ObservabilityState] = {
    ObservabilityEvent.SANITIZE: ObservabilityState.SANITIZING_ATTRIBUTES,
    ObservabilityEvent.RECORD: ObservabilityState.RECORDING_SPANS,
    ObservabilityEvent.COMPLETE: ObservabilityState.COMPLETED,
    ObservabilityEvent.FAIL: ObservabilityState.FAILED,
}


def transition_state(
    current: ObservabilityState,
    event: ObservabilityEvent
) -> Result[ObservabilityState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown observability event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
