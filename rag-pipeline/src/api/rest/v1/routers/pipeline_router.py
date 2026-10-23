import time
from typing import Dict, Any, List
from pydantic import BaseModel, ConfigDict, Field
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from src.orchestrator import EndToEndPipelineOrchestrator
from src.features.authz_rewrite.contracts.authz_rewrite_types import ConversationTurn
from src.features.embed_enrich.contracts.embed_enrich_types import (
    EnrichedChunkVectorDTO,
    SparseVectorDTO,
)
from src.api.rest.v1.handlers.pipeline_handler import create_pipeline_query_response
from src.shared.types.envelope import ApiResponse, ResponseError, ResponseMeta
from src.shared.utils.time_utils import utc_now_iso, generate_request_id

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


class PipelineQueryRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenantId: str = Field(min_length=1)
    userId: str = Field(min_length=1)
    query: str = Field(min_length=1)
    conversationHistory: List[ConversationTurn] = Field(default_factory=list)


def _init_default_orchestrator() -> EndToEndPipelineOrchestrator:
    seeded_chunk = EnrichedChunkVectorDTO(
        chunkId="doc-policy:v1:c0000",
        documentId="doc-policy",
        tenantId="tenant-corp",
        version=1,
        sectionTitle="Travel Expense",
        content="According to the corporate policy, all travel expenses must be submitted within 30 days.",
        denseVector=[0.1] * 128,
        sparseVector=SparseVectorDTO(indices=[1, 2], values=[1.0, 1.0]),
        aclTags=["INTERNAL", "PUBLIC"],
        metadata={},
        createdAt="2026-10-23T12:00:00Z"
    )
    return EndToEndPipelineOrchestrator(seeded_points=[seeded_chunk])


_orchestrator = _init_default_orchestrator()


@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse
)
async def query_pipeline(request: Request, payload: Dict[str, Any]) -> JSONResponse:
    start_time = time.perf_counter()
    req_id = request.headers.get("x-request-id") or generate_request_id()
    trace_id = request.headers.get("traceparent", "4bf92f3577b34da6a3ce929d0e0e4736")

    try:
        dto = PipelineQueryRequestDTO.model_validate(payload)
    except Exception as exc:
        elapsed = int((time.perf_counter() - start_time) * 1000)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ApiResponse(
                success=False,
                statusCode=400,
                data=None,
                error=ResponseError(
                    code="VALIDATION_ERROR",
                    message=str(exc),
                    retryable=False
                ),
                meta=ResponseMeta(
                    requestId=req_id,
                    timestamp=utc_now_iso(),
                    executionTimeMs=elapsed,
                    apiVersion="v1"
                )
            ).model_dump()
        )

    res = await _orchestrator.execute_query(
        tenant_id=dto.tenantId,
        user_id=dto.userId,
        query=dto.query,
        conversation_history=tuple(dto.conversationHistory),
        request_id=req_id,
        trace_id=trace_id
    )

    elapsed = int((time.perf_counter() - start_time) * 1000)

    if not res.is_ok:
        err = res.error
        return JSONResponse(
            status_code=err.status_code,
            content=ApiResponse(
                success=False,
                statusCode=err.status_code,
                data=None,
                error=ResponseError(
                    code=err.code,
                    message=err.message,
                    retryable=err.retryable
                ),
                meta=ResponseMeta(
                    requestId=req_id,
                    timestamp=utc_now_iso(),
                    executionTimeMs=elapsed,
                    apiVersion="v1"
                )
            ).model_dump()
        )

    response_envelope = create_pipeline_query_response(res.value, req_id, elapsed)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_envelope.model_dump()
    )
