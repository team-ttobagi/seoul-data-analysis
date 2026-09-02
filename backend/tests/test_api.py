from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_list_trade_areas():
    response = client.get("/api/v1/trade-areas")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert any(ta["code"] == "SEONGSU" for ta in data)


def test_list_industries():
    response = client.get("/api/v1/industries")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(ind["code"] == "CS100010" for ind in data)


def test_analytics_recommendations():
    response = client.get("/api/v1/analytics/recommendations?industry_code=CS100010&quarter=2026%20Q2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert data[0]["trade_area_code"] == "SEONGSU"
    assert data[0]["score"] == 82


def test_district_overview():
    response = client.get("/api/v1/trade-areas/SEONGSU/overview?industry_code=CS100010&quarter=2026%20Q2")
    assert response.status_code == 200
    data = response.json()
    assert data["trade_area_code"] == "SEONGSU"
    assert data["kpis"]["estimated_sales_formatted"] == "12.8억"
    assert data["kpis"]["transaction_count_formatted"] == "45만"


def test_district_patterns():
    response = client.get("/api/v1/trade-areas/SEONGSU/patterns?industry_code=CS100010&quarter=2026%20Q2")
    assert response.status_code == 200
    data = response.json()
    assert data["when"]["peak_slot"] == "17–21시"
    assert data["who"]["primary_target"] == "20대 여성"
    assert data["day"]["peak_day"] == "금요일"


def test_compare_districts():
    response = client.get("/api/v1/compare?trade_area_codes=SEONGSU,HONGDAE,SHAROSU&industry_code=CS100010")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["trade_area_code"] == "SEONGSU"
