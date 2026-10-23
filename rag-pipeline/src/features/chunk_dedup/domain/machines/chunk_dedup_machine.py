from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class ChunkDedupState(str, Enum):
    INITIALIZED = "INITIALIZED"
    AGGREGATING = "AGGREGATING"
    CHUNKED = "CHUNKED"
    DEDUPLICATING = "DEDUPLICATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ChunkDedupEvent(str, Enum):
    AGGREGATE = "AGGREGATE"
    CHUNK = "CHUNK"
    DEDUPLICATE = "DEDUPLICATE"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[ChunkDedupState, Set[ChunkDedupState]] = {
    ChunkDedupState.INITIALIZED: {ChunkDedupState.AGGREGATING, ChunkDedupState.FAILED},
    ChunkDedupState.AGGREGATING: {ChunkDedupState.CHUNKED, ChunkDedupState.FAILED},
    ChunkDedupState.CHUNKED: {ChunkDedupState.DEDUPLICATING, ChunkDedupState.FAILED},
    ChunkDedupState.DEDUPLICATING: {ChunkDedupState.COMPLETED, ChunkDedupState.FAILED},
    ChunkDedupState.COMPLETED: set(),
    ChunkDedupState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[ChunkDedupEvent, ChunkDedupState] = {
    ChunkDedupEvent.AGGREGATE: ChunkDedupState.AGGREGATING,
    ChunkDedupEvent.CHUNK: ChunkDedupState.CHUNKED,
    ChunkDedupEvent.DEDUPLICATE: ChunkDedupState.DEDUPLICATING,
    ChunkDedupEvent.COMPLETE: ChunkDedupState.COMPLETED,
    ChunkDedupEvent.FAIL: ChunkDedupState.FAILED,
}


def transition_state(
    current: ChunkDedupState,
    event: ChunkDedupEvent
) -> Result[ChunkDedupState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown chunk_dedup event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
