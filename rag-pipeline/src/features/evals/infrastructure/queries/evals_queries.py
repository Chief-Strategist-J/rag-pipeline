FLOW_INSERT_EVAL_METRIC = """
INSERT INTO evaluation_metrics (
    id,
    public_id,
    tenant_id,
    query_id,
    recall_at_k,
    mrr,
    faithfulness_score,
    is_abstain_appropriate,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :query_id,
    :recall_at_k,
    :mrr,
    :faithfulness_score,
    :is_abstain_appropriate,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_EVAL_SUMMARY_BY_TENANT = """
SELECT AVG(recall_at_k) as avg_recall, AVG(mrr) as avg_mrr, AVG(faithfulness_score) as avg_faithfulness
FROM evaluation_metrics
WHERE tenant_id = :tenant_id;
"""
