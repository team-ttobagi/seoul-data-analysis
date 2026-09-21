"""Pure policies for the backend-generated overview insight context.

The thresholds in this module are review heuristics calibrated against the
12 supplied 2026 Q2 cases. They are deliberately named constants so that
they can be re-evaluated when the source distribution changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Optional, SupportsFloat, SupportsIndex


MIN_TRANSACTIONS_FOR_TAG = 10
LOW_VOLUME_TRANSACTION_LIMIT = 100
LOW_VOLUME_MIN_SHARE_PERCENT = 50.0
LOW_VOLUME_MIN_GAP_PP = 15.0
MIN_AGE_OR_DAY_SHARE_PERCENT = 25.0
MIN_AGE_OR_DAY_GAP_PP = 5.0
MIN_TIME_SHARE_PERCENT = 30.0
MIN_TIME_GAP_PP = 4.0
MIN_AGE_IDENTIFIED_SALES_COVERAGE_PERCENT = 20.0
CONCENTRATED_PATTERN_SHARE_PERCENT = 90.0

EXTREME_SALES_GROWTH_RATE_PERCENT = 500.0
EXTREME_TRANSACTION_GROWTH_RATE_PERCENT = 300.0
EXTREME_SALES_PER_TRANSACTION_GROWTH_RATE_PERCENT = 500.0

def _as_float(value: object) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    if not isinstance(
        value,
        (str, bytes, bytearray, SupportsFloat, SupportsIndex),
    ):
        return None
    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if isfinite(converted) else None


def _first_value(row: Mapping[str, object], *names: str) -> object:
    for name in names:
        if name in row:
            return row[name]
    return None


def _rate(current: Optional[float], previous: Optional[float]) -> Optional[float]:
    if current is None or previous is None or previous <= 0:
        return None
    return (current - previous) / previous * 100


@dataclass(frozen=True)
class InsightMetrics:
    current_sales: Optional[float]
    previous_sales: Optional[float]
    transaction_count: Optional[float]
    previous_transaction_count: Optional[float]
    sales_change_amount: Optional[float]
    transaction_change_count: Optional[float]
    qoq_growth_rate: Optional[float]
    transaction_qoq_rate: Optional[float]
    sales_per_transaction_current: Optional[float]
    sales_per_transaction_previous: Optional[float]
    sales_per_transaction_qoq_rate: Optional[float]
    transactions_per_store_current: Optional[float]
    transactions_per_store_previous: Optional[float]
    transactions_per_store_qoq_rate: Optional[float]
    store_count: Optional[float]
    previous_store_count: Optional[float]
    store_count_change: Optional[float]


@dataclass(frozen=True)
class PatternShare:
    top_label: str
    top_share: float
    second_share: float
    gap_pp: float
    source_valid: bool = True
    coverage_pct: Optional[float] = None

    @classmethod
    def from_values(
        cls,
        values: Mapping[str, object],
        *,
        display_labels: Optional[Mapping[str, str]] = None,
        coverage_pct: Optional[float] = None,
    ) -> "PatternShare":
        normalized = [
            (label, _as_float(value)) for label, value in values.items()
        ]
        source_valid = bool(normalized) and all(
            value is not None and value >= 0 for _, value in normalized
        )
        if not source_valid:
            return cls(
                top_label="",
                top_share=0.0,
                second_share=0.0,
                gap_pp=0.0,
                source_valid=False,
                coverage_pct=coverage_pct,
            )

        ranked = sorted(normalized, key=lambda item: item[1] or 0.0, reverse=True)
        top_label, top_share = ranked[0]
        second_share = ranked[1][1] if len(ranked) > 1 else 0.0
        assert top_share is not None
        assert second_share is not None
        labels = display_labels or {}
        return cls(
            top_label=labels.get(top_label, top_label),
            top_share=top_share,
            second_share=second_share,
            gap_pp=top_share - second_share,
            source_valid=sum(value or 0.0 for _, value in normalized) > 0,
            coverage_pct=coverage_pct,
        )


@dataclass(frozen=True)
class PatternFacts:
    age: Optional[PatternShare]
    day: Optional[PatternShare]
    time: Optional[PatternShare]


def derive_insight_metrics(
    row: Mapping[str, object],
    store_count: object = None,
    previous_store_count: object = None,
) -> InsightMetrics:
    current_sales = _as_float(_first_value(row, "current_sales", "sales"))
    previous_sales = _as_float(_first_value(row, "previous_sales", "prev_sales"))
    transaction_count = _as_float(row.get("transaction_count"))
    previous_transaction_count = _as_float(
        _first_value(row, "previous_transaction_count", "prev_transaction_count")
    )
    current_store_count = _as_float(store_count)
    prior_store_count = _as_float(previous_store_count)

    sales_per_transaction_current = (
        current_sales / transaction_count
        if current_sales is not None and transaction_count is not None and transaction_count > 0
        else None
    )
    sales_per_transaction_previous = (
        previous_sales / previous_transaction_count
        if previous_sales is not None
        and previous_transaction_count is not None
        and previous_transaction_count > 0
        else None
    )
    transactions_per_store_current = (
        transaction_count / current_store_count
        if transaction_count is not None and current_store_count is not None and current_store_count > 0
        else None
    )
    transactions_per_store_previous = (
        previous_transaction_count / prior_store_count
        if previous_transaction_count is not None
        and prior_store_count is not None
        and prior_store_count > 0
        else None
    )

    return InsightMetrics(
        current_sales=current_sales,
        previous_sales=previous_sales,
        transaction_count=transaction_count,
        previous_transaction_count=previous_transaction_count,
        sales_change_amount=(
            current_sales - previous_sales
            if current_sales is not None and previous_sales is not None
            else None
        ),
        transaction_change_count=(
            transaction_count - previous_transaction_count
            if transaction_count is not None and previous_transaction_count is not None
            else None
        ),
        qoq_growth_rate=_rate(current_sales, previous_sales),
        transaction_qoq_rate=_rate(transaction_count, previous_transaction_count),
        sales_per_transaction_current=sales_per_transaction_current,
        sales_per_transaction_previous=sales_per_transaction_previous,
        sales_per_transaction_qoq_rate=_rate(
            sales_per_transaction_current, sales_per_transaction_previous
        ),
        transactions_per_store_current=transactions_per_store_current,
        transactions_per_store_previous=transactions_per_store_previous,
        transactions_per_store_qoq_rate=_rate(
            transactions_per_store_current, transactions_per_store_previous
        ),
        store_count=current_store_count,
        previous_store_count=prior_store_count,
        store_count_change=(
            current_store_count - prior_store_count
            if current_store_count is not None and prior_store_count is not None
            else None
        ),
    )


def is_extreme_metrics(metrics: InsightMetrics) -> bool:
    rates = (
        (metrics.qoq_growth_rate, EXTREME_SALES_GROWTH_RATE_PERCENT),
        (metrics.transaction_qoq_rate, EXTREME_TRANSACTION_GROWTH_RATE_PERCENT),
        (
            metrics.sales_per_transaction_qoq_rate,
            EXTREME_SALES_PER_TRANSACTION_GROWTH_RATE_PERCENT,
        ),
    )
    return any(
        rate is not None and abs(rate) >= threshold
        for rate, threshold in rates
    )


def _is_representative(
    pattern: PatternShare,
    *,
    min_share: float,
    min_gap: float,
    extreme: bool,
) -> bool:
    if not pattern.source_valid:
        return False
    if extreme and pattern.top_share >= CONCENTRATED_PATTERN_SHARE_PERCENT:
        return False
    return pattern.top_share >= min_share and pattern.gap_pp >= min_gap


def select_tag_candidates(
    patterns: PatternFacts,
    transaction_count: object,
    extreme: bool,
) -> list[str]:
    count = _as_float(transaction_count)
    if count is None or count < MIN_TRANSACTIONS_FOR_TAG:
        return []

    if count < LOW_VOLUME_TRANSACTION_LIMIT:
        min_share = LOW_VOLUME_MIN_SHARE_PERCENT
        min_gap = LOW_VOLUME_MIN_GAP_PP
    else:
        min_share = None
        min_gap = None

    candidates: list[str] = []
    if patterns.age is not None:
        age_min_share = min_share or MIN_AGE_OR_DAY_SHARE_PERCENT
        age_min_gap = min_gap or MIN_AGE_OR_DAY_GAP_PP
        coverage = patterns.age.coverage_pct
        if (
            coverage is not None
            and coverage >= MIN_AGE_IDENTIFIED_SALES_COVERAGE_PERCENT
            and _is_representative(
                patterns.age,
                min_share=age_min_share,
                min_gap=age_min_gap,
                extreme=extreme,
            )
        ):
            candidates.append(patterns.age.top_label)

    if patterns.day is not None:
        day_min_share = min_share or MIN_AGE_OR_DAY_SHARE_PERCENT
        day_min_gap = min_gap or MIN_AGE_OR_DAY_GAP_PP
        if _is_representative(
            patterns.day,
            min_share=day_min_share,
            min_gap=day_min_gap,
            extreme=extreme,
        ):
            candidates.append(patterns.day.top_label)

    if patterns.time is not None:
        time_min_share = min_share or MIN_TIME_SHARE_PERCENT
        time_min_gap = min_gap or MIN_TIME_GAP_PP
        if _is_representative(
            patterns.time,
            min_share=time_min_share,
            min_gap=time_min_gap,
            extreme=extreme,
        ):
            candidates.append(patterns.time.top_label)

    return candidates
