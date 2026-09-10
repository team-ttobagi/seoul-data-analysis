"""Score calculation pipeline shared by the sales and analytics domains.

Implements the formulas from docs/상권 분석 지표 산출 정의서.md section 4-5 and 12.
Pure functions only — no DB access. Input is raw per-trade-area rows fetched by
SalesRepository.get_metrics_rows()/get_diversity_rows(); output is a scored
pandas.DataFrame. SalesRepository.get_metrics_dataframe() is the single entry
point both SalesRepository (/sales/summary) and AnalyticsService (overview/
competition/compare/recommendations) call, so every endpoint sees the same
computed numbers for the same quarter+industry+trade_area.
"""

from typing import Iterable, List, Optional

import numpy as np
import pandas as pd

BENCHMARK_PERCENTILE_COLUMNS = [
    "sales_percentile",
    "growth_percentile",
    "volume_percentile",
    "competition_percentile",
]


def safe_minmax(series: pd.Series, neutral: float = 0.5) -> pd.Series:
    """0~1 Min-Max normalization. All-equal or single-value series get `neutral`."""
    valid = series.dropna()

    if valid.empty:
        return pd.Series(np.nan, index=series.index)

    min_value = valid.min()
    max_value = valid.max()

    if min_value == max_value:
        result = pd.Series(neutral, index=series.index, dtype=float)
        result[series.isna()] = np.nan
        return result

    return (series - min_value) / (max_value - min_value)


def growth_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.4 — P5~P95 Winsorize 후 0~100 Min-Max."""
    valid = series.dropna()

    if valid.empty:
        return pd.Series(np.nan, index=series.index)

    p5 = valid.quantile(0.05)
    p95 = valid.quantile(0.95)

    if p5 == p95:
        result = pd.Series(50.0, index=series.index)
        result[series.isna()] = np.nan
        return result

    clipped = series.clip(lower=p5, upper=p95)
    return ((clipped - p5) / (p95 - p5) * 100).clip(0, 100)


def transaction_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.5 — log1p 변환 후 0~100 Min-Max."""
    log_values = np.log1p(series.clip(lower=0))
    return safe_minmax(log_values) * 100


def ticket_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.6.1 — 객단가 Min-Max."""
    return safe_minmax(series) * 100


def growth_balance_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.6.2 — GrowthPressure가 높을수록 낮은 점수가 되도록 역정규화."""
    normalized = safe_minmax(series)
    return (1 - normalized) * 100


def calculate_hhi(raw_df: pd.DataFrame, value_col: str = "sales") -> pd.DataFrame:
    """산출 정의서 4.6.3 — 상권 전체 업종별 매출 비중으로 HHI와 Diversity(1-HHI) 계산."""
    if raw_df.empty:
        return pd.DataFrame(columns=["trdar_cd", "hhi", "diversity"])

    industry_sales = raw_df.groupby(
        ["trdar_cd", "svc_induty_cd"], as_index=False
    ).agg(industry_sales=(value_col, "sum"))

    industry_sales["total_area_sales"] = industry_sales.groupby("trdar_cd")[
        "industry_sales"
    ].transform("sum")

    industry_sales["share"] = np.where(
        industry_sales["total_area_sales"] > 0,
        industry_sales["industry_sales"] / industry_sales["total_area_sales"],
        np.nan,
    )
    industry_sales["share_sq"] = industry_sales["share"] ** 2

    hhi = industry_sales.groupby("trdar_cd", as_index=False).agg(hhi=("share_sq", "sum"))
    hhi["diversity"] = 1 - hhi["hhi"]
    return hhi


def demand_diversity_score(diversity: pd.Series) -> pd.Series:
    """산출 정의서 4.6.3 — 동일 분기 상권들의 Diversity를 0~100 Min-Max."""
    return safe_minmax(diversity) * 100


def competition_score(ticket: pd.Series, growth_balance: pd.Series, diversity: pd.Series) -> pd.Series:
    """산출 정의서 4.6 — Ticket 50% + GrowthBalance 30% + Diversity 20%."""
    return ticket * 0.50 + growth_balance * 0.30 + diversity * 0.20


def exploration_score(growth: pd.Series, transaction: pd.Series, competition: pd.Series) -> pd.Series:
    """산출 정의서 4.7 — Growth 40% + Transaction 35% + Competition 25%."""
    return growth * 0.40 + transaction * 0.35 + competition * 0.25


def percentile_and_rank(df: pd.DataFrame, value_col: str, prefix: str) -> pd.DataFrame:
    """산출 정의서 5장 — 값이 높을수록 낮은(=상위) percentile이 되도록 순위/percentile 계산."""
    result = df.copy()
    result[f"{prefix}_rank"] = result[value_col].rank(method="min", ascending=False)
    result[f"{prefix}_percentile"] = (
        result[value_col].rank(method="min", pct=True, ascending=False) * 100
    )
    return result


def seoul_rank(df: pd.DataFrame, percentile_cols: List[str] = BENCHMARK_PERCENTILE_COLUMNS) -> pd.DataFrame:
    """산출 정의서 5.5 — 4개 Benchmark Percentile 평균 기반 종합 순위."""
    result = df.copy()
    result["overall_benchmark_percentile"] = result[percentile_cols].mean(axis=1, skipna=False)
    result["seoul_rank"] = result["overall_benchmark_percentile"].rank(method="min", ascending=True)
    return result


def grade_from_score(score: Optional[float]) -> Optional[str]:
    """산출 정의서 7.1 — 70 이상 높음 / 40~70 보통 / 40 미만 낮음."""
    if score is None or pd.isna(score):
        return None
    if score >= 70:
        return "높음"
    if score >= 40:
        return "보통"
    return "낮음"


def none_if_nan(value):
    """NaN/None -> None, so callers can distinguish '산출 불가' from an actual 0."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return value


def none_if_nan_round(value) -> Optional[int]:
    value = none_if_nan(value)
    return None if value is None else round(value)


def signal_from_score(score: Optional[float]) -> Optional[str]:
    """산출 정의서 7.1 — signals.* 필드용 영문 등급."""
    if score is None or pd.isna(score):
        return None
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def build_metrics_dataframe(rows: List[dict], diversity_rows: Iterable[dict]) -> pd.DataFrame:
    """동일 분기+업종 population에 대한 전체 점수 파이프라인 (산출 정의서 12장)."""
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["growth_rate"] = np.where(
        df["prev_sales"].notna() & (df["prev_sales"] > 0),
        (df["sales"] - df["prev_sales"]) / df["prev_sales"] * 100,
        np.nan,
    )
    df["transaction_growth"] = np.where(
        df["prev_transaction_count"].notna() & (df["prev_transaction_count"] > 0),
        (df["transaction_count"] - df["prev_transaction_count"])
        / df["prev_transaction_count"]
        * 100,
        np.nan,
    )
    df["avg_ticket"] = np.where(
        df["transaction_count"] > 0, df["sales"] / df["transaction_count"], np.nan
    )
    df["growth_pressure"] = df["transaction_growth"] - df["growth_rate"]

    df["growth_score"] = growth_score(df["growth_rate"])
    df["transaction_score"] = transaction_score(df["transaction_count"])
    df["ticket_score"] = ticket_score(df["avg_ticket"])
    df["growth_balance_score"] = growth_balance_score(df["growth_pressure"])

    diversity_df = calculate_hhi(pd.DataFrame(diversity_rows))
    if not diversity_df.empty:
        diversity_df["demand_diversity_score"] = demand_diversity_score(diversity_df["diversity"])
        df = df.merge(
            diversity_df[["trdar_cd", "diversity", "demand_diversity_score"]],
            on="trdar_cd",
            how="left",
        )
    else:
        df["diversity"] = np.nan
        df["demand_diversity_score"] = np.nan

    df["competition_score"] = competition_score(
        df["ticket_score"], df["growth_balance_score"], df["demand_diversity_score"]
    )
    df["exploration_score"] = exploration_score(
        df["growth_score"], df["transaction_score"], df["competition_score"]
    )

    df = percentile_and_rank(df, "sales", "sales")
    df = percentile_and_rank(df, "transaction_count", "volume")
    df = percentile_and_rank(df, "growth_rate", "growth")
    df = percentile_and_rank(df, "competition_score", "competition")
    df = seoul_rank(df)
    df = percentile_and_rank(df, "exploration_score", "exploration")

    return df
