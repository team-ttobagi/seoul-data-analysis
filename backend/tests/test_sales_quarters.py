from typing import List

import pytest
from fastapi.testclient import TestClient

from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.sales.router import get_sales_service
from backend.app.domain.sales.schemas import QuarterOptionResponse
from backend.app.domain.sales.service import SalesService
from backend.app.main import app


class FakeQuarterResult:
    def __init__(self, quarter_codes: List[str]):
        self.quarter_codes = quarter_codes

    def scalars(self):
        return self

    def all(self):
        return self.quarter_codes


class FakeQuarterSession:
    def __init__(self, quarter_codes: List[str]):
        self.quarter_codes = quarter_codes

    async def execute(self, _statement):
        return FakeQuarterResult(self.quarter_codes)


@pytest.mark.asyncio
async def test_quarter_codes_are_unique_descending_and_formatted():
    session = FakeQuarterSession(["20262", "20261", "20254"])
    service = SalesService(SalesRepository(session=session))
    quarters = await service.get_quarters()

    assert [quarter.code for quarter in quarters] == ["20262", "20261", "20254"]
    assert [quarter.value for quarter in quarters] == [
        "2026 Q2",
        "2026 Q1",
        "2025 Q4",
    ]


@pytest.mark.asyncio
async def test_quarters_returns_empty_list_when_sales_data_is_empty():
    session = FakeQuarterSession([])
    service = SalesService(SalesRepository(session=session))

    assert await service.get_quarters() == []


class FakeSalesService:
    async def get_quarters(self) -> List[QuarterOptionResponse]:
        return [QuarterOptionResponse(code="20262", value="2026 Q2")]

    async def get_summary(self, *_: str):
        return None


def test_get_quarters_endpoint_uses_sales_service():
    app.dependency_overrides[get_sales_service] = lambda: FakeSalesService()

    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/sales/quarters")
    finally:
        app.dependency_overrides.pop(get_sales_service, None)

    assert response.status_code == 200
    assert response.json() == [{"code": "20262", "value": "2026 Q2"}]


def test_sales_summary_accepts_quarter_code_and_rejects_display_value():
    app.dependency_overrides[get_sales_service] = lambda: FakeSalesService()

    try:
        with TestClient(app) as client:
            code_response = client.get(
                "/api/v1/sales/summary",
                params={"trade_area_code": "SEONGSU", "quarter": "20262"},
            )
            display_response = client.get(
                "/api/v1/sales/summary",
                params={"trade_area_code": "SEONGSU", "quarter": "2026 Q2"},
            )
    finally:
        app.dependency_overrides.pop(get_sales_service, None)

    assert code_response.status_code == 200
    assert display_response.status_code == 422
