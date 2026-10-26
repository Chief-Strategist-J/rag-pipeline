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
from src.shared.constants.system import HttpHeader
from src.infra.config.settings import settings

router = APIRouter(prefix="/pipeline", tags=["Pipeline"])


class PipelineQueryRequestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    tenantId: str = Field(min_length=1)
    userId: str = Field(min_length=1)
    query: str = Field(min_length=1)
    conversationHistory: List[ConversationTurn] = Field(default_factory=list)


class DocumentIngestDTO(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    tenantId: str = Field(default="tenant-corp")
    documentId: str = Field(min_length=1)
    version: int = Field(default=1)
    sectionTitle: str = Field(default="General")
    content: str = Field(min_length=1)
    aclTags: List[str] = Field(default_factory=lambda: list(settings.DEFAULT_ALLOWED_ACLS))


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
        aclTags=list(settings.DEFAULT_ALLOWED_ACLS),
        metadata={},
        createdAt="2026-10-23T12:00:00Z"
    )
    return EndToEndPipelineOrchestrator(seeded_points=[seeded_chunk])


_orchestrator = _init_default_orchestrator()


@router.post(
    "/ingest",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse
)
async def ingest_document(request: Request, payload: Dict[str, Any]) -> JSONResponse:
    start_time = time.perf_counter()
    req_id = request.headers.get(HttpHeader.X_REQUEST_ID.value) or generate_request_id()

    try:
        dto = DocumentIngestDTO.model_validate(payload)
    except Exception as exc:
        elapsed = int((time.perf_counter() - start_time) * 1000)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ApiResponse(
                success=False,
                statusCode=400,
                data=None,
                error=ResponseError(code="VALIDATION_ERROR", message=str(exc), retryable=False),
                meta=ResponseMeta(requestId=req_id, timestamp=utc_now_iso(), executionTimeMs=elapsed, apiVersion="v1")
            ).model_dump()
        )

    blocks = [b.strip() for b in dto.content.split("\n\n") if b.strip()]
    if not blocks:
        blocks = [dto.content]

    added_chunks = []
    for idx, block in enumerate(blocks):
        cid = f"{dto.documentId}:v{dto.version}:c{idx:04d}"
        chunk = EnrichedChunkVectorDTO(
            chunkId=cid,
            documentId=dto.documentId,
            tenantId=dto.tenantId,
            version=dto.version,
            sectionTitle=dto.sectionTitle,
            content=block,
            denseVector=[0.1] * 128,
            sparseVector=SparseVectorDTO(indices=[1, 2], values=[1.0, 1.0]),
            aclTags=dto.aclTags,
            metadata={},
            createdAt=utc_now_iso()
        )
        _orchestrator.vector_search_adapter.add_point(chunk)
        added_chunks.append(cid)

    elapsed = int((time.perf_counter() - start_time) * 1000)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=ApiResponse(
            success=True,
            statusCode=200,
            data={"documentId": dto.documentId, "totalChunksAdded": len(added_chunks), "chunkIds": added_chunks},
            error=None,
            meta=ResponseMeta(requestId=req_id, timestamp=utc_now_iso(), executionTimeMs=elapsed, apiVersion="v1")
        ).model_dump()
    )


@router.post(
    "/query",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse
)
async def query_pipeline(request: Request, payload: Dict[str, Any]) -> JSONResponse:
    start_time = time.perf_counter()
    req_id = request.headers.get(HttpHeader.X_REQUEST_ID.value) or generate_request_id()
    raw_traceparent = request.headers.get(HttpHeader.TRACEPARENT.value)
    if raw_traceparent and "-" in raw_traceparent:
        parts = raw_traceparent.split("-")
        trace_id = parts[1] if len(parts) > 1 else generate_request_id()
    else:
        trace_id = generate_request_id()

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
