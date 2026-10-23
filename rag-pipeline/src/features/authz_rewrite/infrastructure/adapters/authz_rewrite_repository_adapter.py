from typing import Sequence
import httpx
from src.features.authz_rewrite.infrastructure.ports.authz_rewrite_repository_port import (
    AuthzPermissionPort,
    QueryRewriteLlmPort,
)
from src.features.authz_rewrite.contracts.authz_rewrite_types import (
    PermissionScope,
    ConversationTurn,
)
from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import ApplicationError, TimeoutError


class MemoryAuthzPermissionAdapter(AuthzPermissionPort):
    def __init__(self, default_acls: Sequence[str] = ("INTERNAL", "PUBLIC")) -> None:
        self._default_acls = tuple(default_acls)

    async def get_permission_scope(
        self,
        tenant_id: str,
        user_id: str
    ) -> Result[PermissionScope, ApplicationError]:
        try:
            scope = PermissionScope(
                tenantId=tenant_id,
                userId=user_id,
                allowedAcls=self._default_acls,
                allowedPartitions=(tenant_id,)
            )
            return Ok(scope)
        except Exception as err:
            return Err(ApplicationError(str(err), code="AUTHZ_RESOLUTION_FAILED", status_code=500))


class VllmQueryRewriteAdapter(QueryRewriteLlmPort):
    def __init__(self, endpoint: str, model_name: str, timeout_seconds: float = 3.0) -> None:
        self._endpoint = endpoint
        self._model_name = model_name
        self._timeout_seconds = timeout_seconds

    async def rewrite_query(
        self,
        query: str,
        history: Sequence[ConversationTurn]
    ) -> Result[str, ApplicationError]:
        try:
            prompt_context = " ".join(f"{turn.role}: {turn.content}" for turn in history)
            payload = {
                "model": self._model_name,
                "messages": [
                    {
                        "role": "system",
                        "content": "Rewrite the following question into a standalone search query using the conversation context."
                    },
                    {
                        "role": "user",
                        "content": f"Context: {prompt_context}\nQuestion: {query}"
                    }
                ],
                "temperature": 0.0,
                "max_tokens": 128
            }
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                resp = await client.post(f"{self._endpoint}/chat/completions", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    choices = data.get("choices", [])
                    if choices:
                        rewritten = choices[0].get("message", {}).get("content", query).strip()
                        return Ok(rewritten)
                return Ok(query)
        except httpx.TimeoutException:
            return Err(TimeoutError("vLLM rewrite request timed out"))
        except Exception as err:
            return Err(ApplicationError(str(err), code="REWRITE_EXECUTION_FAILED", status_code=502))
