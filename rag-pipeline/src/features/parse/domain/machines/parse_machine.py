from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class ParseState(str, Enum):
    INITIALIZED = "INITIALIZED"
    INGESTED = "INGESTED"
    PARSING = "PARSING"
    STRUCTURED = "STRUCTURED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ParseEvent(str, Enum):
    INGEST = "INGEST"
    PARSE = "PARSE"
    STRUCTURE = "STRUCTURE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[ParseState, Set[ParseState]] = {
    ParseState.INITIALIZED: {ParseState.INGESTED, ParseState.FAILED},
    ParseState.INGESTED: {ParseState.PARSING, ParseState.FAILED},
    ParseState.PARSING: {ParseState.STRUCTURED, ParseState.FAILED},
    ParseState.STRUCTURED: {ParseState.COMPLETED, ParseState.FAILED},
    ParseState.COMPLETED: set(),
    ParseState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[ParseEvent, ParseState] = {
    ParseEvent.INGEST: ParseState.INGESTED,
    ParseEvent.PARSE: ParseState.PARSING,
    ParseEvent.STRUCTURE: ParseState.STRUCTURED,
    ParseEvent.COMPLETE: ParseState.COMPLETED,
    ParseEvent.FAIL: ParseState.FAILED,
}


def transition_state(
    current: ParseState,
    event: ParseEvent
) -> Result[ParseState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown parse event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
