import httpx
import pytest

from backend.app.domain.trade_area.router import get_trade_area_service
from backend.app.domain.trade_area.schemas import (
    TradeAreaResponse,
    TradeAreaSearchResponse,
)
from backend.app.core.exceptions import TradeAreaNotFoundException
from backend.app.main import app



def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    )


class FakeTradeAreaService:
    def __init__(self):
        self.calls = []

    async def get_trade_areas_by_filters(
        self,
        *,
        industry_code: str,
        signgu_cd: str,
        quarter: str,
    ):
        self.calls.append(
            {
                "industry_code": industry_code,
                "signgu_cd": signgu_cd,
                "quarter": quarter,
            }
        )
        return [
            TradeAreaSearchResponse(
                code="SEOUL_CITY_HALL",
                name="서울시청",
                district_code=signgu_cd,
                district_name="중구",
            ),
            TradeAreaSearchResponse(
                code="OTHER_AREA",
                name="다른상권",
                district_code=signgu_cd,
                district_name="중구",
            ),
        ]

    async def get_trade_area(self, code: str):
        self.calls.append({"method": "get_trade_area", "code": code})
        if code == "MISSING_AREA":
            raise TradeAreaNotFoundException(code)
        return TradeAreaResponse(
            trdar_cd=code,
            trdar_se_cd="A",
            trdar_cd_nm="서울시청",
            signgu_cd="11140",
            signgu_cd_nm="중구",
        )


async def _request_trade_area_search(params: dict):
    service = FakeTradeAreaService()
    app.dependency_overrides[get_trade_area_service] = lambda: service
    try:
        async with _client() as client:
            response = await client.get("/api/v1/trade-areas/search", params=params)
    finally:
        app.dependency_overrides.pop(get_trade_area_service, None)
    return response, service


async def _request_trade_area_detail(code: str):
    service = FakeTradeAreaService()
    app.dependency_overrides[get_trade_area_service] = lambda: service
    try:
        async with _client() as client:
            response = await client.get(f"/api/v1/trade-areas/{code}")
    finally:
        app.dependency_overrides.pop(get_trade_area_service, None)
    return response, service


@pytest.mark.asyncio
async def test_health_check():
    async with _client() as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_search_trade_areas_by_district():
    response, _ = await _request_trade_area_search(
        {
            "industry_code": "CS100010",
            "signgu_cd": "11140",
            "quarter": "20261",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    assert all(ta["district_code"] == "11140" for ta in data)


@pytest.mark.asyncio
async def test_search_trade_areas_by_district_and_query_contract():
    response, service = await _request_trade_area_search(
        {
            "industry_code": "CS100010",
            "signgu_cd": "11140",
            "quarter": "20262",
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert all(ta["district_code"] == "11140" for ta in data)

    assert service.calls == [
        {
            "industry_code": "CS100010",
            "signgu_cd": "11140",
            "quarter": "20262",
        }
    ]


@pytest.mark.asyncio
async def test_search_trade_areas_rejects_display_quarter_format():
    async with _client() as client:
        response = await client.get(
            "/api/v1/trade-areas/search",
            params={
                "industry_code": "CS100010",
                "signgu_cd": "11140",
                "quarter": "2026 Q2",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_trade_area_by_code_returns_detail_contract():
    response, service = await _request_trade_area_detail("SEOUL_CITY_HALL")

    assert response.status_code == 200
    assert response.json() == {
        "trdar_cd": "SEOUL_CITY_HALL",
        "trdar_se_cd": "A",
        "trdar_cd_nm": "서울시청",
        "signgu_cd": "11140",
        "signgu_cd_nm": "중구",
    }
    assert service.calls == [
        {"method": "get_trade_area", "code": "SEOUL_CITY_HALL"}
    ]


@pytest.mark.asyncio
async def test_get_trade_area_by_code_returns_structured_not_found_error():
    response, service = await _request_trade_area_detail("MISSING_AREA")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TRADE_AREA_NOT_FOUND",
            "message": "Trade area with code 'MISSING_AREA' was not found.",
        }
    }
    assert service.calls == [
        {"method": "get_trade_area", "code": "MISSING_AREA"}
    ]
