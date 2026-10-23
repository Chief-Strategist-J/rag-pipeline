import pytest
from src.features.chunk_dedup.domain.rules.chunk_dedup_rules import (
    generate_deterministic_chunk_id,
    compute_content_hash,
    estimate_token_count,
)
from src.features.chunk_dedup.domain.machines.chunk_dedup_machine import (
    ChunkDedupState,
    ChunkDedupEvent,
    transition_state,
)


def test_deterministic_chunk_id_and_hashing():
    chunk_id = generate_deterministic_chunk_id(
        document_id="doc-terms",
        version=2,
        offset_index=3
    )
    assert chunk_id == "doc-terms:v2:c0003"

    hash1 = compute_content_hash("The maximum transaction limit is $5000.")
    hash2 = compute_content_hash("The maximum transaction limit is $5000.")
    hash3 = compute_content_hash("Different content entirely.")
    assert hash1 == hash2
    assert hash1 != hash3
    assert estimate_token_count("The limit is 50") == 4


def test_chunk_dedup_state_machine():
    t1 = transition_state(ChunkDedupState.INITIALIZED, ChunkDedupEvent.AGGREGATE)
    assert t1.is_ok is True
    assert t1.value == ChunkDedupState.AGGREGATING

    t2 = transition_state(t1.value, ChunkDedupEvent.CHUNK)
    assert t2.is_ok is True
    assert t2.value == ChunkDedupState.CHUNKED

    t3 = transition_state(t2.value, ChunkDedupEvent.DEDUPLICATE)
    assert t3.is_ok is True
    assert t3.value == ChunkDedupState.DEDUPLICATING

    t4 = transition_state(t3.value, ChunkDedupEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == ChunkDedupState.COMPLETED
