import math


def sigmoid_normalize(score: float) -> float:
    return 1.0 / (1.0 + math.exp(-score))


def is_within_latency_budget(duration_ms: float, max_budget_ms: float = 300.0) -> bool:
    return duration_ms <= max_budget_ms
