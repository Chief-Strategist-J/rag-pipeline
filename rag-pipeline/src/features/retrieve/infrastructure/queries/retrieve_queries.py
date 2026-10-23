FLOW_INSERT_RETRIEVAL_AUDIT = """
INSERT INTO retrieval_audit_logs (
    id,
    public_id,
    tenant_id,
    user_id,
    query,
    total_candidates,
    top_chunk_id,
    rrf_score,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :user_id,
    :query,
    :total_candidates,
    :top_chunk_id,
    :rrf_score,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_RETRIEVAL_AUDIT_BY_CORRELATION = """
SELECT id, public_id, tenant_id, user_id, query, total_candidates, top_chunk_id, rrf_score
FROM retrieval_audit_logs
WHERE tenant_id = :tenant_id AND correlation_id = :correlation_id
LIMIT 1;
"""
