FLOW_INSERT_TELEMETRY_RECORD = """
INSERT INTO pipeline_telemetry_records (
    id,
    public_id,
    tenant_id,
    request_id,
    trace_id,
    total_duration_ms,
    has_error,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :request_id,
    :trace_id,
    :total_duration_ms,
    :has_error,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_TELEMETRY_BY_REQUEST_ID = """
SELECT id, public_id, tenant_id, request_id, trace_id, total_duration_ms, has_error
FROM pipeline_telemetry_records
WHERE tenant_id = :tenant_id AND request_id = :request_id
LIMIT 1;
"""
