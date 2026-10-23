from typing import Dict, Any, Optional
import httpx

from src.shared.types.envelope import Result, Ok, Err
from src.shared.errors.exceptions import (
    ApplicationError,
    ValidationError,
    NotFoundError,
    TimeoutError
)
from src.shared.constants.system import HttpHeader


class ReusableHttpClient:
    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        default_headers: Optional[Dict[str, str]] = None
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._default_headers = default_headers or {}

    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], ApplicationError]:
        return await self._request("GET", endpoint, params=params, headers=headers)

    async def post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], ApplicationError]:
        return await self._request("POST", endpoint, json_data=json_data, headers=headers)

    async def put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], ApplicationError]:
        return await self._request("PUT", endpoint, json_data=json_data, headers=headers)

    async def delete(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], ApplicationError]:
        return await self._request("DELETE", endpoint, headers=headers)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Result[Dict[str, Any], ApplicationError]:
        url = f"{self._base_url}/{endpoint.lstrip('/')}"
        merged_headers = {**self._default_headers, **(headers or {})}

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=merged_headers
                )
                if response.status_code in (200, 201, 204):
                    if response.status_code == 204 or not response.content:
                        return Ok({})
                    return Ok(response.json())

                msg = response.text
                if response.status_code == 400:
                    return Err(ValidationError(msg))
                if response.status_code == 404:
                    return Err(NotFoundError(msg))

                return Err(ApplicationError(msg, code="HTTP_REQUEST_FAILED", status_code=response.status_code))
        except httpx.TimeoutException:
            return Err(TimeoutError("HTTP request timed out"))
        except Exception as err:
            return Err(ApplicationError(str(err), code="HTTP_CLIENT_ERROR", status_code=500))
