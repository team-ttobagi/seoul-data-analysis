import math
import pytest
from types import SimpleNamespace

from backend.app.domain.analytics.service import AnalyticsService
from backend.app.domain.sales import scoring
from backend.app.domain.store.service import StoreService
from backend.app.domain.store.repository import StoreRepository
from backend.app.domain.trade_area.service import TradeAreaService
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


@pytest.mark.asyncio
async def test_unscorable_area_is_excluded_from_search_and_recommendations():
    trade_area = {
        "trdar_cd": "MISSING_SCORE",
        "trdar_se_cd": "A",
        "trdar_cd_nm": "점수없음상권",
        "signgu_cd": "11140",
        "signgu_cd_nm": "중구",
    }
    metrics_rows = [
        {
            "trdar_cd": "MISSING_SCORE",
            "sales": 1_000,
            "transaction_count": 100,
            "prev_sales": 900,
            "prev_transaction_count": 90,
            # 검색에는 현재 분기 매출이 있어 포함되지만, 점포 데이터가 없어
            # CompetitionScore와 ExplorationScore를 계산할 수 없다.
            "store_count": None,
            "closing_rate": None,
        }
    ]

    trade_area_repo = SimpleNamespace(
        get_all=lambda: _async_return([trade_area]),
        get_by_filters=lambda **_: _async_return([trade_area]),
    )
    sales_repo = SimpleNamespace(
        get_metrics_dataframe=lambda *_: _async_return(
            scoring.build_metrics_dataframe(metrics_rows)
        )
    )
    analytics_service = AnalyticsService(
        trade_area_repo=trade_area_repo,
        sales_repo=sales_repo,
        store_service=StoreService(repository=StoreRepository(session=None)),
    )

    search_results = await TradeAreaService(
        trade_area_repo,
        sales_repo,
    ).get_trade_areas_by_filters(
        industry_code="CS100010",
        signgu_cd="11140",
        quarter="20261",
    )
    recommendations = await analytics_service.get_recommendations(
        industry_code="CS100010",
        quarter="20261",
        region="중구",
        keyword="점수없음",
    )

    metrics = await sales_repo.get_metrics_dataframe("20261", "CS100010")
    assert search_results == []
    assert math.isnan(metrics.loc[0, "exploration_score"])
    assert recommendations == []


async def _async_return(value):
    return value
