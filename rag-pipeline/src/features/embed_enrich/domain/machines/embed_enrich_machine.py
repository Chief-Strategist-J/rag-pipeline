from enum import Enum
from typing import Dict, Set
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ConflictError


class EmbedEnrichState(str, Enum):
    INITIALIZED = "INITIALIZED"
    DENSE_EMBEDDING = "DENSE_EMBEDDING"
    SPARSE_ENCODING = "SPARSE_ENCODING"
    ENRICHING_METADATA = "ENRICHING_METADATA"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class EmbedEnrichEvent(str, Enum):
    EMBED_DENSE = "EMBED_DENSE"
    ENCODE_SPARSE = "ENCODE_SPARSE"
    ATTACH_METADATA = "ATTACH_METADATA"
    COMPLETE = "COMPLETE"
    FAIL = "FAIL"


ALLOWED_TRANSITIONS: Dict[EmbedEnrichState, Set[EmbedEnrichState]] = {
    EmbedEnrichState.INITIALIZED: {EmbedEnrichState.DENSE_EMBEDDING, EmbedEnrichState.FAILED},
    EmbedEnrichState.DENSE_EMBEDDING: {EmbedEnrichState.SPARSE_ENCODING, EmbedEnrichState.FAILED},
    EmbedEnrichState.SPARSE_ENCODING: {EmbedEnrichState.ENRICHING_METADATA, EmbedEnrichState.FAILED},
    EmbedEnrichState.ENRICHING_METADATA: {EmbedEnrichState.COMPLETED, EmbedEnrichState.FAILED},
    EmbedEnrichState.COMPLETED: set(),
    EmbedEnrichState.FAILED: set(),
}

EVENT_TARGET_MAP: Dict[EmbedEnrichEvent, EmbedEnrichState] = {
    EmbedEnrichEvent.EMBED_DENSE: EmbedEnrichState.DENSE_EMBEDDING,
    EmbedEnrichEvent.ENCODE_SPARSE: EmbedEnrichState.SPARSE_ENCODING,
    EmbedEnrichEvent.ATTACH_METADATA: EmbedEnrichState.ENRICHING_METADATA,
    EmbedEnrichEvent.COMPLETE: EmbedEnrichState.COMPLETED,
    EmbedEnrichEvent.FAIL: EmbedEnrichState.FAILED,
}


def transition_state(
    current: EmbedEnrichState,
    event: EmbedEnrichEvent
) -> Result[EmbedEnrichState, ConflictError]:
    target = EVENT_TARGET_MAP.get(event)
    if not target:
        return Err(ConflictError(f"Unknown embed_enrich event {event}"))

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if target not in allowed:
        return Err(
            ConflictError(
                f"Illegal state transition from {current.value} via {event.value} to {target.value}"
            )
        )
    return Ok(target)
