from typing import Dict, Any, Optional
import httpx

from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import (
    ApplicationError,
    ValidationError,
    TimeoutError
)


class ReusableGraphqlClient:
    def __init__(
        self,
        endpoint_url: str,
        timeout_seconds: float = 10.0,
        default_headers: Optional[Dict[str, str]] = None
    ) -> None:
        self._endpoint_url = endpoint_url
        self._timeout_seconds = timeout_seconds
        self._default_headers = default_headers or {
            "Content-Type": "application/json"
        }

    async def execute(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], ApplicationError]:
        payload: Dict[str, Any] = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        merged_headers = {**self._default_headers, **(headers or {})}

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    self._endpoint_url,
                    json=payload,
                    headers=merged_headers
                )
                if response.status_code != 200:
                    return Err(
                        ApplicationError(
                            response.text,
                            code="GRAPHQL_HTTP_ERROR",
                            status_code=response.status_code
                        )
                    )

                body = response.json()
                errors = body.get("errors")
                if errors:
                    error_msg = "; ".join(e.get("message", "Unknown GraphQL error") for e in errors)
                    return Err(ValidationError(f"GraphQL execution errors: {error_msg}"))

                data = body.get("data", {})
                return Ok(data)

        except httpx.TimeoutException:
            return Err(TimeoutError("GraphQL request timed out"))
        except Exception as err:
            return Err(ApplicationError(str(err), code="GRAPHQL_CLIENT_ERROR", status_code=500))
