from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class RerankState(str, Enum):
    INITIALIZED = "INITIALIZED"
    PREPARING_PAIRS = "PREPARING_PAIRS"
    SCORING_CROSS_ENCODER = "SCORING_CROSS_ENCODER"
    RANKING_AND_CAPPING = "RANKING_AND_CAPPING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class RerankEvent(str, Enum):
    PREPARE = "PREPARE"
    SCORE = "SCORE"
    RANK = "RANK"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[RerankState, Set[RerankState]] = {
    RerankState.INITIALIZED: {RerankState.PREPARING_PAIRS, RerankState.FAILED},
    RerankState.PREPARING_PAIRS: {RerankState.SCORING_CROSS_ENCODER, RerankState.FAILED},
    RerankState.SCORING_CROSS_ENCODER: {RerankState.RANKING_AND_CAPPING, RerankState.FAILED},
    RerankState.RANKING_AND_CAPPING: {RerankState.COMPLETED, RerankState.FAILED},
    RerankState.COMPLETED: set(),
    RerankState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[RerankEvent, RerankState] = {
    RerankEvent.PREPARE: RerankState.PREPARING_PAIRS,
    RerankEvent.SCORE: RerankState.SCORING_CROSS_ENCODER,
    RerankEvent.RANK: RerankState.RANKING_AND_CAPPING,
    RerankEvent.COMPLETE: RerankState.COMPLETED,
    RerankEvent.FAIL: RerankState.FAILED,
}


def transition_state(
    current: RerankState,
    event: RerankEvent
) -> Result[RerankState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown rerank event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
