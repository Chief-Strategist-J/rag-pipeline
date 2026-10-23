def format_collection_name(tenant_id: str, version: str) -> str:
    sanitized_tenant = tenant_id.lower().replace("_", "-")
    sanitized_ver = version.lower().replace("_", "-")
    return f"rag-col-{sanitized_tenant}-{sanitized_ver}"


def is_dimension_compliant(vector_dim: int, expected_dim: int = 1024) -> bool:
    return vector_dim == expected_dim
