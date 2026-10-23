from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class GenerateState(str, Enum):
    INITIALIZED = "INITIALIZED"
    BUILDING_PROMPT = "BUILDING_PROMPT"
    EXECUTING_INFERENCE = "EXECUTING_INFERENCE"
    PARSING_CITATIONS = "PARSING_CITATIONS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class GenerateEvent(str, Enum):
    BUILD_PROMPT = "BUILD_PROMPT"
    INFER = "INFER"
    PARSE = "PARSE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[GenerateState, Set[GenerateState]] = {
    GenerateState.INITIALIZED: {GenerateState.BUILDING_PROMPT, GenerateState.FAILED},
    GenerateState.BUILDING_PROMPT: {GenerateState.EXECUTING_INFERENCE, GenerateState.FAILED},
    GenerateState.EXECUTING_INFERENCE: {GenerateState.PARSING_CITATIONS, GenerateState.FAILED},
    GenerateState.PARSING_CITATIONS: {GenerateState.COMPLETED, GenerateState.FAILED},
    GenerateState.COMPLETED: set(),
    GenerateState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[GenerateEvent, GenerateState] = {
    GenerateEvent.BUILD_PROMPT: GenerateState.BUILDING_PROMPT,
    GenerateEvent.INFER: GenerateState.EXECUTING_INFERENCE,
    GenerateEvent.PARSE: GenerateState.PARSING_CITATIONS,
    GenerateEvent.COMPLETE: GenerateState.COMPLETED,
    GenerateEvent.FAIL: GenerateState.FAILED,
}


def transition_state(
    current: GenerateState,
    event: GenerateEvent
) -> Result[GenerateState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown generate event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
