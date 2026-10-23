from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class RetrieveState(str, Enum):
    INITIALIZED = "INITIALIZED"
    RESOLVING_FILTERS = "RESOLVING_FILTERS"
    EXECUTING_HYBRID_SEARCH = "EXECUTING_HYBRID_SEARCH"
    FUSING_RRF = "FUSING_RRF"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RetrieveEvent(str, Enum):
    RESOLVE_FILTERS = "RESOLVE_FILTERS"
    SEARCH_HYBRID = "SEARCH_HYBRID"
    FUSE_RRF = "FUSE_RRF"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[RetrieveState, Set[RetrieveState]] = {
    RetrieveState.INITIALIZED: {RetrieveState.RESOLVING_FILTERS, RetrieveState.FAILED},
    RetrieveState.RESOLVING_FILTERS: {RetrieveState.EXECUTING_HYBRID_SEARCH, RetrieveState.FAILED},
    RetrieveState.EXECUTING_HYBRID_SEARCH: {RetrieveState.FUSING_RRF, RetrieveState.FAILED},
    RetrieveState.FUSING_RRF: {RetrieveState.COMPLETED, RetrieveState.FAILED},
    RetrieveState.COMPLETED: set(),
    RetrieveState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[RetrieveEvent, RetrieveState] = {
    RetrieveEvent.RESOLVE_FILTERS: RetrieveState.RESOLVING_FILTERS,
    RetrieveEvent.SEARCH_HYBRID: RetrieveState.EXECUTING_HYBRID_SEARCH,
    RetrieveEvent.FUSE_RRF: RetrieveState.FUSING_RRF,
    RetrieveEvent.COMPLETE: RetrieveState.COMPLETED,
    RetrieveEvent.FAIL: RetrieveState.FAILED,
}


def transition_state(
    current: RetrieveState,
    event: RetrieveEvent
) -> Result[RetrieveState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown retrieve event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
