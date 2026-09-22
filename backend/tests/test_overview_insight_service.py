import logging
from types import SimpleNamespace
from typing import cast

import pandas as pd
import pytest
from asyncpg.exceptions import InternalServerError

from backend.app.domain.analytics.service import AnalyticsService
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.store.service import StoreService
from backend.app.domain.store.schemas import StoreTrendSchema
from backend.app.domain.trade_area.repository import TradeAreaRepository


async def _return(value):
    return value


def _metrics_repo(row: dict, pattern_facts: dict | None = None):
    if pattern_facts is None:
        pattern_facts = {
            "age": {
                "10대": 0.0,
                "20대": 0.0,
                "30대": 0.0,
                "40대": 65.38,
                "50대": 0.0,
                "60대 이상": 34.62,
            },
            "day": {
                "월": 19.23,
                "화": 0.0,
                "수": 0.0,
                "목": 23.08,
                "금": 30.77,
                "토": 26.92,
                "일": 0.0,
            },
            "time": {
                "새벽": 0.0,
                "오전": 0.0,
                "점심": 7.69,
                "오후": 26.92,
                "저녁": 65.38,
                "밤": 0.0,
            },
            "age_identified_sales_coverage_pct": 100.0,
        }

    return SimpleNamespace(
        get_metrics_dataframe=lambda *_: _return(pd.DataFrame([row])),
        get_insight_pattern_facts=lambda *_: _return(pattern_facts),
    )


def _service(row: dict, generator=None, sales_repo=None, db_session=None):
    trade_area_repo = cast(
        TradeAreaRepository,
        SimpleNamespace(
            get_by_code=lambda code: _return(
                {
                    "trdar_cd_nm": "테스트상권",
                    "signgu_cd_nm": "테스트구",
                }
            )
        ),
    )
    store_service = cast(
        StoreService,
        SimpleNamespace(
            get_store_trend=lambda **_: _return(
                StoreTrendSchema(
                    store_count=int(row["store_count"]),
                    store_count_change=int(row["store_count_change"]),
                )
            ),
            get_summary=lambda **_: _return(None),
        ),
    )
    resolved_sales_repo = cast(
        SalesRepository,
        sales_repo or _metrics_repo(row),
    )
    return AnalyticsService(
        trade_area_repo=trade_area_repo,
        sales_repo=resolved_sales_repo,
        store_service=store_service,
        insight_generator=generator,
        db_session=db_session,
    )


@pytest.mark.asyncio
async def test_extreme_survives_generator_unavailable_fallback():
    row = {
        "trdar_cd": "3110729",
        "sales": 196567593,
        "transaction_count": 741,
        "prev_sales": 2348993,
        "prev_transaction_count": 480,
        "growth_rate": 8268.164272945896,
        "growth_score": 90.0,
        "transaction_score": 20.0,
        "competition_score": 80.0,
        "store_count": 3,
        "store_count_change": 0,
    }

    response = await _service(row).get_overview_insight("3110729", "CS300021", "20262")

    assert response.extreme is True
    assert response.source == "fallback"
    assert response.status == "fallback"


@pytest.mark.asyncio
async def test_fallback_includes_verified_pattern_tags():
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }

    response = await _service(row).get_overview_insight("3111067", "CS200029", "20262")

    assert response.source == "fallback"
    assert response.status == "fallback"
    assert response.summary.startswith("[40대·저녁 중심] ")
    assert len(response.summary) <= 120


class _CaptureGenerator:
    def __init__(self):
        self.context = None

    async def generate(self, context):
        self.context = context
        return "[40대·저녁 중심] 거래건수는 유지됐지만 거래당 추정 매출액이 16.6% 증가했습니다."


class _FailingGenerator:
    async def generate(self, context):
        raise RuntimeError("provider unavailable")


class _SessionAwareGenerator:
    def __init__(self, session):
        self.session = session

    async def generate(self, context):
        assert self.session.rollback_called is True
        return "[40대·저녁 중심] 거래건수는 유지됐지만 거래당 추정 매출액이 16.6% 증가했습니다."


class _TrackingSession:
    rollback_called = False

    async def rollback(self):
        self.rollback_called = True


async def _raise_pattern_lookup_error(*_):
    raise RuntimeError("pattern facts unavailable")


async def _raise_pattern_db_error(*_):
    raise InternalServerError("EMAXCONNSESSION max clients reached")


class _TwoSentenceGenerator:
    async def generate(self, context):
        return "매출은 16.6% 증가했습니다. 거래건수는 전분기와 같습니다."


@pytest.mark.asyncio
async def test_context_contains_verified_relationship_metrics_and_allowed_candidates():
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }
    generator = _CaptureGenerator()

    response = await _service(row, generator).get_overview_insight(
        "3111067", "CS200029", "20262"
    )

    assert response.source == "gemini"
    assert response.status == "generated"
    assert response.extreme is False
    assert generator.context is not None
    assert generator.context.current_sales == 3271104
    assert generator.context.transaction_count == 76
    assert generator.context.transaction_qoq_rate == 0
    assert generator.context.sales_per_transaction_qoq_rate == pytest.approx(
        16.59, rel=1e-3
    )
    assert generator.context.tag_candidates == ["40대", "저녁"]


@pytest.mark.asyncio
async def test_overview_insight_releases_read_transaction_before_external_generation():
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }
    session = _TrackingSession()

    response = await _service(
        row,
        _SessionAwareGenerator(session),
        db_session=session,
    ).get_overview_insight("3111067", "CS200029", "20262")

    assert response.source == "gemini"
    assert session.rollback_called is True


@pytest.mark.asyncio
async def test_service_accepts_two_sentence_summary():
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }

    response = await _service(row, _TwoSentenceGenerator()).get_overview_insight(
        "3111067", "CS200029", "20262"
    )

    assert response.source == "gemini"
    assert response.status == "generated"


@pytest.mark.asyncio
async def test_pattern_lookup_failure_is_not_logged_as_no_candidates(caplog):
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }
    sales_repo = _metrics_repo(row)
    sales_repo.get_insight_pattern_facts = _raise_pattern_lookup_error

    caplog.set_level(logging.INFO, logger="backend.app.domain.analytics.service")
    response = await _service(
        row,
        _CaptureGenerator(),
        sales_repo=sales_repo,
    ).get_overview_insight("3111067", "CS200029", "20262")

    assert response.source == "gemini"
    reasons = [record.reason for record in caplog.records if hasattr(record, "reason")]
    assert "patterns_error" in reasons
    assert "patterns_no_candidates" not in reasons


@pytest.mark.asyncio
async def test_pattern_db_error_is_not_treated_as_missing_pattern_data():
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }
    sales_repo = _metrics_repo(row)
    sales_repo.get_insight_pattern_facts = _raise_pattern_db_error

    with pytest.raises(InternalServerError, match="EMAXCONNSESSION"):
        await _service(
            row,
            _CaptureGenerator(),
            sales_repo=sales_repo,
        ).get_overview_insight("3111067", "CS200029", "20262")


@pytest.mark.asyncio
async def test_no_tag_candidates_is_logged_separately_from_lookup_failure(caplog):
    row = {
        "trdar_cd": "3111067",
        "sales": 3271104,
        "transaction_count": 76,
        "prev_sales": 2805601,
        "prev_transaction_count": 76,
        "growth_rate": 16.59191738240755,
        "growth_score": 30.0,
        "transaction_score": 20.0,
        "competition_score": 50.0,
        "store_count": 8,
        "store_count_change": 0,
    }
    pattern_facts = {
        "age": {
            label: 16.67
            for label in ("10대", "20대", "30대", "40대", "50대", "60대 이상")
        },
        "day": {label: 14.29 for label in ("월", "화", "수", "목", "금", "토", "일")},
        "time": {
            label: 16.67 for label in ("새벽", "오전", "점심", "오후", "저녁", "밤")
        },
        "age_identified_sales_coverage_pct": 100.0,
    }
    generator = _CaptureGenerator()

    caplog.set_level(logging.INFO, logger="backend.app.domain.analytics.service")
    response = await _service(
        row,
        generator,
        sales_repo=_metrics_repo(row, pattern_facts),
    ).get_overview_insight("3111067", "CS200029", "20262")

    assert response.source == "gemini"
    assert generator.context is not None
    assert generator.context.tag_candidates == []
    reasons = [record.reason for record in caplog.records if hasattr(record, "reason")]
    assert "patterns_no_candidates" in reasons
    assert "patterns_error" not in reasons


@pytest.mark.asyncio
async def test_generator_error_keeps_extreme_state_and_uses_fallback():
    row = {
        "trdar_cd": "3110729",
        "sales": 196567593,
        "transaction_count": 741,
        "prev_sales": 2348993,
        "prev_transaction_count": 480,
        "growth_rate": 8268.164272945896,
        "growth_score": 90.0,
        "transaction_score": 20.0,
        "competition_score": 80.0,
        "store_count": 3,
        "store_count_change": 0,
    }

    response = await _service(row, _FailingGenerator()).get_overview_insight(
        "3110729", "CS300021", "20262"
    )

    assert response.extreme is True
    assert response.source == "fallback"
    assert response.status == "fallback"
