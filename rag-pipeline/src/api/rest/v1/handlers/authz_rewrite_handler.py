from src.shared.types.envelope import ApiResponse, ResponseMeta
from src.shared.utils.time_utils import utc_now_iso
from src.features.authz_rewrite.contracts.authz_rewrite_schema import map_output_to_api
from src.features.authz_rewrite.contracts.authz_rewrite_types import RewrittenQueryOutputDTO


def create_authz_rewrite_response(
    output_dto: RewrittenQueryOutputDTO,
    request_id: str,
    execution_time_ms: int
) -> ApiResponse:
    return ApiResponse(
        success=True,
        statusCode=200,
        data=map_output_to_api(output_dto),
        error=None,
        meta=ResponseMeta(
            requestId=request_id,
            timestamp=utc_now_iso(),
            executionTimeMs=execution_time_ms,
            apiVersion="v1"
        )
    )
