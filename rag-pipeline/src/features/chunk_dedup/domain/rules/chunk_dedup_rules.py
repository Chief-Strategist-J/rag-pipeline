import hashlib


def generate_deterministic_chunk_id(document_id: str, version: int, offset_index: int) -> str:
    return f"{document_id}:v{version}:c{offset_index:04d}"


def compute_content_hash(content: str) -> str:
    return hashlib.sha256(content.strip().encode("utf-8")).hexdigest()


def estimate_token_count(text: str) -> int:
    return max(1, len(text.split()))
