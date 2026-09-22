import math
from types import SimpleNamespace
from typing import cast

import pandas as pd
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.analytics.service import AnalyticsService
from backend.app.domain.sales import scoring
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.store.repository import StoreRepository
from backend.app.domain.store.service import StoreService
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.trade_area.service import TradeAreaService


@pytest.mark.asyncio
async def test_trade_area_search_excludes_areas_without_exploration_score():
    trade_areas = [
        {
            "trdar_cd": "SCORABLE",
            "trdar_se_cd": "A",
            "trdar_cd_nm": "점수가능상권",
            "signgu_cd": "11500",
            "signgu_cd_nm": "강서구",
        },
        {
            "trdar_cd": "MISSING_SCORE",
            "trdar_se_cd": "A",
            "trdar_cd_nm": "점수없음상권",
            "signgu_cd": "11500",
            "signgu_cd_nm": "강서구",
        },
    ]
    trade_area_repo = cast(
        TradeAreaRepository,
        SimpleNamespace(get_by_filters=lambda **_: _async_return(trade_areas)),
    )
    metrics_repo = cast(
        SalesRepository,
        SimpleNamespace(
            get_metrics_dataframe=lambda *_: _async_return(
                pd.DataFrame(
                    [
                        {"trdar_cd": "SCORABLE", "exploration_score": 72.0},
                        {"trdar_cd": "MISSING_SCORE", "exploration_score": float("nan")},
                    ]
                )
            )
        ),
    )

    service = TradeAreaService(
        repository=trade_area_repo,
        sales_repo=metrics_repo,
    )

    results = await service.get_trade_areas_by_filters(
        industry_code="CS100010",
        signgu_cd="11500",
        quarter="20262",
    )

    assert [result.code for result in results] == ["SCORABLE"]


@pytest.mark.asyncio
async def test_all_trade_areas_preserves_metadata_without_exploration_score():
    trade_areas = [
        {
            "trdar_cd": "SCORABLE",
            "trdar_se_cd": "A",
            "trdar_cd_nm": "점수가능상권",
            "signgu_cd": "11500",
            "signgu_cd_nm": "강서구",
        },
        {
            "trdar_cd": "MISSING_SCORE",
            "trdar_se_cd": "A",
            "trdar_cd_nm": "점수없음상권",
            "signgu_cd": "11500",
            "signgu_cd_nm": "강서구",
        },
    ]
    trade_area_repo = cast(
        TradeAreaRepository,
        SimpleNamespace(get_all=lambda: _async_return(trade_areas)),
    )
    metrics_repo = cast(
        SalesRepository,
        SimpleNamespace(
            get_metrics_dataframe=lambda *_: _async_return(
                pd.DataFrame(
                    [
                        {"trdar_cd": "SCORABLE", "exploration_score": 72.0},
                        {"trdar_cd": "MISSING_SCORE", "exploration_score": float("nan")},
                    ]
                )
            )
        ),
    )

    service = TradeAreaService(
        repository=trade_area_repo,
        sales_repo=metrics_repo,
    )

    results = await service.get_all_trade_areas()

    assert [result.trdar_cd for result in results] == [
        "SCORABLE",
        "MISSING_SCORE",
    ]


@pytest.mark.asyncio
async def test_3110679_is_excluded_while_scoreable_area_is_kept_everywhere():
    trade_areas = [
        {
            "trdar_cd": "3110679",
            "trdar_se_cd": "A",
            "trdar_cd_nm": "염창역 2번",
            "signgu_cd": "11500",
            "signgu_cd_nm": "강서구",
        },
        {
            "trdar_cd": "SCORABLE",
            "trdar_se_cd": "A",
            "trdar_cd_nm": "점수가능상권",
            "signgu_cd": "11500",
            "signgu_cd_nm": "강서구",
        },
    ]
    metrics = scoring.build_metrics_dataframe(
        [
            {
                "trdar_cd": "3110679",
                "sales": 6_587_904,
                "transaction_count": 2_167,
                "prev_sales": None,
                "prev_transaction_count": None,
                "store_count": 7,
                "closing_rate": 14.0,
            },
            {
                "trdar_cd": "SCORABLE",
                "sales": 10_000,
                "transaction_count": 200,
                "prev_sales": 9_000,
                "prev_transaction_count": 180,
                "store_count": 5,
                "closing_rate": 10.0,
            },
        ]
    )
    trade_area_repo = cast(
        TradeAreaRepository,
        SimpleNamespace(
            get_all=lambda: _async_return(trade_areas),
            get_by_filters=lambda **_: _async_return(trade_areas),
        ),
    )
    metrics_repo = cast(
        SalesRepository,
        SimpleNamespace(get_metrics_dataframe=lambda *_: _async_return(metrics)),
    )
    trade_area_service = TradeAreaService(
        repository=trade_area_repo,
        sales_repo=metrics_repo,
    )
    analytics_service = AnalyticsService(
        trade_area_repo=trade_area_repo,
        sales_repo=metrics_repo,
        store_service=StoreService(
            repository=StoreRepository(session=cast(AsyncSession, None))
        ),
    )

    search_results = await trade_area_service.get_trade_areas_by_filters(
        industry_code="CS100010",
        signgu_cd="11500",
        quarter="20262",
    )
    all_results = await trade_area_service.get_all_trade_areas()
    recommendations = await analytics_service.get_recommendations(
        industry_code="CS100010",
        quarter="20262",
        region="강서구",
    )

    target_metrics = metrics.loc[metrics["trdar_cd"] == "3110679"].iloc[0]
    assert math.isnan(target_metrics["exploration_score"])
    assert [result.code for result in search_results] == ["SCORABLE"]
    assert [result.trdar_cd for result in all_results] == [
        "3110679",
        "SCORABLE",
    ]
    assert [result.trade_area_code for result in recommendations] == ["SCORABLE"]


async def _async_return(value):
    return value
