"""
Shared Standard Error Hierarchy.
"""
from typing import Optional, Dict, Any, List


class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 500,
        retryable: bool = False,
        details: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.retryable = retryable
        self.details = details or []


class ValidationError(ApplicationError):
    def __init__(self, message: str, details: Optional[List[Dict[str, Any]]] = None) -> None:
        super().__init__(
            message=message,
            code="VALIDATION_FAILED",
            status_code=400,
            retryable=False,
            details=details
        )


class UnauthorizedError(ApplicationError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            retryable=False
        )


class ForbiddenError(ApplicationError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            retryable=False
        )


class NotFoundError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="RESOURCE_NOT_FOUND",
            status_code=404,
            retryable=False
        )


class ConflictError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            retryable=False
        )


class PreconditionFailedError(ApplicationError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            code="PRECONDITION_FAILED",
            status_code=412,
            retryable=False
        )


class TimeoutError(ApplicationError):
    def __init__(self, message: str = "Operation timed out") -> None:
        super().__init__(
            message=message,
            code="TIMEOUT",
            status_code=504,
            retryable=True
        )
