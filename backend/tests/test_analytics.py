import math
from typing import cast

import pytest
import pandas as pd
from types import SimpleNamespace
from sqlalchemy.ext.asyncio import AsyncSession

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
        store_service=StoreService(
            repository=StoreRepository(session=cast(AsyncSession, None))
        ),
    )

    # 1. Test standard calculation: 91 * 0.40 + 85 * 0.35 + 62 * 0.25 = 81.65 -> 82
    score = round(
        scoring.exploration_score(
            pd.Series([91]), pd.Series([85]), pd.Series([62])
        ).iloc[0]
    )
    assert score == 82

    # 2. Test maximum score bounds
    max_score = round(
        scoring.exploration_score(
            pd.Series([100]), pd.Series([100]), pd.Series([100])
        ).iloc[0]
    )
    assert max_score == 100

    # 3. Test minimum score bounds
    min_score = round(
        scoring.exploration_score(
            pd.Series([0]), pd.Series([0]), pd.Series([0])
        ).iloc[0]
    )
    assert min_score == 0


@pytest.mark.asyncio
async def test_recommendations_generation():
    metrics = pd.DataFrame(
        [
            {
                "trdar_cd": "SEONGSU",
                "growth_rate": 12.0,
                "growth_score": 91.0,
                "transaction_count": 850,
                "transaction_score": 85.0,
                "competition_score": 62.0,
                "exploration_score": 81.65,
                "growth_percentile": 10.0,
                "volume_percentile": 20.0,
                "competition_percentile": 30.0,
            },
            {
                "trdar_cd": "OTHER_A",
                "growth_rate": 5.0,
                "growth_score": 50.0,
                "transaction_count": 500,
                "transaction_score": 50.0,
                "competition_score": 50.0,
                "exploration_score": 50.0,
                "growth_percentile": 50.0,
                "volume_percentile": 50.0,
                "competition_percentile": 50.0,
            },
            {
                "trdar_cd": "OTHER_B",
                "growth_rate": 1.0,
                "growth_score": 30.0,
                "transaction_count": 300,
                "transaction_score": 30.0,
                "competition_score": 30.0,
                "exploration_score": 30.0,
                "growth_percentile": 70.0,
                "volume_percentile": 70.0,
                "competition_percentile": 70.0,
            },
        ]
    )
    trade_areas = [
        {
            "trdar_cd": "SEONGSU",
            "trdar_cd_nm": "성수",
            "signgu_cd_nm": "성동구",
        },
        {
            "trdar_cd": "OTHER_A",
            "trdar_cd_nm": "기타A",
            "signgu_cd_nm": "중구",
        },
        {
            "trdar_cd": "OTHER_B",
            "trdar_cd_nm": "기타B",
            "signgu_cd_nm": "중구",
        },
    ]
    service = AnalyticsService(
        trade_area_repo=cast(
            TradeAreaRepository,
            SimpleNamespace(get_all=lambda: _async_return(trade_areas)),
        ),
        sales_repo=cast(
            SalesRepository,
            SimpleNamespace(get_metrics_dataframe=lambda *_: _async_return(metrics)),
        ),
        store_service=StoreService(
            repository=StoreRepository(session=cast(AsyncSession, None))
        ),
    )

    recs = await service.get_recommendations(
        industry_code="CS100010", quarter="20262"
    )
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

    trade_area_repo = cast(
        TradeAreaRepository,
        SimpleNamespace(
            get_all=lambda: _async_return([trade_area]),
            get_by_filters=lambda **_: _async_return([trade_area]),
        ),
    )
    sales_repo = cast(
        SalesRepository,
        SimpleNamespace(
            get_metrics_dataframe=lambda *_: _async_return(
                scoring.build_metrics_dataframe(metrics_rows)
            )
        ),
    )
    analytics_service = AnalyticsService(
        trade_area_repo=trade_area_repo,
        sales_repo=sales_repo,
        store_service=StoreService(
            repository=StoreRepository(session=cast(AsyncSession, None))
        ),
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
