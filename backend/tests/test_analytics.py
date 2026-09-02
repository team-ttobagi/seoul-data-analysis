import pytest
from backend.app.domain.analytics.service import AnalyticsService
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.sales.repository import SalesRepository


def test_exploration_score_calculation():
    service = AnalyticsService(
        trade_area_repo=TradeAreaRepository(),
        sales_repo=SalesRepository(),
    )

    # 1. Test standard calculation: 91 * 0.40 + 85 * 0.35 + 62 * 0.25 = 36.4 + 29.75 + 15.5 = 81.65 -> 82
    score = service.calculate_exploration_score(
        sales_growth_norm=91,
        transaction_volume_norm=85,
        competition_norm=62,
    )
    assert score == 82

    # 2. Test maximum score bounds
    max_score = service.calculate_exploration_score(100, 100, 100)
    assert max_score == 100

    # 3. Test minimum score bounds
    min_score = service.calculate_exploration_score(0, 0, 0)
    assert min_score == 0


@pytest.mark.asyncio
async def test_recommendations_generation():
    service = AnalyticsService(
        trade_area_repo=TradeAreaRepository(),
        sales_repo=SalesRepository(),
    )

    recs = await service.get_recommendations(industry_code="CS100010", quarter="2026 Q2")
    assert len(recs) >= 3
    assert recs[0].rank == 1
    assert recs[0].trade_area_code == "SEONGSU"
    assert recs[0].score == 82
    assert "growth" in recs[0].signals
    assert recs[0].components.sales_growth.normalized_score == 91
