FLOW_INSERT_RERANK_AUDIT = """
INSERT INTO rerank_audit_logs (
    id,
    public_id,
    tenant_id,
    query,
    total_evaluated,
    total_selected,
    latency_ms,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :query,
    :total_evaluated,
    :total_selected,
    :latency_ms,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_RERANK_AUDIT_BY_CORRELATION = """
SELECT id, public_id, tenant_id, query, total_evaluated, total_selected, latency_ms
FROM rerank_audit_logs
WHERE tenant_id = :tenant_id AND correlation_id = :correlation_id
LIMIT 1;
"""
