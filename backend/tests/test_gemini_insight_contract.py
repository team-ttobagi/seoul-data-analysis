import json
from types import SimpleNamespace
from typing import Any, cast

import pytest
from pydantic import ValidationError

from backend.app.domain.analytics.schemas import OverviewInsightContext
from backend.app.external.gemini.client import (
    GeminiInsightGenerator,
    GeminiInsightResponseError,
    _ensure_grounding,
)
from backend.app.external.gemini.prompts import SYSTEM_INSTRUCTION, build_overview_input
from backend.app.external.gemini.schemas import OverviewTakeawayInsight


def _context(**overrides) -> OverviewInsightContext:
    values = {
        "trade_area_name": "테스트상권",
        "district_name": "테스트구",
        "industry_name": "테스트업종",
        "quarter": "20262",
        "strongest_age_group": "60대+",
        "peak_slot": "17-21시",
        "peak_day": "금",
        "current_sales": 3271104,
        "previous_sales": 2805601,
        "transaction_count": 76,
        "previous_transaction_count": 76,
        "qoq_growth_rate": 16.5919,
        "transaction_qoq_rate": 0.0,
        "sales_per_transaction_current": 43040.84,
        "sales_per_transaction_previous": 36915.80,
        "sales_per_transaction_qoq_rate": 16.59,
        "growth_level": "낮음",
        "transaction_level": "낮음",
        "competition_level": "보통",
        "tag_candidates": ["40대", "저녁"],
    }
    values.update(overrides)
    return OverviewInsightContext(**values)


def test_prompt_exposes_verified_metrics_and_only_allowed_pattern_candidates():
    payload = json.loads(build_overview_input(_context()))
    context = payload["context"]

    assert context["current_sales"] == 3271104
    assert context["sales_per_transaction_qoq_rate"] == 16.59
    assert context["tag_candidates"] == ["40대", "저녁"]
    assert "strongest_age_group" not in context
    assert "peak_slot" not in context
    assert "peak_day" not in context


def test_system_instruction_targets_100_characters_while_validator_allows_120():
    assert "가장 설명 가치가 높은 관계 하나" in SYSTEM_INSTRUCTION
    assert "tag_candidates" in SYSTEM_INSTRUCTION
    assert "100자 이내를 목표로 하며" in SYSTEM_INSTRUCTION
    assert "120자" not in SYSTEM_INSTRUCTION


def test_non_candidate_tag_is_rejected_by_grounding():
    prompt = build_overview_input(_context())

    with pytest.raises(GeminiInsightResponseError):
        _ensure_grounding(
            "[50대·저녁 중심] 거래건수는 유지됐지만 거래당 추정 매출액이 16.6% 증가했습니다.",
            prompt,
        )


def test_candidate_tag_passes_grounding():
    prompt = build_overview_input(_context())

    _ensure_grounding(
        "[40대·저녁 중심] 거래건수는 유지됐지만 거래당 추정 매출액이 16.6% 증가했습니다.",
        prompt,
    )


def test_numeric_grounding_accepts_korean_amount_units_and_rounded_rate():
    amount_context = _context(
        sales_per_transaction_current=58351.56,
        sales_per_transaction_previous=58000.0,
    )
    _ensure_grounding(
        "거래당 추정 매출액은 약 6만 원입니다.",
        build_overview_input(amount_context),
    )
    _ensure_grounding(
        "거래당 추정 매출액은 약 5만 8천 원입니다.",
        build_overview_input(amount_context),
    )
    with pytest.raises(GeminiInsightResponseError):
        _ensure_grounding(
            "거래당 추정 매출액은 약 5만 7천 원입니다.",
            build_overview_input(amount_context),
        )

    large_amount_context = _context(
        current_sales=183870123,
        previous_sales=180000000,
    )
    _ensure_grounding(
        "전체 매출은 1억 8,387만 원입니다.",
        build_overview_input(large_amount_context),
    )

    won_amount_context = _context(sales_per_transaction_current=9617.4)
    _ensure_grounding(
        "거래당 추정 매출액은 9,617원입니다.",
        build_overview_input(won_amount_context),
    )

    rate_context = _context(transaction_qoq_rate=-4.161625937575611)
    _ensure_grounding(
        "거래는 4.2% 감소했습니다.",
        build_overview_input(rate_context),
    )
    integer_rate_context = _context(sales_per_transaction_qoq_rate=13.0)
    _ensure_grounding(
        "거래당 추정 매출액은 13% 증가했습니다.",
        build_overview_input(integer_rate_context),
    )
    with pytest.raises(GeminiInsightResponseError):
        _ensure_grounding(
            "거래는 4.1% 감소했습니다.",
            build_overview_input(rate_context),
        )


def test_numeric_grounding_accepts_full_korean_transaction_count_expressions():
    count_context = _context(
        transaction_count=182576,
        transaction_change_count=82520,
    )

    _ensure_grounding(
        "거래건수가 8만 2,520건 증가했고 거래건수도 18만 2,576건입니다.",
        build_overview_input(count_context),
    )


def test_numeric_grounding_rejects_ungrounded_full_korean_transaction_count():
    count_context = _context(transaction_count=82520)

    with pytest.raises(GeminiInsightResponseError):
        _ensure_grounding(
            "거래건수는 8만 2,521건입니다.",
            build_overview_input(count_context),
        )


def test_tag_is_omitted_when_candidates_are_empty():
    prompt = build_overview_input(_context(tag_candidates=[]))

    with pytest.raises(GeminiInsightResponseError):
        _ensure_grounding(
            "[40대·저녁 중심] 거래건수는 유지됐지만 거래당 추정 매출액이 16.6% 증가했습니다.",
            prompt,
        )


def test_developer_warning_is_rejected_from_user_summary():
    prompt = build_overview_input(_context())

    with pytest.raises(GeminiInsightResponseError):
        _ensure_grounding(
            "[40대·저녁 중심] 특정 시간대 비중이 높아 원천 집계 확인이 필요합니다.",
            prompt,
        )


def test_summary_keeps_120_character_limit():
    summary = "가" * 118 + "다."
    assert len(summary) == 120
    assert OverviewTakeawayInsight(summary=summary).summary == summary

    with pytest.raises(ValidationError):
        OverviewTakeawayInsight(summary=summary + "가")


def test_summary_allows_two_sentences_but_rejects_three():
    two_sentences = "매출은 16.6% 증가했습니다. 거래건수는 전분기와 같습니다."
    assert OverviewTakeawayInsight(summary=two_sentences).summary == two_sentences

    three_sentences = f"{two_sentences} 성장성은 낮습니다."
    with pytest.raises(ValidationError):
        OverviewTakeawayInsight(summary=three_sentences)


@pytest.mark.asyncio
async def test_none_interaction_is_reported_as_response_error():
    async def create_interaction(**_: Any) -> None:
        return None

    async def close_async_client() -> None:
        return None

    sdk_client = SimpleNamespace(
        aio=SimpleNamespace(
            interactions=SimpleNamespace(create=create_interaction),
            aclose=close_async_client,
        ),
        close=lambda: None,
    )
    generator = GeminiInsightGenerator(
        api_key="test-key",
        model="test-model",
        sdk_client=cast(Any, sdk_client),
        max_retries=0,
    )

    with pytest.raises(GeminiInsightResponseError, match="응답 객체"):
        await generator.generate(_context())

    await generator.aclose()
