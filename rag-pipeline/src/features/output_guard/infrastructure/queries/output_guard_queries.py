FLOW_INSERT_OUTPUT_GUARD_AUDIT = """
INSERT INTO output_guard_audit_logs (
    id,
    public_id,
    tenant_id,
    action,
    hallucinated_count,
    removed_links_count,
    is_grounded,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :action,
    :hallucinated_count,
    :removed_links_count,
    :is_grounded,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_OUTPUT_GUARD_AUDIT_BY_CORRELATION = """
SELECT id, public_id, tenant_id, action, hallucinated_count, removed_links_count, is_grounded
FROM output_guard_audit_logs
WHERE tenant_id = :tenant_id AND correlation_id = :correlation_id
LIMIT 1;
"""
