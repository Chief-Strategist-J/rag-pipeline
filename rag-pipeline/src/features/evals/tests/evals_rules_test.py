import pytest
from src.features.evals.domain.rules.evals_rules import (
    compute_recall_at_k,
    compute_mrr,
    compute_faithfulness_overlap,
)
from src.features.evals.domain.machines.evals_machine import (
    EvalState,
    EvalEvent,
    transition_state,
)


def test_evals_calculation_rules():
    retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    golden = ["doc2", "doc5"]
    recall = compute_recall_at_k(retrieved, golden, k=5)
    assert recall == 1.0

    recall_top1 = compute_recall_at_k(retrieved, golden, k=1)
    assert recall_top1 == 0.0

    mrr = compute_mrr(retrieved, golden)
    assert mrr == 0.5

    faithfulness = compute_faithfulness_overlap(
        answer="Tokens expire after 1 hour.",
        context_text="Corporate security policy states tokens expire after 1 hour in cluster."
    )
    assert faithfulness == 1.0


def test_evals_state_machine():
    t1 = transition_state(EvalState.INITIALIZED, EvalEvent.EVAL_RETRIEVAL)
    assert t1.is_ok is True
    assert t1.value == EvalState.EVALUATING_RETRIEVAL

    t2 = transition_state(t1.value, EvalEvent.EVAL_ANSWER)
    assert t2.is_ok is True
    assert t2.value == EvalState.EVALUATING_ANSWER

    t3 = transition_state(t2.value, EvalEvent.AGGREGATE)
    assert t3.is_ok is True
    assert t3.value == EvalState.AGGREGATING_REPORT

    t4 = transition_state(t3.value, EvalEvent.COMPLETE)
    assert t4.is_ok is True
    assert t4.value == EvalState.COMPLETED
