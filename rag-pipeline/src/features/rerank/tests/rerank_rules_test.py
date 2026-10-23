import pytest
from src.features.rerank.domain.rules.rerank_rules import (
    sigmoid_normalize,
    is_within_latency_budget,
)
from src.features.rerank.domain.machines.rerank_machine import (
    RerankState,
    RerankEvent,
    transition_state,
)


def test_rerank_rules():
    score = sigmoid_normalize(0.0)
    assert score == 0.5
    assert sigmoid_normalize(10.0) > 0.99
    assert is_within_latency_budget(120.0, 300.0) is True
    assert is_within_latency_budget(350.0, 300.0) is False


def test_rerank_state_machine():
    t1 = transition_state(RerankState.INITIALIZED, RerankEvent.PREPARE)
    assert t1.is_ok is True
    assert t1.value == RerankState.PREPARING_PAIRS

    t2 = transition_state(t1.value, RerankEvent.SCORE)
    assert t2.is_ok is True
    assert t2.value == RerankState.SCORING_CROSS_ENCODER

    t3 = transition_state(t2.value, RerankEvent.RANK)
    assert t3.is_ok is True
    assert t3.value == RerankState.RANKING_AND_CAPPING

    t4 = transition_state(t3.value, RerankEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == RerankState.COMPLETED
