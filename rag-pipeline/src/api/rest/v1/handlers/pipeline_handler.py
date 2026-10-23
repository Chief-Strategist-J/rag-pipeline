from typing import Dict, Any
from src.shared.types.envelope import ApiResponse, ResponseMeta
from src.shared.utils.time_utils import utc_now_iso


def create_pipeline_query_response(
    data: Dict[str, Any],
    request_id: str,
    execution_time_ms: int
) -> ApiResponse:
    return ApiResponse(
        success=True,
        statusCode=200,
        data=data,
        error=None,
        meta=ResponseMeta(
            requestId=request_id,
            timestamp=utc_now_iso(),
            executionTimeMs=execution_time_ms,
            apiVersion="v1"
        )
    )
