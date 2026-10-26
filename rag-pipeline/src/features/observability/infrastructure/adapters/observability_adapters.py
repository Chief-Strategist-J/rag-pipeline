from typing import List
from src.features.observability.infrastructure.ports.observability_ports import TelemetrySpanCollectorPort
from src.features.observability.contracts.observability_types import RequestTelemetryEnvelopeDTO
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError


class MemoryTelemetryCollectorAdapter(TelemetrySpanCollectorPort):
    def __init__(self) -> None:
        self.exported_envelopes: List[RequestTelemetryEnvelopeDTO] = []

    async def export_telemetry_envelope(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[bool, ApplicationError]:
        self.exported_envelopes.append(envelope)
        return Ok(True)


class LangfuseTelemetryCollectorAdapter(TelemetrySpanCollectorPort):
    def __init__(self, public_key: str, secret_key: str, host: str) -> None:
        self._public_key = public_key
        self._secret_key = secret_key
        self._host = host
        self._client = None
        self.exported_envelopes: List[RequestTelemetryEnvelopeDTO] = []
        if public_key and secret_key:
            try:
                from langfuse import Langfuse
                self._client = Langfuse(
                    public_key=public_key,
                    secret_key=secret_key,
                    host=host
                )
            except Exception:
                self._client = None

    async def export_telemetry_envelope(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[bool, ApplicationError]:
        self.exported_envelopes.append(envelope)
        try:
            if self._client:
                trace = self._client.trace(
                    id=envelope.traceId,
                    name=f"rag-pipeline-query:{envelope.tenantId}",
                    user_id=envelope.userId,
                    input={"query": envelope.rewrittenQuery},
                    output={"answer": envelope.generatedAnswer},
                    metadata={
                        "requestId": envelope.requestId,
                        "tenantId": envelope.tenantId,
                        "retrievedChunks": envelope.retrievedChunkCount,
                        "rerankedChunks": envelope.rerankedChunkCount,
                        "promptTokens": envelope.promptTokens,
                        "generatedTokens": envelope.generatedTokens,
                        "totalDurationMs": envelope.totalDurationMs
                    }
                )
                for stage in envelope.stages:
                    trace.span(
                        name=f"stage:{stage.stageName}",
                        input={"stage": stage.stageName},
                        output={"status": stage.status, "durationMs": stage.durationMs},
                        metadata={
                            "durationMs": stage.durationMs,
                            "status": stage.status
                        }
                    )
                trace.generation(
                    name="generation-stage",
                    model="Qwen/Qwen2.5-7B-Instruct",
                    input={"promptTokens": envelope.promptTokens, "query": envelope.rewrittenQuery},
                    output={"answer": envelope.generatedAnswer, "generatedTokens": envelope.generatedTokens},
                    usage={
                        "input": envelope.promptTokens,
                        "output": envelope.generatedTokens,
                        "total": envelope.promptTokens + envelope.generatedTokens
                    }
                )
                self._client.flush()
            return Ok(True)
        except Exception as err:
            return Err(ApplicationError(str(err), code="LANGFUSE_EXPORT_FAILED", status_code=500))
