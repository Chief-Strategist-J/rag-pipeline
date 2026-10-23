from typing import Sequence, Dict, List, Tuple
from collections import defaultdict


def calculate_rrf_score(rank: int, k: int = 60) -> float:
    return 1.0 / (k + rank)


def fuse_ranks_rrf(
    dense_ranked_ids: Sequence[str],
    sparse_ranked_ids: Sequence[str],
    k: int = 60
) -> List[Tuple[str, float, int | None, int | None]]:
    scores: Dict[str, float] = defaultdict(float)
    dense_ranks: Dict[str, int] = {}
    sparse_ranks: Dict[str, int] = {}

    for rank, chunk_id in enumerate(dense_ranked_ids, start=1):
        dense_ranks[chunk_id] = rank
        scores[chunk_id] += calculate_rrf_score(rank, k)

    for rank, chunk_id in enumerate(sparse_ranked_ids, start=1):
        sparse_ranks[chunk_id] = rank
        scores[chunk_id] += calculate_rrf_score(rank, k)

    sorted_results = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [
        (chunk_id, score, dense_ranks.get(chunk_id), sparse_ranks.get(chunk_id))
        for chunk_id, score in sorted_results
    ]
