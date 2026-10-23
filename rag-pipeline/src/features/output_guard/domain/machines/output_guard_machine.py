from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class OutputGuardState(str, Enum):
    INITIALIZED = "INITIALIZED"
    INSPECTING_CITATIONS = "INSPECTING_CITATIONS"
    SANITIZING_MARKDOWN = "SANITIZING_MARKDOWN"
    EVALUATING_GROUNDING = "EVALUATING_GROUNDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class OutputGuardEvent(str, Enum):
    INSPECT_CITATIONS = "INSPECT_CITATIONS"
    SANITIZE = "SANITIZE"
    EVALUATE = "EVALUATE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[OutputGuardState, Set[OutputGuardState]] = {
    OutputGuardState.INITIALIZED: {OutputGuardState.SANITIZING_MARKDOWN, OutputGuardState.INSPECTING_CITATIONS, OutputGuardState.FAILED},
    OutputGuardState.SANITIZING_MARKDOWN: {OutputGuardState.INSPECTING_CITATIONS, OutputGuardState.FAILED},
    OutputGuardState.INSPECTING_CITATIONS: {OutputGuardState.EVALUATING_GROUNDING, OutputGuardState.FAILED},
    OutputGuardState.EVALUATING_GROUNDING: {OutputGuardState.COMPLETED, OutputGuardState.FAILED},
    OutputGuardState.COMPLETED: set(),
    OutputGuardState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[OutputGuardEvent, OutputGuardState] = {
    OutputGuardEvent.INSPECT_CITATIONS: OutputGuardState.INSPECTING_CITATIONS,
    OutputGuardEvent.SANITIZE: OutputGuardState.SANITIZING_MARKDOWN,
    OutputGuardEvent.EVALUATE: OutputGuardState.EVALUATING_GROUNDING,
    OutputGuardEvent.COMPLETE: OutputGuardState.COMPLETED,
    OutputGuardEvent.FAIL: OutputGuardState.FAILED,
}


def transition_state(
    current: OutputGuardState,
    event: OutputGuardEvent
) -> Result[OutputGuardState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown output guard event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
