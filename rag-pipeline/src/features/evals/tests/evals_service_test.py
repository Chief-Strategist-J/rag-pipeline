import pytest
from src.features.evals.service.evals_service import (
    EvalsService,
    EvalsServiceDeps,
)
from src.features.evals.infrastructure.adapters.evals_adapters import (
    MemoryEvalMetricStorageAdapter,
)
from src.features.evals.contracts.evals_types import (
    RetrievalEvalInputDTO,
    AnswerEvalInputDTO,
)


class MockEvalsDeps:
    def __init__(self):
        self.storage_port = MemoryEvalMetricStorageAdapter()


@pytest.mark.asyncio
async def test_evals_turn_evaluation():
    deps = MockEvalsDeps()
    service = EvalsService(deps)

    retrieval_in = RetrievalEvalInputDTO(
        tenantId="tenant-corp",
        queryId="q-101",
        retrievedChunkIds=["c1", "c2", "c3"],
        goldenRelevantChunkIds=["c2"],
        k=3,
        correlationId="corr-eval-1"
    )

    answer_in = AnswerEvalInputDTO(
        tenantId="tenant-corp",
        queryId="q-101",
        query="meal limit",
        answer="The limit is $75 per day [c2].",
        contextText="Corporate meal limit is $75 per day for all traveling employees.",
        abstained=False,
        correlationId="corr-eval-1"
    )

    res = await service.evaluate_turn(retrieval_in, answer_in)
    assert res.is_ok is True
    report = res.value
    assert report.recallAtK == 1.0
    assert report.mrr == 0.5
    assert report.faithfulnessScore > 0.5
    assert report.evaluationStatus == "PASS"
    assert len(deps.storage_port.reports) == 1
