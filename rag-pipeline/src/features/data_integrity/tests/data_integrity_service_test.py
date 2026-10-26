import pytest
from src.features.data_integrity.service.data_integrity_service import (
    DataIntegrityService,
)
from src.features.data_integrity.infrastructure.adapters.data_integrity_adapters import (
    MemoryDataIntegrityRepositoryAdapter,
)
from src.features.data_integrity.contracts.data_integrity_types import (
    IntegrityValidationRequestDTO,
)


@pytest.mark.asyncio
async def test_data_integrity_service_full_pass():
    repo = MemoryDataIntegrityRepositoryAdapter()
    service = DataIntegrityService(type("Deps", (), {"repo_port": repo})())

    req = IntegrityValidationRequestDTO(
        tenantId="tenant-corp",
        correlationId="req-100",
        entityName="orders",
        payload={
            "tenantId": "tenant-corp",
            "source": "shopify",
            "externalId": "ord_88899",
            "correlationId": "req-100",
            "status": "confirmed",
            "amount": 250.00,
            "currency": "usd"
        }
    )

    res = await service.validate_and_enforce(req)
    assert res.is_ok is True
    val = res.value
    assert val.isValid is True
    assert val.normalizedEntity.currency == "USD"
    assert len(val.violations) == 0


@pytest.mark.asyncio
async def test_data_integrity_service_storage_duplicate_rejection():
    repo = MemoryDataIntegrityRepositoryAdapter()
    service = DataIntegrityService(type("Deps", (), {"repo_port": repo})())

    req = IntegrityValidationRequestDTO(
        tenantId="tenant-corp",
        correlationId="req-101",
        entityName="orders",
        payload={
            "tenantId": "tenant-corp",
            "source": "shopify",
            "externalId": "dup-key",
            "correlationId": "req-101",
            "status": "confirmed",
            "amount": 10.0,
            "currency": "USD"
        }
    )

    res1 = await service.validate_and_enforce(req)
    assert res1.is_ok is True
    assert res1.value.isValid is True

    res2 = await service.validate_and_enforce(req)
    assert res2.is_ok is True
    assert res2.value.isValid is False
    assert any(v.ruleName == "orders_tenant_ext_uk" for v in res2.value.violations)
