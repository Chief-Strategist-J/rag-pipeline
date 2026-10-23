from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class ChangeFeedState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    DOWNSTREAM_NOTIFIED = "DOWNSTREAM_NOTIFIED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ChangeFeedEvent(str, Enum):
    VALIDATE = "VALIDATE"
    PROCESS = "PROCESS"
    NOTIFY_DOWNSTREAM = "NOTIFY_DOWNSTREAM"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[ChangeFeedState, Set[ChangeFeedState]] = {
    ChangeFeedState.RECEIVED: {ChangeFeedState.VALIDATED, ChangeFeedState.FAILED},
    ChangeFeedState.VALIDATED: {ChangeFeedState.PROCESSING, ChangeFeedState.FAILED},
    ChangeFeedState.PROCESSING: {ChangeFeedState.DOWNSTREAM_NOTIFIED, ChangeFeedState.COMPLETED, ChangeFeedState.FAILED},
    ChangeFeedState.DOWNSTREAM_NOTIFIED: {ChangeFeedState.COMPLETED, ChangeFeedState.FAILED},
    ChangeFeedState.COMPLETED: set(),
    ChangeFeedState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[ChangeFeedEvent, ChangeFeedState] = {
    ChangeFeedEvent.VALIDATE: ChangeFeedState.VALIDATED,
    ChangeFeedEvent.PROCESS: ChangeFeedState.PROCESSING,
    ChangeFeedEvent.NOTIFY_DOWNSTREAM: ChangeFeedState.DOWNSTREAM_NOTIFIED,
    ChangeFeedEvent.COMPLETE: ChangeFeedState.COMPLETED,
    ChangeFeedEvent.FAIL: ChangeFeedState.FAILED,
}


def transition_state(
    current: ChangeFeedState,
    event: ChangeFeedEvent
) -> Result[ChangeFeedState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
