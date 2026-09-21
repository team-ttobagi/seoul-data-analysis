import pytest

from backend.app.domain.analytics.insight_policy import (
    PatternFacts,
    PatternShare,
    derive_insight_metrics,
    is_extreme_metrics,
    select_tag_candidates,
)


CASE_ROWS: list[dict[str, object]] = [
    {
        "sample_no": "1",
        "sales": 547354073,
        "prev_sales": 426572331,
        "transaction_count": 4734,
        "prev_transaction_count": 5132,
        "current_store_count": 26,
        "previous_store_count": 27,
        "patterns": {
            "age": {
                "10대": 0.57,
                "20대": 18.6,
                "30대": 29.23,
                "40대": 20.68,
                "50대": 17.28,
                "60대 이상": 13.64,
            },
            "day": {
                "월": 6.05,
                "화": 7.43,
                "수": 11.04,
                "목": 29.14,
                "금": 10.5,
                "토": 22.61,
                "일": 13.22,
            },
            "time": {
                "새벽": 13.62,
                "오전": 3.1,
                "점심": 9.56,
                "오후": 14.38,
                "저녁": 21.02,
                "밤": 38.32,
            },
            "age_identified_sales_coverage_pct": 57.05,
        },
        "expected_metrics": {
            "qoq_growth_rate": 28.3144810908985,
            "transaction_qoq_rate": -7.76,
            "sales_per_transaction_current": 115621.90,
            "sales_per_transaction_previous": 83120.10,
            "sales_per_transaction_qoq_rate": 39.10,
            "transactions_per_store_current": 182.08,
            "transactions_per_store_previous": 190.07,
            "transactions_per_store_qoq_rate": -4.21,
            "store_count_change": -1,
        },
    },
    {
        "sample_no": "6",
        "sales": 510280686,
        "prev_sales": 413054294,
        "transaction_count": 47215,
        "prev_transaction_count": 37339,
        "current_store_count": 16,
        "previous_store_count": 14,
        "patterns": {
            "age": {
                "10대": 0.41,
                "20대": 8.87,
                "30대": 23.34,
                "40대": 20.32,
                "50대": 22.19,
                "60대 이상": 24.87,
            },
            "day": {
                "월": 15.74,
                "화": 13.71,
                "수": 15.24,
                "목": 14.54,
                "금": 15.72,
                "토": 15.33,
                "일": 9.72,
            },
            "time": {
                "새벽": 0.02,
                "오전": 19.3,
                "점심": 23.13,
                "오후": 19.3,
                "저녁": 30.02,
                "밤": 8.24,
            },
            "age_identified_sales_coverage_pct": 91.58,
        },
        "expected_metrics": {
            "qoq_growth_rate": 23.5384048567717,
            "transaction_qoq_rate": 26.45,
            "sales_per_transaction_current": 10807.60,
            "sales_per_transaction_previous": 11062.28,
            "sales_per_transaction_qoq_rate": -2.30,
            "transactions_per_store_current": 2950.94,
            "transactions_per_store_previous": 2667.07,
            "transactions_per_store_qoq_rate": 10.64,
            "store_count_change": 2,
        },
    },
    {
        "sample_no": "16",
        "sales": 57886664,
        "prev_sales": 73559142,
        "transaction_count": 9820,
        "prev_transaction_count": 12286,
        "current_store_count": 4,
        "previous_store_count": 4,
        "patterns": {
            "age": {
                "10대": 0.98,
                "20대": 46.79,
                "30대": 27.62,
                "40대": 16.05,
                "50대": 7.56,
                "60대 이상": 0.99,
            },
            "day": {
                "월": 11.08,
                "화": 11.87,
                "수": 12.14,
                "목": 11.13,
                "금": 13.62,
                "토": 20.55,
                "일": 19.62,
            },
            "time": {
                "새벽": 13.86,
                "오전": 7.66,
                "점심": 9.77,
                "오후": 17.62,
                "저녁": 33.28,
                "밤": 17.81,
            },
            "age_identified_sales_coverage_pct": 100.0,
        },
        "expected_metrics": {
            "qoq_growth_rate": -21.3059554174789,
            "transaction_qoq_rate": -20.07,
            "sales_per_transaction_current": 5894.77,
            "sales_per_transaction_previous": 5987.23,
            "sales_per_transaction_qoq_rate": -1.54,
            "transactions_per_store_current": 2455.00,
            "transactions_per_store_previous": 3071.50,
            "transactions_per_store_qoq_rate": -20.07,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "17",
        "sales": 525164,
        "prev_sales": None,
        "transaction_count": 9,
        "prev_transaction_count": None,
        "current_store_count": 5,
        "previous_store_count": 5,
        "patterns": {
            "age": {
                "10대": 0.0,
                "20대": 0.0,
                "30대": 0.0,
                "40대": 0.0,
                "50대": 100.0,
                "60대 이상": 0.0,
            },
            "day": {
                "월": 0.0,
                "화": 0.0,
                "수": 0.0,
                "목": 0.0,
                "금": 0.0,
                "토": 100.0,
                "일": 0.0,
            },
            "time": {
                "새벽": 0.0,
                "오전": 0.0,
                "점심": 0.0,
                "오후": 100.0,
                "저녁": 0.0,
                "밤": 0.0,
            },
            "age_identified_sales_coverage_pct": 100.0,
        },
        "expected_metrics": {
            "qoq_growth_rate": None,
            "transaction_qoq_rate": None,
            "sales_per_transaction_current": 58351.56,
            "sales_per_transaction_previous": None,
            "sales_per_transaction_qoq_rate": None,
            "transactions_per_store_current": 1.80,
            "transactions_per_store_previous": None,
            "transactions_per_store_qoq_rate": None,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "29",
        "sales": 486006147,
        "prev_sales": 484492258,
        "transaction_count": 55441,
        "prev_transaction_count": 53867,
        "current_store_count": 17,
        "previous_store_count": 17,
        "patterns": {
            "age": {
                "10대": 0.02,
                "20대": 8.37,
                "30대": 33.32,
                "40대": 24.74,
                "50대": 16.56,
                "60대 이상": 16.99,
            },
            "day": {
                "월": 14.23,
                "화": 16.9,
                "수": 16.59,
                "목": 16.77,
                "금": 18.73,
                "토": 10.39,
                "일": 6.38,
            },
            "time": {
                "새벽": 0.37,
                "오전": 24.53,
                "점심": 46.1,
                "오후": 18.03,
                "저녁": 10.07,
                "밤": 0.9,
            },
            "age_identified_sales_coverage_pct": 86.14,
        },
        "expected_metrics": {
            "qoq_growth_rate": 0.3124691829441,
            "transaction_qoq_rate": 2.92,
            "sales_per_transaction_current": 8766.19,
            "sales_per_transaction_previous": 8994.23,
            "sales_per_transaction_qoq_rate": -2.54,
            "transactions_per_store_current": 3261.24,
            "transactions_per_store_previous": 3168.65,
            "transactions_per_store_qoq_rate": 2.92,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "42",
        "sales": 642882257,
        "prev_sales": 517075089,
        "transaction_count": 15185,
        "prev_transaction_count": 14814,
        "current_store_count": 5,
        "previous_store_count": 5,
        "patterns": {
            "age": {
                "10대": 0.0,
                "20대": 17.44,
                "30대": 18.93,
                "40대": 12.05,
                "50대": 29.58,
                "60대 이상": 21.99,
            },
            "day": {
                "월": 24.63,
                "화": 11.13,
                "수": 2.09,
                "목": 9.08,
                "금": 40.63,
                "토": 12.44,
                "일": 0.0,
            },
            "time": {
                "새벽": 11.28,
                "오전": 8.52,
                "점심": 16.97,
                "오후": 19.96,
                "저녁": 43.27,
                "밤": 0.0,
            },
            "age_identified_sales_coverage_pct": 94.62,
        },
        "expected_metrics": {
            "qoq_growth_rate": 24.3305412843046,
            "transaction_qoq_rate": 2.50,
            "sales_per_transaction_current": 42336.66,
            "sales_per_transaction_previous": 34904.49,
            "sales_per_transaction_qoq_rate": 21.29,
            "transactions_per_store_current": 3037.00,
            "transactions_per_store_previous": 2962.80,
            "transactions_per_store_qoq_rate": 2.50,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "48",
        "sales": 183872540,
        "prev_sales": 169849153,
        "transaction_count": 3961,
        "prev_transaction_count": 4133,
        "current_store_count": 6,
        "previous_store_count": 6,
        "patterns": {
            "age": {
                "10대": 0.0,
                "20대": 2.09,
                "30대": 2.09,
                "40대": 14.58,
                "50대": 35.48,
                "60대 이상": 45.77,
            },
            "day": {
                "월": 4.22,
                "화": 41.9,
                "수": 22.68,
                "목": 9.68,
                "금": 15.06,
                "토": 3.75,
                "일": 2.71,
            },
            "time": {
                "새벽": 0.0,
                "오전": 8.5,
                "점심": 71.28,
                "오후": 13.15,
                "저녁": 7.07,
                "밤": 0.0,
            },
            "age_identified_sales_coverage_pct": 59.38,
        },
        "expected_metrics": {
            "qoq_growth_rate": 8.2563773514961,
            "transaction_qoq_rate": -4.16,
            "sales_per_transaction_current": 46420.74,
            "sales_per_transaction_previous": 41095.85,
            "sales_per_transaction_qoq_rate": 12.96,
            "transactions_per_store_current": 660.17,
            "transactions_per_store_previous": 688.83,
            "transactions_per_store_qoq_rate": -4.16,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "53",
        "sales": 196567593,
        "prev_sales": 2348993,
        "transaction_count": 741,
        "prev_transaction_count": 480,
        "current_store_count": 3,
        "previous_store_count": 3,
        "patterns": {
            "age": {
                "10대": 0.0,
                "20대": 0.0,
                "30대": 2.76,
                "40대": 2.5,
                "50대": 0.0,
                "60대 이상": 94.74,
            },
            "day": {
                "월": 48.2,
                "화": 0.0,
                "수": 51.4,
                "목": 0.4,
                "금": 0.0,
                "토": 0.0,
                "일": 0.0,
            },
            "time": {
                "새벽": 0.0,
                "오전": 1.14,
                "점심": 0.54,
                "오후": 0.05,
                "저녁": 98.28,
                "밤": 0.0,
            },
            "age_identified_sales_coverage_pct": 1.77,
        },
        "expected_metrics": {
            "qoq_growth_rate": 8268.1642729459,
            "transaction_qoq_rate": 54.38,
            "sales_per_transaction_current": 265273.40,
            "sales_per_transaction_previous": 4893.74,
            "sales_per_transaction_qoq_rate": 5320.67,
            "transactions_per_store_current": 247.00,
            "transactions_per_store_previous": 160.00,
            "transactions_per_store_qoq_rate": 54.38,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "76",
        "sales": 249170586,
        "prev_sales": 207314283,
        "transaction_count": 9263,
        "prev_transaction_count": 6018,
        "current_store_count": 10,
        "previous_store_count": 10,
        "patterns": {
            "age": {
                "10대": 3.12,
                "20대": 32.29,
                "30대": 23.41,
                "40대": 16.7,
                "50대": 19.02,
                "60대 이상": 5.46,
            },
            "day": {
                "월": 10.98,
                "화": 9.43,
                "수": 7.76,
                "목": 15.93,
                "금": 34.22,
                "토": 15.09,
                "일": 6.59,
            },
            "time": {
                "새벽": 0.29,
                "오전": 7.19,
                "점심": 16.62,
                "오후": 23.52,
                "저녁": 37.22,
                "밤": 15.17,
            },
            "age_identified_sales_coverage_pct": 100.0,
        },
        "expected_metrics": {
            "qoq_growth_rate": 20.1897825824186,
            "transaction_qoq_rate": 53.92,
            "sales_per_transaction_current": 26899.56,
            "sales_per_transaction_previous": 34449.03,
            "sales_per_transaction_qoq_rate": -21.91,
            "transactions_per_store_current": 926.30,
            "transactions_per_store_previous": 601.80,
            "transactions_per_store_qoq_rate": 53.92,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "85",
        "sales": 3271104,
        "prev_sales": 2805601,
        "transaction_count": 76,
        "prev_transaction_count": 76,
        "current_store_count": 8,
        "previous_store_count": 8,
        "patterns": {
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
        },
        "expected_metrics": {
            "qoq_growth_rate": 16.5919173824075,
            "transaction_qoq_rate": 0.0,
            "sales_per_transaction_current": 43040.84,
            "sales_per_transaction_previous": 36915.80,
            "sales_per_transaction_qoq_rate": 16.59,
            "transactions_per_store_current": 9.50,
            "transactions_per_store_previous": 9.50,
            "transactions_per_store_qoq_rate": 0.0,
            "store_count_change": 0,
        },
    },
    {
        "sample_no": "90",
        "sales": 7286103096,
        "prev_sales": 6756123285,
        "transaction_count": 757653,
        "prev_transaction_count": 674100,
        "current_store_count": 206,
        "previous_store_count": 207,
        "patterns": {
            "age": {
                "10대": 1.95,
                "20대": 39.29,
                "30대": 30.74,
                "40대": 13.11,
                "50대": 10.64,
                "60대 이상": 4.27,
            },
            "day": {
                "월": 10.33,
                "화": 12.87,
                "수": 11.38,
                "목": 12.42,
                "금": 16.06,
                "토": 20.44,
                "일": 16.5,
            },
            "time": {
                "새벽": 0.15,
                "오전": 6.93,
                "점심": 25.45,
                "오후": 33.54,
                "저녁": 29.2,
                "밤": 4.74,
            },
            "age_identified_sales_coverage_pct": 92.52,
        },
        "expected_metrics": {
            "qoq_growth_rate": 7.8444366487016,
            "transaction_qoq_rate": 12.39,
            "sales_per_transaction_current": 9616.68,
            "sales_per_transaction_previous": 10022.43,
            "sales_per_transaction_qoq_rate": -4.05,
            "transactions_per_store_current": 3677.93,
            "transactions_per_store_previous": 3256.52,
            "transactions_per_store_qoq_rate": 12.94,
            "store_count_change": -1,
        },
    },
    {
        "sample_no": "94",
        "sales": 1044625977,
        "prev_sales": 986084087,
        "transaction_count": 4676,
        "prev_transaction_count": 4363,
        "current_store_count": 74,
        "previous_store_count": 77,
        "patterns": {
            "age": {
                "10대": 0.0,
                "20대": 1.74,
                "30대": 15.08,
                "40대": 21.34,
                "50대": 44.83,
                "60대 이상": 17.01,
            },
            "day": {
                "월": 11.21,
                "화": 20.46,
                "수": 13.63,
                "목": 12.56,
                "금": 15.08,
                "토": 14.83,
                "일": 12.24,
            },
            "time": {
                "새벽": 34.83,
                "오전": 5.91,
                "점심": 2.75,
                "오후": 5.13,
                "저녁": 18.68,
                "밤": 32.69,
            },
            "age_identified_sales_coverage_pct": 77.96,
        },
        "expected_metrics": {
            "qoq_growth_rate": 5.9368050627512,
            "transaction_qoq_rate": 7.17,
            "sales_per_transaction_current": 223401.62,
            "sales_per_transaction_previous": 226010.56,
            "sales_per_transaction_qoq_rate": -1.15,
            "transactions_per_store_current": 63.19,
            "transactions_per_store_previous": 56.66,
            "transactions_per_store_qoq_rate": 11.52,
            "store_count_change": -3,
        },
    },
]


def _pattern_facts(row: dict[str, object]) -> PatternFacts:
    patterns = row["patterns"]
    assert isinstance(patterns, dict)
    age_values = {
        label: float(patterns["age"][label])
        for label in ("10대", "20대", "30대", "40대", "50대", "60대 이상")
    }
    day_values = {
        label: float(patterns["day"][label])
        for label in ("월", "화", "수", "목", "금", "토", "일")
    }
    time_values = {
        label: float(patterns["time"][label])
        for label in ("새벽", "오전", "점심", "오후", "저녁", "밤")
    }
    return PatternFacts(
        age=PatternShare.from_values(
            age_values,
            display_labels={"60대 이상": "60대 이상"},
            coverage_pct=float(patterns["age_identified_sales_coverage_pct"]),
        ),
        day=PatternShare.from_values(
            day_values,
            display_labels={label: f"{label}요일" for label in day_values},
        ),
        time=PatternShare.from_values(time_values),
    )


def _cases() -> list[dict[str, object]]:
    return CASE_ROWS


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


def test_final_review_cases_match_expected_derived_metrics():
    expected_fields = (
        "qoq_growth_rate",
        "transaction_qoq_rate",
        "sales_per_transaction_current",
        "sales_per_transaction_previous",
        "sales_per_transaction_qoq_rate",
        "transactions_per_store_current",
        "transactions_per_store_previous",
        "transactions_per_store_qoq_rate",
        "store_count_change",
    )

    for row in _cases():
        metrics = derive_insight_metrics(
            row,
            store_count=row["current_store_count"],
            previous_store_count=row["previous_store_count"],
        )
        expected_metrics = row["expected_metrics"]
        assert isinstance(expected_metrics, dict)
        for metric_name in expected_fields:
            actual = getattr(metrics, metric_name)
            expected = expected_metrics[metric_name]
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
