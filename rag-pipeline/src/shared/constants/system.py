"""
Universal Shared Constants.
"""
from enum import Enum


class HttpHeader(str, Enum):
    TRACEPARENT = "traceparent"
    X_REQUEST_ID = "x-request-id"
    X_CORRELATION_ID = "x-correlation-id"
    X_CAUSATION_ID = "x-causation-id"
    X_IDEMPOTENCY_KEY = "x-idempotency-key"
    X_TENANT_ID = "x-tenant-id"
    X_CLIENT_ID = "x-client-id"
    X_USER_ID = "x-user-id"
    IF_MATCH = "If-Match"
    ETAG = "ETag"
    RETRY_AFTER = "Retry-After"


class ProcessingStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"


class DocumentAcl(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
