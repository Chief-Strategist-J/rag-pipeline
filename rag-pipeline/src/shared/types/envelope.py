"""
Shared Generic Types, Result Container, and Response Envelopes.
"""
from typing import Generic, TypeVar, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

T = TypeVar("T")
E = TypeVar("E")


class Ok(Generic[T]):
    def __init__(self, value: T) -> None:
        self.value = value
        self.is_ok = True
        self.is_err = False


class Err(Generic[E]):
    def __init__(self, error: E) -> None:
        self.error = error
        self.is_ok = False
        self.is_err = True


Result = Union[Ok[T], Err[E]]


class ErrorDetail(BaseModel):
    field: str
    issue: str
    rule: str
    rejectedValue: Optional[Any] = None


class ResponseError(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: List[ErrorDetail] = Field(default_factory=list)


class ResponseMeta(BaseModel):
    requestId: str
    correlationId: Optional[str] = None
    causationId: Optional[str] = None
    timestamp: str
    executionTimeMs: int
    apiVersion: str = "v1"


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    statusCode: int
    data: Optional[T] = None
    error: Optional[ResponseError] = None
    meta: ResponseMeta
