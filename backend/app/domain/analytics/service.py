from typing import List, Dict, Optional

import pandas as pd

from backend.app.domain.analytics.schemas import (
    RecommendationItemResponse,
    DistrictOverviewResponse,
    DistrictPatternsResponse,
    DistrictCompetitionResponse,
    CompareDistrictData,
    RecommendationComponents,
    ScoreComponent,
    DistrictKpis,
    DistrictRankingItem,
)
from backend.app.domain.analytics import scoring
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.industry.repository import IndustryRepository
from backend.app.core.exceptions import SalesDataNotFoundException


def _fmt_amount(amount: Optional[float]) -> str:
    if amount is None or pd.isna(amount):
        return "-"
    amount = float(amount)
    if amount >= 100_000_000:
        return f"{amount / 100_000_000:.1f}억"
    if amount >= 10_000:
        return f"{amount / 10_000:.0f}만"
    return str(int(amount))


def _fmt_count(count: Optional[float]) -> str:
    if count is None or pd.isna(count):
        return "-"
    count = float(count)
    if count >= 10_000:
        return f"{count / 10_000:.0f}만"
    return str(int(count))


def _none_if_nan(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return value


def _build_insight(growth_grade: Optional[str], transaction_grade: Optional[str], competition_grade: Optional[str]) -> str:
    parts = []
    if growth_grade:
        parts.append(f"성장성 {growth_grade}")
    if transaction_grade:
        parts.append(f"거래 활성도 {transaction_grade}")
    if competition_grade:
        parts.append(f"경쟁 여건 {competition_grade}")
    if not parts:
        return "데이터가 충분하지 않아 판단이 어렵습니다."
    return ", ".join(parts) + " 수준의 상권입니다."


def _build_warning(competition_grade: Optional[str]) -> Optional[str]:
    if competition_grade == "낮음":
        return "동일 업종 경쟁 압박이 상대적으로 높은 상권입니다."
    return None


class AnalyticsService:
    def __init__(
        self,
        trade_area_repo: TradeAreaRepository,
        sales_repo: SalesRepository,
        industry_repo: Optional[IndustryRepository] = None,
    ):
        self.trade_area_repo = trade_area_repo
        self.sales_repo = sales_repo
        self.industry_repo = industry_repo

    async def _compute_metrics(self, quarter: str, industry_code: str) -> pd.DataFrame:
        rows = await self.sales_repo.get_metrics_rows(quarter, industry_code)
        diversity_rows = await self.sales_repo.get_diversity_rows(quarter)
        return scoring.build_metrics_dataframe(rows, diversity_rows)

    async def _trade_area_lookup(self) -> Dict[str, dict]:
        trade_areas = await self.trade_area_repo.get_all()
        return {ta["trdar_cd"]: ta for ta in trade_areas}

    async def get_recommendations(
        self,
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
        region: Optional[str] = "서울 전체",
    ) -> List[RecommendationItemResponse]:
        metrics_df = await self._compute_metrics(quarter, industry_code)
        if metrics_df.empty:
            return []

        lookup = await self._trade_area_lookup()

        if region and region != "서울 전체":
            valid_codes = {
                code for code, ta in lookup.items() if ta.get("signgu_cd_nm") == region
            }
            metrics_df = metrics_df[metrics_df["trdar_cd"].isin(valid_codes)]

        top = metrics_df.sort_values("exploration_score", ascending=False).head(5)

        results = []
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            ta = lookup.get(row["trdar_cd"], {})
            growth_grade = scoring.signal_from_score(row["growth_score"])
            transaction_grade = scoring.signal_from_score(row["transaction_score"])
            competition_grade = scoring.signal_from_score(row["competition_score"])

            components = RecommendationComponents(
                sales_growth=ScoreComponent(
                    value=_none_if_nan(row["growth_rate"]) or 0.0,
                    normalized_score=round(_none_if_nan(row["growth_score"]) or 0),
                    benchmark_percentile=_none_if_nan(row["growth_percentile"]) and round(row["growth_percentile"]),
                ),
                transaction_volume=ScoreComponent(
                    value=row["transaction_count"],
                    normalized_score=round(_none_if_nan(row["transaction_score"]) or 0),
                    benchmark_percentile=_none_if_nan(row["volume_percentile"]) and round(row["volume_percentile"]),
                ),
                competition=ScoreComponent(
                    value=_none_if_nan(row["competition_score"]) or 0.0,
                    normalized_score=round(_none_if_nan(row["competition_score"]) or 0),
                    benchmark_percentile=_none_if_nan(row["competition_percentile"]) and round(row["competition_percentile"]),
                ),
            )

            results.append(
                RecommendationItemResponse(
                    rank=rank,
                    trade_area_code=row["trdar_cd"],
                    trade_area_name=ta.get("trdar_cd_nm", row["trdar_cd"]),
                    district=ta.get("signgu_cd_nm") or "-",
                    score=round(row["exploration_score"]),
                    signals={
                        "growth": growth_grade or "medium",
                        "transaction": transaction_grade or "medium",
                        "competition": competition_grade or "medium",
                    },
                    components=components,
                    insight=_build_insight(
                        scoring.grade_from_score(row["growth_score"]),
                        scoring.grade_from_score(row["transaction_score"]),
                        scoring.grade_from_score(row["competition_score"]),
                    ),
                    warning=_build_warning(scoring.grade_from_score(row["competition_score"])),
                )
            )

        return results

    async def get_overview(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> DistrictOverviewResponse:
        code = trade_area_code.upper()
        trade_area = await self.trade_area_repo.get_by_code(code)
        ta_name = trade_area["trdar_cd_nm"] if trade_area else code
        district_name = trade_area["signgu_cd_nm"] if trade_area else "-"

        industry_name = industry_code
        if self.industry_repo:
            industry = await self.industry_repo.get_by_code(industry_code)
            if industry:
                industry_name = industry["name"]

        metrics_df = await self._compute_metrics(quarter, industry_code)
        matched = metrics_df[metrics_df["trdar_cd"] == code] if not metrics_df.empty else metrics_df
        if matched.empty:
            raise SalesDataNotFoundException(code, industry_code, quarter)
        row = matched.iloc[0]

        kpis = DistrictKpis(
            estimated_sales=int(row["sales"]),
            estimated_sales_formatted=_fmt_amount(row["sales"]),
            transaction_count=int(row["transaction_count"]),
            transaction_count_formatted=_fmt_count(row["transaction_count"]),
            seoul_rank=int(row["seoul_rank"]),
            qoq_growth_rate=_none_if_nan(row["growth_rate"]),
            sales_percentile=round(row["sales_percentile"]),
            volume_percentile=round(row["volume_percentile"]),
            competition_level=scoring.grade_from_score(row["competition_score"]),
            sales_level=scoring.grade_from_score(100 - row["sales_percentile"]),
            volume_level=scoring.grade_from_score(100 - row["volume_percentile"]),
        )

        why_explore = {
            "growth_rate": kpis.qoq_growth_rate,
            "growth_percentile": kpis.sales_percentile,
            "volume_formatted": kpis.transaction_count_formatted,
            "volume_percentile": kpis.volume_percentile,
        }

        lookup = await self._trade_area_lookup()
        rankings = {
            "by_sales": self._ranking_items(metrics_df, "sales", "sales", code, lookup),
            "by_volume": self._ranking_items(metrics_df, "transaction_count", "transaction_count", code, lookup),
            "by_growth": self._ranking_items(metrics_df, "growth_rate", "growth_rate", code, lookup),
            "by_score": self._ranking_items(metrics_df, "exploration_score", "score", code, lookup),
        }

        exploration_score = round(row["exploration_score"])
        takeaway = {
            "score": exploration_score,
            "growth_tag": f"매출 성장률 {kpis.qoq_growth_rate:+.1f}%" if kpis.qoq_growth_rate is not None else "매출 성장률 정보 없음",
            "volume_tag": f"거래건수 {kpis.transaction_count_formatted}",
            "competition_tag": f"경쟁 여건 {kpis.competition_level or '정보 없음'}",
            "summary": _build_insight(
                scoring.grade_from_score(row["growth_score"]),
                scoring.grade_from_score(row["transaction_score"]),
                scoring.grade_from_score(row["competition_score"]),
            ),
            "disclaimer": "실제 창업 성공 가능성을 의미하지 않는 데이터 기반 탐색 지표입니다.",
        }

        return DistrictOverviewResponse(
            trade_area_code=code,
            trade_area_name=ta_name,
            district=district_name,
            industry_code=industry_code,
            industry_name=industry_name,
            quarter=quarter,
            kpis=kpis,
            why_explore=why_explore,
            rankings=rankings,
            takeaway=takeaway,
        )

    def _ranking_items(
        self,
        metrics_df: pd.DataFrame,
        sort_col: str,
        value_kind: str,
        current_code: str,
        lookup: Dict[str, dict],
        top_n: int = 5,
    ) -> List[DistrictRankingItem]:
        top = metrics_df.sort_values(sort_col, ascending=False).head(top_n)
        items = []
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            ta = lookup.get(row["trdar_cd"], {})
            if value_kind == "sales":
                raw, formatted = row["sales"], _fmt_amount(row["sales"])
            elif value_kind == "transaction_count":
                raw, formatted = row["transaction_count"], _fmt_count(row["transaction_count"])
            elif value_kind == "growth_rate":
                raw = _none_if_nan(row["growth_rate"]) or 0.0
                formatted = f"{raw:+.1f}%"
            else:
                raw = round(row["exploration_score"])
                formatted = f"{raw}점"

            items.append(
                DistrictRankingItem(
                    rank=rank,
                    trade_area_code=row["trdar_cd"],
                    trade_area_name=ta.get("trdar_cd_nm", row["trdar_cd"]),
                    sales_formatted=formatted,
                    sales_raw=float(raw),
                    is_current=(row["trdar_cd"] == current_code),
                )
            )
        return items

    async def get_patterns(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> DistrictPatternsResponse:
        code = trade_area_code.upper()
        time_slots = await self.sales_repo.get_sales_by_time(code, industry_code, quarter)
        demographics = await self.sales_repo.get_sales_by_age_gender(code, industry_code, quarter)
        gender = await self.sales_repo.get_gender_split(code, industry_code, quarter)
        days = await self.sales_repo.get_sales_by_day(code, industry_code, quarter)

        peak_slot = next((s["slot"] for s in time_slots if s["is_peak"]), None)
        when_data = {
            "peak_slot": peak_slot,
            "insight": f"{peak_slot}에 소비가 가장 집중됩니다." if peak_slot else "시간대 데이터가 없습니다.",
            "slots": time_slots,
        }

        primary_age = next((d for d in demographics if d["is_primary"]), None)
        who_data = {
            "primary_age_group": primary_age["age_group"] if primary_age else None,
            "primary_age_percentage": primary_age["percentage"] if primary_age else None,
            "gender": gender,
            "insight": (
                f"{primary_age['age_group']} 소비 비중이 가장 높습니다." if primary_age else "연령대 데이터가 없습니다."
            ),
            "demographics": demographics,
        }

        peak_day = next((d for d in days if d["is_peak"]), None)
        day_data = {
            "peak_day": peak_day["day"] if peak_day else None,
            "peak_diff_badge": f"{peak_day['diff_from_average']:+d}%" if peak_day else None,
            "insight": (
                f"{peak_day['day']}요일 매출이 주중 평균보다 {peak_day['diff_from_average']:+d}% 높습니다."
                if peak_day
                else "요일 데이터가 없습니다."
            ),
            "days": days,
        }

        return DistrictPatternsResponse(when=when_data, who=who_data, day=day_data)

    async def get_competition(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> DistrictCompetitionResponse:
        code = trade_area_code.upper()
        metrics_df = await self._compute_metrics(quarter, industry_code)
        matched = metrics_df[metrics_df["trdar_cd"] == code] if not metrics_df.empty else metrics_df
        if matched.empty:
            return DistrictCompetitionResponse(trade_area_code=code)

        row = matched.iloc[0]
        competition_grade = scoring.grade_from_score(row["competition_score"])
        return DistrictCompetitionResponse(
            trade_area_code=code,
            competition_level=competition_grade,
            sales_level=scoring.grade_from_score(100 - row["sales_percentile"]),
            volume_level=scoring.grade_from_score(100 - row["volume_percentile"]),
            warning_text=_build_warning(competition_grade),
        )

    async def get_compare(
        self,
        trade_area_codes: List[str],
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> List[CompareDistrictData]:
        codes = [c.upper() for c in trade_area_codes] if trade_area_codes else []
        if not codes:
            return []

        metrics_df = await self._compute_metrics(quarter, industry_code)
        lookup = await self._trade_area_lookup()

        results = []
        for code in codes:
            matched = metrics_df[metrics_df["trdar_cd"] == code] if not metrics_df.empty else metrics_df
            if matched.empty:
                continue
            row = matched.iloc[0]
            ta = lookup.get(code, {})

            demographics = await self.sales_repo.get_sales_by_age_gender(code, industry_code, quarter)
            primary_age = next((d for d in demographics if d["is_primary"]), None)
            time_slots = await self.sales_repo.get_sales_by_time(code, industry_code, quarter)
            peak_slot = next((s for s in time_slots if s["is_peak"]), None)
            days = await self.sales_repo.get_sales_by_day(code, industry_code, quarter)
            peak_day = next((d for d in days if d["is_peak"]), None)

            competition_grade = scoring.grade_from_score(row["competition_score"])

            results.append(
                CompareDistrictData(
                    trade_area_code=code,
                    trade_area_name=ta.get("trdar_cd_nm", code),
                    district=ta.get("signgu_cd_nm") or "-",
                    exploration_score=round(row["exploration_score"]),
                    estimated_sales_formatted=_fmt_amount(row["sales"]),
                    estimated_sales=int(row["sales"]),
                    transaction_count_formatted=_fmt_count(row["transaction_count"]),
                    transaction_count=int(row["transaction_count"]),
                    growth_rate=_none_if_nan(row["growth_rate"]),
                    strongest_age_group=(
                        f"{primary_age['age_group']} ({primary_age['percentage']}%)" if primary_age else "-"
                    ),
                    strongest_time_period=(
                        f"{peak_slot['slot']} ({peak_slot['percentage']}%)" if peak_slot else "-"
                    ),
                    strongest_day=(
                        f"{peak_day['day']} ({peak_day['diff_from_average']:+d}%)" if peak_day else "-"
                    ),
                    competition_level=competition_grade,
                    key_insight=_build_insight(
                        scoring.grade_from_score(row["growth_score"]),
                        scoring.grade_from_score(row["transaction_score"]),
                        competition_grade,
                    ),
                )
            )

        return results
