import re
from typing import Dict


def sanitize_sensitive_attributes(attributes: Dict[str, str]) -> Dict[str, str]:
    sanitized = {}
    sensitive_keys = {"authorization", "token", "password", "secret", "bearer", "apikey"}
    for k, v in attributes.items():
        if any(sk in k.lower() for sk in sensitive_keys):
            sanitized[k] = "[REDACTED]"
        else:
            sanitized[k] = v
    return sanitized


def validate_trace_id_format(trace_id: str) -> bool:
    return bool(re.match(r"^[0-9a-fA-F]{16,32}$", trace_id))
