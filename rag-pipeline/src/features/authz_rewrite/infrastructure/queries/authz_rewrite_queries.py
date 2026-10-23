FLOW_SELECT_PERMISSION_SCOPE_BY_TENANT_USER = """
SELECT
    tenant_id,
    user_id,
    allowed_acls,
    allowed_partitions
FROM permission_scopes
WHERE tenant_id = :tenant_id AND user_id = :user_id
LIMIT 1;
"""

FLOW_INSERT_QUERY_REWRITE_AUDIT_LOG = """
INSERT INTO query_rewrite_audit_logs (
    id,
    tenant_id,
    user_id,
    request_id,
    correlation_id,
    original_query,
    rewritten_query,
    was_rewritten,
    latency_ms,
    created_at
) VALUES (
    gen_random_uuid(),
    :tenant_id,
    :user_id,
    :request_id,
    :correlation_id,
    :original_query,
    :rewritten_query,
    :was_rewritten,
    :latency_ms,
    NOW()
);
"""
