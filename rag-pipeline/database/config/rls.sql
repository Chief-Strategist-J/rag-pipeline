ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;

CREATE POLICY documents_tenant_isolation ON documents
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.current_tenant_id', true));

CREATE POLICY document_chunks_tenant_isolation ON document_chunks
    AS RESTRICTIVE
    USING (tenant_id = current_setting('app.current_tenant_id', true));
