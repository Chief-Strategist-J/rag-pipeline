import time
from typing import Dict, Any
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from src.features.authz_rewrite.contracts.authz_rewrite_schema import map_input_from_api
from src.features.authz_rewrite.service.authz_rewrite_service import AuthzRewriteService
from src.features.authz_rewrite.infrastructure.adapters.authz_rewrite_repository_adapter import (
    MemoryAuthzPermissionAdapter,
    VllmQueryRewriteAdapter,
)
from src.api.rest.v1.handlers.authz_rewrite_handler import create_authz_rewrite_response
from src.shared.types.envelope import ApiResponse, ResponseError, ResponseMeta
from src.shared.utils.time_utils import utc_now_iso, generate_request_id
from src.infra.config.settings import settings

router = APIRouter(prefix="/authz-rewrite", tags=["AuthzRewrite"])


class ServiceDependencies:
    def __init__(self) -> None:
        self.authz_port = MemoryAuthzPermissionAdapter()
        self.rewrite_port = VllmQueryRewriteAdapter(
            endpoint=settings.VLLM_ENDPOINT,
            model_name="Qwen/Qwen2.5-7B-Instruct"
        )


_service = AuthzRewriteService(ServiceDependencies())


@router.post(
    "/process",
    status_code=status.HTTP_200_OK,
    response_model=ApiResponse
)
async def process_authz_rewrite(request: Request, payload: Dict[str, Any]) -> JSONResponse:
    start_time = time.perf_counter()
    req_id = request.headers.get("x-request-id") or generate_request_id()

    input_result = map_input_from_api(payload)
    if not input_result.is_ok:
        elapsed = int((time.perf_counter() - start_time) * 1000)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ApiResponse(
                success=False,
                statusCode=400,
                data=None,
                error=ResponseError(
                    code=input_result.error.code,
                    message=input_result.error.message,
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

    service_result = await _service.execute(input_result.value)
    elapsed = int((time.perf_counter() - start_time) * 1000)

    if not service_result.is_ok:
        err = service_result.error
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

    response_envelope = create_authz_rewrite_response(service_result.value, req_id, elapsed)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=response_envelope.model_dump()
    )
