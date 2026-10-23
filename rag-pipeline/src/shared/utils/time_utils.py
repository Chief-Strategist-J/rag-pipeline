"""
Shared Pure Deterministic Utilities.
"""
from datetime import datetime, timezone
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def generate_request_id() -> str:
    return str(uuid.uuid4())
