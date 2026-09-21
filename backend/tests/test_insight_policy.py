import csv
from pathlib import Path

import pytest

from backend.app.domain.analytics.insight_policy import (
    PatternFacts,
    PatternShare,
    derive_insight_metrics,
    is_extreme_metrics,
    select_tag_candidates,
)


FIXTURE = Path(__file__).parent / "fixtures" / "gemini_insight_20262_12_pattern_test.csv"


def _float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key, "").strip()
    return float(value) if value else None


def _pattern_facts(row: dict[str, str]) -> PatternFacts:
    age_values = {
        "10대": float(row["age_10대_pct"]),
        "20대": float(row["age_20대_pct"]),
        "30대": float(row["age_30대_pct"]),
        "40대": float(row["age_40대_pct"]),
        "50대": float(row["age_50대_pct"]),
        "60대 이상": float(row["age_60대 이상_pct"]),
    }
    day_values = {
        label: float(row[f"day_{label}_pct"])
        for label in ("월", "화", "수", "목", "금", "토", "일")
    }
    time_values = {
        label: float(row[f"time_{label}_pct"])
        for label in ("새벽", "오전", "점심", "오후", "저녁", "밤")
    }
    return PatternFacts(
        age=PatternShare.from_values(
            age_values,
            display_labels={"60대 이상": "60대 이상"},
            coverage_pct=_float(row, "age_identified_sales_coverage_pct"),
        ),
        day=PatternShare.from_values(
            day_values,
            display_labels={label: f"{label}요일" for label in day_values},
        ),
        time=PatternShare.from_values(time_values),
    )


def _cases() -> list[dict[str, str]]:
    with FIXTURE.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def test_final_review_cases_select_only_representative_pattern_candidates():
    expected = {
        "1": ["30대", "목요일", "밤"],
        "6": ["저녁"],
        "16": ["20대", "저녁"],
        "17": [],
        "29": ["30대", "점심"],
        "42": ["50대", "금요일", "저녁"],
        "48": ["60대 이상", "화요일", "점심"],
        "53": [],
        "76": ["20대", "금요일", "저녁"],
        "85": ["40대", "저녁"],
        "90": ["20대", "오후"],
        "94": ["50대"],
    }

    for row in _cases():
        metrics = derive_insight_metrics(
            row,
            store_count=row["current_store_count"],
            previous_store_count=row["previous_store_count"],
        )
        candidates = select_tag_candidates(
            _pattern_facts(row),
            row["transaction_count"],
            is_extreme_metrics(metrics),
        )
        assert candidates == expected[row["sample_no"]]


def test_extreme_is_based_on_metric_magnitude_not_sample_number():
    extreme_cases = {row["sample_no"] for row in _cases() if is_extreme_metrics(
        derive_insight_metrics(
            row,
            store_count=row["current_store_count"],
            previous_store_count=row["previous_store_count"],
        )
    )}

    assert extreme_cases == {"53"}


def test_derived_metrics_preserve_missing_previous_values():
    case = next(row for row in _cases() if row["sample_no"] == "17")

    metrics = derive_insight_metrics(
        case,
        store_count=case["current_store_count"],
        previous_store_count=case["previous_store_count"],
    )

    assert metrics.current_sales == 525164
    assert metrics.transaction_count == 9
    assert metrics.previous_sales is None
    assert metrics.sales_change_amount is None
    assert metrics.transaction_qoq_rate is None
    assert metrics.store_count == 5
    assert metrics.previous_store_count == 5


def test_final_review_cases_match_csv_derived_metric_expectations():
    expected_fields = {
        "qoq_growth_rate": "qoq_growth_rate",
        "transaction_qoq_rate": "transaction_qoq_pct",
        "sales_per_transaction_current": "sales_per_transaction_current",
        "sales_per_transaction_previous": "sales_per_transaction_previous",
        "sales_per_transaction_qoq_rate": "sales_per_transaction_qoq_pct",
        "transactions_per_store_current": "transactions_per_store_current",
        "transactions_per_store_previous": "transactions_per_store_previous",
        "transactions_per_store_qoq_rate": "transactions_per_store_qoq_pct",
        "store_count_change": "store_count_change",
    }

    for row in _cases():
        metrics = derive_insight_metrics(
            row,
            store_count=row["current_store_count"],
            previous_store_count=row["previous_store_count"],
        )
        for metric_name, csv_name in expected_fields.items():
            actual = getattr(metrics, metric_name)
            expected = _float(row, csv_name)
            if expected is None:
                assert actual is None, row["sample_no"]
            else:
                assert actual == pytest.approx(expected, abs=0.02), (
                    row["sample_no"],
                    metric_name,
                )


def test_extreme_does_not_automatically_remove_strong_non_concentrated_patterns():
    patterns = PatternFacts(
        age=PatternShare("30대", 40.0, 20.0, 20.0, coverage_pct=100.0),
        day=PatternShare("금요일", 40.0, 20.0, 20.0),
        time=PatternShare("저녁", 40.0, 20.0, 20.0),
    )

    assert select_tag_candidates(patterns, 1_000, extreme=True) == [
        "30대",
        "금요일",
        "저녁",
    ]


def test_low_age_coverage_does_not_remove_independent_day_and_time_candidates():
    patterns = PatternFacts(
        age=PatternShare("60대 이상", 70.0, 10.0, 60.0, coverage_pct=1.77),
        day=PatternShare("수요일", 40.0, 20.0, 20.0),
        time=PatternShare("저녁", 40.0, 20.0, 20.0),
    )

    assert select_tag_candidates(patterns, 741, extreme=False) == ["수요일", "저녁"]


def test_final_review_cases_preserve_the_relationships_gemini_must_explain():
    expected_signs = {
        "1": (-1, 1, 1, None),
        "6": (1, -1, 1, 2),
        "16": (-1, -1, -1, 0),
        "17": (None, None, None, 0),
        "29": (1, -1, 1, 0),
        "42": (1, 1, 1, 0),
        "48": (-1, 1, 1, 0),
        "53": (1, 1, 1, 0),
        "76": (1, -1, 1, 0),
        "85": (0, 1, 1, 0),
        "90": (1, -1, 1, -1),
        "94": (1, -1, 1, -3),
    }

    for row in _cases():
        metrics = derive_insight_metrics(
            row,
            store_count=row["current_store_count"],
            previous_store_count=row["previous_store_count"],
        )
        expected_transaction_sign, expected_ticket_sign, expected_sales_sign, expected_store_change = expected_signs[row["sample_no"]]

        def sign(value: float | None) -> int | None:
            if value is None:
                return None
            return 1 if value > 0 else -1 if value < 0 else 0

        assert sign(metrics.transaction_qoq_rate) == expected_transaction_sign
        assert sign(metrics.sales_per_transaction_qoq_rate) == expected_ticket_sign
        assert sign(metrics.qoq_growth_rate) == expected_sales_sign
        if expected_store_change is not None:
            assert metrics.store_count_change == expected_store_change
