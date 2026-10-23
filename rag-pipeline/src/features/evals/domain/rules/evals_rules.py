from typing import Sequence


def compute_recall_at_k(retrieved_ids: Sequence[str], golden_ids: Sequence[str], k: int) -> float:
    if not golden_ids:
        return 1.0
    top_k_retrieved = set(retrieved_ids[:k])
    golden_set = set(golden_ids)
    hits = len(top_k_retrieved.intersection(golden_set))
    return float(hits / len(golden_set))


def compute_mrr(retrieved_ids: Sequence[str], golden_ids: Sequence[str]) -> float:
    if not golden_ids:
        return 1.0
    golden_set = set(golden_ids)
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in golden_set:
            return 1.0 / rank
    return 0.0


def compute_faithfulness_overlap(answer: str, context_text: str) -> float:
    if not answer.strip():
        return 1.0
    if not context_text.strip():
        return 0.0
    import re
    answer_words = set(re.findall(r"\b\w+\b", answer.lower()))
    context_words = set(re.findall(r"\b\w+\b", context_text.lower()))
    if not answer_words:
        return 1.0
    overlap = len(answer_words.intersection(context_words))
    return float(overlap / len(answer_words))
