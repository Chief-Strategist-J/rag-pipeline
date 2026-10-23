from enum import Enum
from typing import Set, Dict
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class RewriteState(str, Enum):
    UNPROCESSED = "UNPROCESSED"
    SCOPE_RESOLVED = "SCOPE_RESOLVED"
    BYPASSED = "BYPASSED"
    REWRITTEN = "REWRITTEN"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RewriteEvent(str, Enum):
    RESOLVE_SCOPE = "RESOLVE_SCOPE"
    BYPASS = "BYPASS"
    REWRITE = "REWRITE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


_TRANSITIONS: Dict[RewriteState, Dict[RewriteEvent, RewriteState]] = {
    RewriteState.UNPROCESSED: {
        RewriteEvent.RESOLVE_SCOPE: RewriteState.SCOPE_RESOLVED,
        RewriteEvent.FAIL: RewriteState.FAILED,
    },
    RewriteState.SCOPE_RESOLVED: {
        RewriteEvent.BYPASS: RewriteState.BYPASSED,
        RewriteEvent.REWRITE: RewriteState.REWRITTEN,
        RewriteEvent.FAIL: RewriteState.FAILED,
    },
    RewriteState.BYPASSED: {
        RewriteEvent.COMPLETE: RewriteState.COMPLETED,
        RewriteEvent.FAIL: RewriteState.FAILED,
    },
    RewriteState.REWRITTEN: {
        RewriteEvent.COMPLETE: RewriteState.COMPLETED,
        RewriteEvent.FAIL: RewriteState.FAILED,
    },
}


def transition_state(
    current_state: RewriteState,
    event: RewriteEvent
) -> Result[RewriteState, ConflictError]:
    allowed_events = _TRANSITIONS.get(current_state, {})
    next_state = allowed_events.get(event)
    if not next_state:
        return Err(
            ConflictError(
                f"Invalid transition from state {current_state.value} via event {event.value}"
            )
        )
    return Ok(next_state)
