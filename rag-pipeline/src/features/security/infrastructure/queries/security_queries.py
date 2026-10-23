FLOW_INSERT_SECURITY_THREAT = """
INSERT INTO security_threat_audit_logs (
    id,
    public_id,
    tenant_id,
    threat_type,
    severity,
    matched_pattern,
    correlation_id,
    created_at
) VALUES (
    gen_random_uuid(),
    :public_id,
    :tenant_id,
    :threat_type,
    :severity,
    :matched_pattern,
    :correlation_id,
    NOW()
);
"""

FLOW_SELECT_SECURITY_THREATS_BY_CORRELATION = """
SELECT id, public_id, tenant_id, threat_type, severity, matched_pattern
FROM security_threat_audit_logs
WHERE tenant_id = :tenant_id AND correlation_id = :correlation_id;
"""
