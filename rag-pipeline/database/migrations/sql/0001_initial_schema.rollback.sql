-- migration:      0001
-- description:    rollback initial schema for multi-tenant authz and rag pipeline audit
-- author:         rag-pipeline-architect
-- date:           2026-10-23
-- depends_on:     NONE
-- reversible:     YES
-- lock_risk:      LOW
-- rows_affected:  schema only
-- reason:         clean rollback of 0001 initial schema

DROP INDEX IF EXISTS idx_rewrite_audit_tenant_corr;
DROP INDEX IF EXISTS idx_rewrite_audit_req;
DROP INDEX IF EXISTS idx_perm_scopes_tenant_user;
DROP INDEX IF EXISTS idx_tenants_status;

DROP TABLE IF EXISTS query_rewrite_audit_logs;
DROP TABLE IF EXISTS permission_scopes;
DROP TABLE IF EXISTS tenants;
