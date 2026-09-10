from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_trade_areas_by_district():
    response = client.get("/api/v1/trade-areas/search?signgu_cd=11140")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    assert all(ta["district_code"] == "11140" for ta in data)


def test_search_trade_areas_by_district_and_keyword():
    response = client.get(
        "/api/v1/trade-areas/search" "?signgu_cd=11140" "&keyword=서울시청"
    )

    assert response.status_code == 200

    data = response.json()

    assert all(ta["district_code"] == "11140" for ta in data)

    assert all("서울시청" in ta["name"] for ta in data)
