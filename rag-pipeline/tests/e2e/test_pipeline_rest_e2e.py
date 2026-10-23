import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app


@pytest.mark.asyncio
async def test_pipeline_query_endpoint_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "tenantId": "tenant-corp",
            "userId": "user-ops",
            "query": "What is the travel expense submission deadline?",
            "conversationHistory": []
        }
        headers = {
            "Content-Type": "application/json",
            "x-request-id": "req-rest-pipeline-001",
            "traceparent": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
        }

        response = await client.post("/api/v1/pipeline/query", json=payload, headers=headers)
        assert response.status_code == 200

        body = response.json()
        assert body["success"] is True
        assert body["statusCode"] == 200
        assert body["meta"]["requestId"] == "req-rest-pipeline-001"
        assert body["meta"]["apiVersion"] == "v1"

        data = body["data"]
        assert data["tenantId"] == "tenant-corp"
        assert "30 days" in data["answer"]
        assert "doc-policy:v1:c0000" in data["citedChunkIds"]
        assert data["abstained"] is False
        assert data["isGrounded"] is True


@pytest.mark.asyncio
async def test_pipeline_query_endpoint_extra_field_rejected():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        payload = {
            "tenantId": "tenant-corp",
            "userId": "user-ops",
            "query": "What is the travel expense submission deadline?",
            "conversationHistory": [],
            "unknownInjectedField": "not_allowed"
        }
        headers = {
            "Content-Type": "application/json",
            "x-request-id": "req-rest-pipeline-002"
        }

        response = await client.post("/api/v1/pipeline/query", json=payload, headers=headers)
        assert response.status_code == 400

        body = response.json()
        assert body["success"] is False
        assert body["statusCode"] == 400
        assert body["error"]["code"] == "VALIDATION_ERROR"
