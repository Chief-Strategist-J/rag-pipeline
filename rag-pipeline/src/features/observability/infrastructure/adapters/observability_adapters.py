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
        import base64
        self._public_key = public_key
        self._secret_key = secret_key
        self._host = host.rstrip("/")
        auth_str = f"{public_key}:{secret_key}"
        self._auth_header = f"Basic {base64.b64encode(auth_str.encode()).decode()}"
        self.exported_envelopes: List[RequestTelemetryEnvelopeDTO] = []

    async def export_telemetry_envelope(
        self,
        envelope: RequestTelemetryEnvelopeDTO
    ) -> Result[bool, ApplicationError]:
        self.exported_envelopes.append(envelope)
        if not (self._public_key and self._secret_key):
            return Ok(True)

        try:
            import httpx
            from src.shared.utils.time_utils import utc_now_iso

            now_iso = utc_now_iso()
            batch: List[dict] = [
                {
                    "id": f"evt-{envelope.traceId}-trace",
                    "type": "trace-create",
                    "timestamp": now_iso,
                    "body": {
                        "id": envelope.traceId,
                        "name": f"rag-pipeline-query:{envelope.tenantId}",
                        "userId": envelope.userId,
                        "input": {"query": envelope.rewrittenQuery},
                        "output": {"answer": envelope.generatedAnswer},
                        "metadata": {
                            "requestId": envelope.requestId,
                            "tenantId": envelope.tenantId,
                            "retrievedChunks": envelope.retrievedChunkCount,
                            "rerankedChunks": envelope.rerankedChunkCount,
                            "promptTokens": envelope.promptTokens,
                            "generatedTokens": envelope.generatedTokens,
                            "totalDurationMs": envelope.totalDurationMs
                        }
                    }
                }
            ]

            for idx, stage in enumerate(envelope.stages):
                batch.append({
                    "id": f"evt-{envelope.traceId}-span-{idx}",
                    "type": "span-create",
                    "timestamp": now_iso,
                    "body": {
                        "id": f"span-{envelope.traceId}-{idx}",
                        "traceId": envelope.traceId,
                        "name": f"stage:{stage.stageName}",
                        "input": {"stage": stage.stageName},
                        "output": {"status": stage.status, "durationMs": stage.durationMs},
                        "metadata": {
                            "durationMs": stage.durationMs,
                            "status": stage.status
                        }
                    }
                })

            batch.append({
                "id": f"evt-{envelope.traceId}-gen",
                "type": "generation-create",
                "timestamp": now_iso,
                "body": {
                    "id": f"gen-{envelope.traceId}",
                    "traceId": envelope.traceId,
                    "name": "generation-stage",
                    "model": "Qwen/Qwen2.5-7B-Instruct",
                    "input": {"promptTokens": envelope.promptTokens, "query": envelope.rewrittenQuery},
                    "output": {"answer": envelope.generatedAnswer, "generatedTokens": envelope.generatedTokens},
                    "usage": {
                        "input": envelope.promptTokens,
                        "output": envelope.generatedTokens,
                        "total": envelope.promptTokens + envelope.generatedTokens
                    }
                }
            })

            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(
                    f"{self._host}/api/public/ingestion",
                    headers={
                        "Authorization": self._auth_header,
                        "Content-Type": "application/json"
                    },
                    json={"batch": batch}
                )
                if res.status_code in (200, 201, 207):
                    return Ok(True)
                return Err(ApplicationError(f"HTTP {res.status_code}: {res.text}", code="LANGFUSE_INGESTION_ERROR", status_code=502))
        except Exception as err:
            return Err(ApplicationError(str(err), code="LANGFUSE_EXPORT_FAILED", status_code=500))
