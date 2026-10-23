import pytest
from src.features.retrieve.domain.rules.retrieve_rules import (
    calculate_rrf_score,
    fuse_ranks_rrf,
)
from src.features.retrieve.domain.machines.retrieve_machine import (
    RetrieveState,
    RetrieveEvent,
    transition_state,
)


def test_rrf_scoring_and_fusion():
    score1 = calculate_rrf_score(rank=1, k=60)
    score2 = calculate_rrf_score(rank=2, k=60)
    assert score1 > score2
    assert round(score1, 5) == round(1.0 / 61.0, 5)

    dense_ranks = ["docA", "docB", "docC"]
    sparse_ranks = ["docB", "docA", "docD"]
    fused = fuse_ranks_rrf(dense_ranks, sparse_ranks, k=60)

    # docA has rank 1 & 2: (1/61 + 1/62) = 0.0325
    # docB has rank 2 & 1: (1/62 + 1/61) = 0.0325
    assert len(fused) == 4
    top_ids = [f[0] for f in fused[:2]]
    assert "docA" in top_ids
    assert "docB" in top_ids


def test_retrieve_state_machine():
    t1 = transition_state(RetrieveState.INITIALIZED, RetrieveEvent.RESOLVE_FILTERS)
    assert t1.is_ok is True
    assert t1.value == RetrieveState.RESOLVING_FILTERS

    t2 = transition_state(t1.value, RetrieveEvent.SEARCH_HYBRID)
    assert t2.is_ok is True
    assert t2.value == RetrieveState.EXECUTING_HYBRID_SEARCH

    t3 = transition_state(t2.value, RetrieveEvent.FUSE_RRF)
    assert t3.is_ok is True
    assert t3.value == RetrieveState.FUSING_RRF

    t4 = transition_state(t3.value, RetrieveEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == RetrieveState.COMPLETED
