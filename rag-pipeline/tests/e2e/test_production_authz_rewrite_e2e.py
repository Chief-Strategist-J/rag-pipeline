import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.mark.asyncio
async def test_production_e2e_first_turn_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "query": "What is the organization refund policy?",
            "tenantId": "org_987654",
            "userId": "usr_123456",
            "conversationHistory": [],
            "skipRewriteIfFirstTurn": True
        }
        headers = {
            "Content-Type": "application/json",
            "x-request-id": "req_prod_test_001",
            "x-tenant-id": "org_987654",
            "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
        }

        response = await client.post("/api/v1/authz-rewrite/process", json=payload, headers=headers)
        assert response.status_code == 200

        body = response.json()
        assert body["success"] is True
        assert body["statusCode"] == 200
        assert body["meta"]["requestId"] == "req_prod_test_001"
        assert body["meta"]["apiVersion"] == "v1"

        data = body["data"]
        assert data["originalQuery"] == "What is the organization refund policy?"
        assert data["rewrittenQuery"] == "What is the organization refund policy?"
        assert data["wasRewritten"] is False
        assert data["permissionScope"]["tenantId"] == "org_987654"
        assert "INTERNAL" in data["permissionScope"]["allowedAcls"]


@pytest.mark.asyncio
async def test_production_e2e_multi_turn_follow_up_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "query": "Does that apply to enterprise subscriptions too?",
            "tenantId": "org_987654",
            "userId": "usr_123456",
            "conversationHistory": [
                {
                    "role": "user",
                    "content": "Can I get a refund if I cancel within 14 days?"
                },
                {
                    "role": "assistant",
                    "content": "Standard plans are eligible for full refunds within 14 days."
                }
            ],
            "skipRewriteIfFirstTurn": True
        }
        headers = {
            "Content-Type": "application/json",
            "x-request-id": "req_prod_test_002",
            "x-tenant-id": "org_987654"
        }

        response = await client.post("/api/v1/authz-rewrite/process", json=payload, headers=headers)
        assert response.status_code == 200

        body = response.json()
        assert body["success"] is True
        assert body["statusCode"] == 200
        assert "rewrittenQuery" in body["data"]


@pytest.mark.asyncio
async def test_production_e2e_closed_schema_rejection_on_undeclared_fields():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "query": "Query text",
            "tenantId": "org_1",
            "userId": "usr_1",
            "unauthorizedExtraField": "malicious injection"
        }
        headers = {"Content-Type": "application/json"}

        response = await client.post("/api/v1/authz-rewrite/process", json=payload, headers=headers)
        assert response.status_code == 400

        body = response.json()
        assert body["success"] is False
        assert body["statusCode"] == 400
        assert body["error"]["code"] == "VALIDATION_FAILED"
