from typing import Sequence, Dict, Any, Optional
import httpx

from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    RewriteInputDTO,
    RewrittenQueryOutputDTO,
    PermissionScope,
)
from src.shared.types.envelope import Result, Ok, Err, ApiResponse
from src.shared.errors.exceptions import (
    ApplicationError,
    ValidationError,
    NotFoundError,
    TimeoutError
)
from src.shared.constants.system import HttpHeader


class RagPipelineRestClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        api_version: str = "v1"
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._api_version = api_version

    async def process_authz_rewrite(
        self,
        input_dto: RewriteInputDTO,
        traceparent: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> Result[RewrittenQueryOutputDTO, ApplicationError]:
        url = f"{self._base_url}/api/{self._api_version}/authz-rewrite/process"
        headers: Dict[str, str] = {
            "Content-Type": "application/json",
            HttpHeader.X_TENANT_ID.value: input_dto.tenantId,
            HttpHeader.X_USER_ID.value: input_dto.userId,
        }
        if traceparent:
            headers[HttpHeader.TRACEPARENT.value] = traceparent
        if request_id:
            headers[HttpHeader.X_REQUEST_ID.value] = request_id

        payload = {
            "query": input_dto.query,
            "tenantId": input_dto.tenantId,
            "userId": input_dto.userId,
            "conversationHistory": [
                {"role": turn.role, "content": turn.content}
                for turn in input_dto.conversationHistory
            ],
            "skipRewriteIfFirstTurn": input_dto.skipRewriteIfFirstTurn
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(url, json=payload, headers=headers)
                data = response.json()

                if response.status_code == 200 and data.get("success"):
                    body = data.get("data", {})
                    scope_raw = body.get("permissionScope", {})
                    scope = PermissionScope(
                        tenantId=scope_raw.get("tenantId", input_dto.tenantId),
                        userId=scope_raw.get("userId", input_dto.userId),
                        allowedAcls=tuple(scope_raw.get("allowedAcls", ())),
                        allowedPartitions=tuple(scope_raw.get("allowedPartitions", ()))
                    )
                    output = RewrittenQueryOutputDTO(
                        originalQuery=body.get("originalQuery", input_dto.query),
                        rewrittenQuery=body.get("rewrittenQuery", input_dto.query),
                        wasRewritten=bool(body.get("wasRewritten", False)),
                        permissionScope=scope,
                        resolvedTenantId=body.get("resolvedTenantId", input_dto.tenantId)
                    )
                    return Ok(output)

                error_obj = data.get("error", {})
                code = error_obj.get("code", "HTTP_REQUEST_FAILED")
                msg = error_obj.get("message", response.text)

                if response.status_code == 400:
                    return Err(ValidationError(msg))
                if response.status_code == 404:
                    return Err(NotFoundError(msg))

                return Err(ApplicationError(msg, code=code, status_code=response.status_code))

        except httpx.TimeoutException:
            return Err(TimeoutError("Client request to pipeline service timed out"))
        except Exception as err:
            return Err(ApplicationError(str(err), code="HTTP_CLIENT_ERROR", status_code=500))
