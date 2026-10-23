FLOW_INSERT_GENERATION_AUDIT = """
INSERT INTO generation_audit_logs (
    id,
    public_id,
    tenant_id,
    query,
    answer,
    abstained,
    cited_chunk_ids,
    model_name,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :query,
    :answer,
    :abstained,
    :cited_chunk_ids,
    :model_name,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_GENERATION_AUDIT_BY_CORRELATION = """
SELECT id, public_id, tenant_id, query, answer, abstained, cited_chunk_ids, model_name
FROM generation_audit_logs
WHERE tenant_id = :tenant_id AND correlation_id = :correlation_id
LIMIT 1;
"""
