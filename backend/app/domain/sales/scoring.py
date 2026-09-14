"""매출 도메인과 분석 도메인이 공유하는 점수 계산 파이프라인이다.

`docs/상권 분석 지표 산출 정의서.md` 4~5장과 12장의 산식을 구현한다.
DB에 접근하지 않는 순수 함수로만 구성하며, 입력은 하나의 업종에 대한 현재 분기별
상권 행이다. 입력 행에는 점포 수와 폐업률을 결합한 값이 포함된다.
`SalesRepository.get_metrics_dataframe()`을 `/sales/summary`와 모든 analytics 점수
사용 경로가 공통으로 호출하므로 모든 API에서 CompetitionScore가 동일하게 계산된다.
"""

from typing import List, Optional

import numpy as np
import pandas as pd

BENCHMARK_PERCENTILE_COLUMNS = [
    "sales_percentile",
    "growth_percentile",
    "volume_percentile",
    "competition_percentile",
]


def safe_minmax(series: pd.Series, neutral: float = 0.5) -> pd.Series:
    """0~1 Min-Max 정규화. 모든 값이 같거나 값이 하나면 `neutral`을 사용한다."""
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
    """산출 정의서 4.4 — P5~P95 윈저라이즈 후 0~100 Min-Max."""
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
    """산출 정의서 4.5 — log1p 변환 후 0~100 Min-Max 정규화."""
    log_values = np.log1p(series.clip(lower=0))
    return safe_minmax(log_values) * 100


def store_count_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.6.1 — 점포 수를 역 Min-Max하여 적을수록 높게 평가한다."""
    return (1 - safe_minmax(series)) * 100


def demand_per_store_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.6.2 — 점포당 거래건수를 정 Min-Max하여 높을수록 높게 평가한다."""
    return safe_minmax(series) * 100


def closing_rate_score(series: pd.Series) -> pd.Series:
    """산출 정의서 4.6.3 — 폐업률을 역 Min-Max하여 낮을수록 높게 평가한다."""
    return (1 - safe_minmax(series)) * 100


def competition_score(
    store_count: pd.Series,
    demand_per_store: pd.Series,
    closing_rate: pd.Series,
) -> pd.Series:
    """산출 정의서 4.6 — 점포 수 50% + 점포당 수요 30% + 폐업률 20%.

    구성요소 중 하나라도 NaN이면 pandas 연산을 통해 결과에도 NaN이 전파된다.
    이를 통해 산출 불가 데이터를 실제 0점으로 잘못 해석하지 않는다.
    """
    return store_count * 0.50 + demand_per_store * 0.30 + closing_rate * 0.20


def exploration_score(growth: pd.Series, transaction: pd.Series, competition: pd.Series) -> pd.Series:
    """산출 정의서 4.7 — 성장성 40% + 거래 활성도 35% + 경쟁 여건 25%."""
    return growth * 0.40 + transaction * 0.35 + competition * 0.25


def percentile_and_rank(df: pd.DataFrame, value_col: str, prefix: str) -> pd.DataFrame:
    """산출 정의서 5장 — 값이 높을수록 낮은(=상위) 백분위가 되도록 순위와 백분위를 계산한다."""
    result = df.copy()
    result[f"{prefix}_rank"] = result[value_col].rank(method="min", ascending=False)
    result[f"{prefix}_percentile"] = (
        result[value_col].rank(method="min", pct=True, ascending=False) * 100
    )
    return result


def seoul_rank(df: pd.DataFrame, percentile_cols: List[str] = BENCHMARK_PERCENTILE_COLUMNS) -> pd.DataFrame:
    """산출 정의서 5.5 — 4개 벤치마크 백분위 평균 기반 종합 순위."""
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
    """NaN/None을 None으로 변환해 산출 불가와 실제 0을 구분한다."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return value


def none_if_nan_round(value) -> Optional[int]:
    value = none_if_nan(value)
    return None if value is None else round(value)


def signal_from_score(score: Optional[float]) -> Optional[str]:
    """산출 정의서 7.1 — signals.* 필드에 사용할 영문 등급."""
    if score is None or pd.isna(score):
        return None
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def build_metrics_dataframe(rows: List[dict]) -> pd.DataFrame:
    """동일 분기·업종 상권 비교 집단의 전체 점수 파이프라인을 실행한다.

    ``store_count``는 저장소 조인으로 가져온 ``store_data.similr_induty_stor_co``이고,
    ``closing_rate``는 ``store_data.clsbiz_rt``이다. 점포 행이나 폐업률이 없거나
    점포 수가 0 이하이면 CompetitionScore와 ExplorationScore까지 NaN을 유지한다.
    """
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    # SQL NULL과 숫자로 변환할 수 없는 값은 0으로 바꾸지 않고 산출 불가로 유지한다.
    # 0으로 바꾸면 Min-Max 정규화의 유효한 최솟값으로 잘못 포함될 수 있다.
    numeric_columns = [
        "sales",
        "transaction_count",
        "prev_sales",
        "prev_transaction_count",
        "store_count",
        "closing_rate",
    ]
    for column in numeric_columns:
        if column not in df:
            df[column] = np.nan
        df[column] = pd.to_numeric(df[column], errors="coerce")

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
    df["growth_score"] = growth_score(df["growth_rate"])
    df["transaction_score"] = transaction_score(df["transaction_count"])

    # 0 이하인 점포 수는 분모나 유효한 공급량으로 사용할 수 없다.
    # 정규화 집단에서도 제외해 유효한 상권의 점수를 왜곡하지 않는다.
    valid_store_count = df["store_count"].where(df["store_count"] > 0)
    df["demand_per_store"] = df["transaction_count"] / valid_store_count
    df["store_count_score"] = store_count_score(valid_store_count)
    df["demand_per_store_score"] = demand_per_store_score(df["demand_per_store"])
    df["closing_rate_score"] = closing_rate_score(df["closing_rate"])

    df["competition_score"] = competition_score(
        df["store_count_score"],
        df["demand_per_store_score"],
        df["closing_rate_score"],
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
