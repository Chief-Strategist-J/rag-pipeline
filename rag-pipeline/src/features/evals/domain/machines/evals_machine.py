from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class EvalState(str, Enum):
    INITIALIZED = "INITIALIZED"
    EVALUATING_RETRIEVAL = "EVALUATING_RETRIEVAL"
    EVALUATING_ANSWER = "EVALUATING_ANSWER"
    AGGREGATING_REPORT = "AGGREGATING_REPORT"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EvalEvent(str, Enum):
    EVAL_RETRIEVAL = "EVAL_RETRIEVAL"
    EVAL_ANSWER = "EVAL_ANSWER"
    AGGREGATE = "AGGREGATE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[EvalState, Set[EvalState]] = {
    EvalState.INITIALIZED: {EvalState.EVALUATING_RETRIEVAL, EvalState.FAILED},
    EvalState.EVALUATING_RETRIEVAL: {EvalState.EVALUATING_ANSWER, EvalState.FAILED},
    EvalState.EVALUATING_ANSWER: {EvalState.AGGREGATING_REPORT, EvalState.FAILED},
    EvalState.AGGREGATING_REPORT: {EvalState.COMPLETED, EvalState.FAILED},
    EvalState.COMPLETED: set(),
    EvalState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[EvalEvent, EvalState] = {
    EvalEvent.EVAL_RETRIEVAL: EvalState.EVALUATING_RETRIEVAL,
    EvalEvent.EVAL_ANSWER: EvalState.EVALUATING_ANSWER,
    EvalEvent.AGGREGATE: EvalState.AGGREGATING_REPORT,
    EvalEvent.COMPLETE: EvalState.COMPLETED,
    EvalEvent.FAIL: EvalState.FAILED,
}


def transition_state(
    current: EvalState,
    event: EvalEvent
) -> Result[EvalState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown eval event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
