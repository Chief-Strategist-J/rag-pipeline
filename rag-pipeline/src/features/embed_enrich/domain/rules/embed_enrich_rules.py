from typing import Sequence, Dict, Tuple
from collections import Counter
import math


def normalize_dense_vector(vector: Sequence[float]) -> Tuple[float, ...]:
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return tuple(vector)
    return tuple(round(x / norm, 6) for x in vector)


def build_lexical_sparse_representation(text: str) -> Tuple[Tuple[int, ...], Tuple[float, ...]]:
    tokens = [t.lower() for t in text.split() if t]
    counts = Counter(tokens)
    indices = []
    values = []
    for token, count in sorted(counts.items()):
        token_hash = abs(hash(token)) % 100000
        tf = 1.0 + math.log(count)
        indices.append(token_hash)
        values.append(round(tf, 4))
    return tuple(indices), tuple(values)
