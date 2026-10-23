from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class IndexLifecycleState(str, Enum):
    INITIALIZED = "INITIALIZED"
    VALIDATING_COLLECTION = "VALIDATING_COLLECTION"
    UPSERTING_BATCH = "UPSERTING_BATCH"
    REGISTRY_SYNCED = "REGISTRY_SYNCED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class IndexLifecycleEvent(str, Enum):
    VALIDATE = "VALIDATE"
    UPSERT = "UPSERT"
    SYNC = "SYNC"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[IndexLifecycleState, Set[IndexLifecycleState]] = {
    IndexLifecycleState.INITIALIZED: {IndexLifecycleState.VALIDATING_COLLECTION, IndexLifecycleState.FAILED},
    IndexLifecycleState.VALIDATING_COLLECTION: {IndexLifecycleState.UPSERTING_BATCH, IndexLifecycleState.FAILED},
    IndexLifecycleState.UPSERTING_BATCH: {IndexLifecycleState.REGISTRY_SYNCED, IndexLifecycleState.FAILED},
    IndexLifecycleState.REGISTRY_SYNCED: {IndexLifecycleState.COMPLETED, IndexLifecycleState.FAILED},
    IndexLifecycleState.COMPLETED: set(),
    IndexLifecycleState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[IndexLifecycleEvent, IndexLifecycleState] = {
    IndexLifecycleEvent.VALIDATE: IndexLifecycleState.VALIDATING_COLLECTION,
    IndexLifecycleEvent.UPSERT: IndexLifecycleState.UPSERTING_BATCH,
    IndexLifecycleEvent.SYNC: IndexLifecycleState.REGISTRY_SYNCED,
    IndexLifecycleEvent.COMPLETE: IndexLifecycleState.COMPLETED,
    IndexLifecycleEvent.FAIL: IndexLifecycleState.FAILED,
}


def transition_state(
    current: IndexLifecycleState,
    event: IndexLifecycleEvent
) -> Result[IndexLifecycleState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown index lifecycle event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
