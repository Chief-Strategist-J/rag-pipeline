import pytest
from src.features.observability.service.observability_service import (
    ObservabilityService,
    ObservabilityServiceDeps,
)
from src.features.observability.infrastructure.adapters.observability_adapters import (
    MemoryTelemetryCollectorAdapter,
)
from src.features.observability.contracts.observability_types import (
    RequestTelemetryEnvelopeDTO,
    PipelineStageMetricsDTO,
)


class MockObservabilityDeps:
    def __init__(self):
        self.collector_port = MemoryTelemetryCollectorAdapter()


@pytest.mark.asyncio
async def test_observability_pipeline_telemetry_export():
    deps = MockObservabilityDeps()
    service = ObservabilityService(deps)

    stages = [
        PipelineStageMetricsDTO(
            stageName="authz_rewrite",
            durationMs=12.4,
            status="OK",
            attributes={"authorization": "Bearer token123", "user": "user1"}
        ),
        PipelineStageMetricsDTO(
            stageName="retrieve",
            durationMs=35.1,
            status="OK",
            attributes={"dense_k": "50", "sparse_k": "50"}
        ),
        PipelineStageMetricsDTO(
            stageName="rerank",
            durationMs=82.0,
            status="OK",
            attributes={"selected": "5"}
        ),
        PipelineStageMetricsDTO(
            stageName="generate",
            durationMs=450.2,
            status="OK",
            attributes={"model": "Qwen2.5"}
        )
    ]

    envelope = RequestTelemetryEnvelopeDTO(
        requestId="req-test-99",
        tenantId="tenant-corp",
        userId="user-worker",
        traceId="4bf92f3577b34da6a3ce929d0e0e4736",
        stages=stages,
        totalDurationMs=579.7,
        rewrittenQuery="meal limits during travel",
        retrievedChunkCount=50,
        rerankedChunkCount=5,
        promptTokens=256,
        generatedTokens=32,
        hasError=False,
        timestamp="2026-10-23T12:00:00Z",
        correlationId="corr-obs-1"
    )

    res = await service.record_pipeline_telemetry(envelope)
    assert res.is_ok is True
    exported = deps.collector_port.exported_envelopes[0]
    assert exported.requestId == "req-test-99"
    assert exported.stages[0].attributes["authorization"] == "[REDACTED]"
    assert exported.stages[0].attributes["user"] == "user1"
    assert exported.totalDurationMs == 579.7
