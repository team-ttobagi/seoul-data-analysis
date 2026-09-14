import asyncio
import logging
import math
import re
import time
from typing import Dict, List, Optional, Protocol, SupportsFloat, SupportsIndex

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
    DistrictTakeaway,
    OverviewInsightContext,
    OverviewInsightResponse,
)
from backend.app.domain.sales import scoring
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.industry.repository import IndustryRepository
from backend.app.domain.store.service import StoreService
from backend.app.domain.store.schemas import StoreSummarySchema, StoreTrendSchema
from backend.app.core.exceptions import SalesDataNotFoundException

logger = logging.getLogger(__name__)

# Gemini 프롬프트·외부 출력은 100자 이내이며, 내부 생성 결과 검증과 fallback은 120자까지 허용한다.
MAX_GENERATED_SUMMARY_LENGTH = 120
OVERVIEW_INSIGHT_PENDING_SUMMARY = "AI 인사이트 생성 중입니다."
_SENTENCE_TERMINATOR = re.compile(r"(?<!\d)[.!?。！？]")
_FORBIDDEN_GENERATED_CLAIMS = re.compile(
    r"창업\s*성공|성공(?:을|이)?\s*(?:보장|확신)|"
    r"(?:수익|이익)(?:을|이)?\s*보장|투자(?:금)?\s*회수|"
    r"미래\s*(?:매출|성과|수익)|(?:반드시|무조건)|확실(?:히|한)|"
    r"(?:최고|최적|대박|유망)|강력\s*추천|추천합니다|"
    r"매출(?:이|은)?\s*(?:오를|늘|증가할|상승할)"
)


class OverviewInsightGenerator(Protocol):
    """Gemini 통합 어댑터가 구현하는 비동기 경계."""

    async def generate(self, context: OverviewInsightContext) -> str:
        """검증된 사실 데이터로 평문 종합 요약 한 문장을 생성한다."""
        ...


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


def _build_insight(
    growth_grade: Optional[str],
    transaction_grade: Optional[str],
    competition_grade: Optional[str],
) -> str:
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


def _validate_generated_summary(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("generated summary must be a string")
    summary = value.strip()
    if not summary:
        raise ValueError("generated summary must not be empty")
    if len(summary) > MAX_GENERATED_SUMMARY_LENGTH:
        raise ValueError("generated summary is too long")
    if "\n" in summary or "\r" in summary:
        raise ValueError("generated summary must be one sentence")
    if not re.search(r"[가-힣]", summary):
        raise ValueError("generated summary must contain Korean text")
    if _FORBIDDEN_GENERATED_CLAIMS.search(summary):
        raise ValueError("generated summary contains a forbidden claim")
    terminators = list(_SENTENCE_TERMINATOR.finditer(summary))
    if len(terminators) != 1 or not summary.endswith(terminators[0].group()):
        raise ValueError("generated summary must be one sentence")
    return summary


def _optional_float(value: object) -> Optional[float]:
    """원천 결측·비유한 값을 0이 아닌 None으로 보존한다."""
    if value is None or isinstance(value, bool):
        return None

    # ``object``는 float()에 전달 가능한 타입이라는 보장이 없으므로,
    # Python의 float 변환 계약에 해당하는 타입으로 먼저 좁힌다.
    if not isinstance(
        value,
        (str, bytes, bytearray, SupportsFloat, SupportsIndex),
    ):
        return None

    try:
        converted = float(value)
    except (TypeError, ValueError, OverflowError):
        return None
    return converted if math.isfinite(converted) else None


def _franchise_ratio_percent(
    franchise_store_count: object,
    store_count: object,
) -> Optional[float]:
    """유효한 점포 원천값으로만 프랜차이즈 비율을 계산한다."""
    franchise_count = _optional_float(franchise_store_count)
    total_count = _optional_float(store_count)
    if (
        franchise_count is None
        or total_count is None
        or total_count <= 0
        or franchise_count < 0
        or franchise_count > total_count
    ):
        return None
    return franchise_count / total_count * 100


def _first_pattern_value(items: object, key: str, flag: str) -> Optional[str]:
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, dict) and item.get(flag):
            value = item.get(key)
            return value if isinstance(value, str) and value.strip() else None
    return None


class AnalyticsService:
    def __init__(
        self,
        trade_area_repo: TradeAreaRepository,
        sales_repo: SalesRepository,
        industry_repo: Optional[IndustryRepository] = None,
        *,
        store_service: StoreService,
        insight_generator: Optional[OverviewInsightGenerator] = None,
        insight_timeout_seconds: float = 6.0,
    ):
        if not 0 < insight_timeout_seconds <= 10:
            raise ValueError(
                "insight_timeout_seconds must be greater than 0 and at most 10"
            )
        self.trade_area_repo = trade_area_repo
        self.sales_repo = sales_repo
        self.industry_repo = industry_repo
        self.store_service = store_service
        self.insight_generator = insight_generator
        self.insight_timeout_seconds = insight_timeout_seconds

    async def _get_overview_data(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> tuple[str, str, str, str, pd.DataFrame, pd.Series]:
        """overview와 insight가 공유하는 검증된 분석 사실을 조회합니다."""
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
        matched = (
            metrics_df[metrics_df["trdar_cd"] == code]
            if not metrics_df.empty
            else metrics_df
        )
        if matched.empty:
            raise SalesDataNotFoundException(code, industry_code, quarter)

        return code, ta_name, district_name, industry_name, metrics_df, matched.iloc[0]

    def _build_overview_insight_context(
        self,
        *,
        trade_area_name: str,
        district_name: str,
        industry_name: str,
        quarter: str,
        row: pd.Series,
        patterns: tuple[Optional[str], Optional[str], Optional[str]],
        store_summary: Optional[StoreSummarySchema],
        store_trend: Optional[StoreTrendSchema],
    ) -> OverviewInsightContext:
        strongest_age_group, peak_slot, peak_day = patterns
        franchise_ratio_percent = _franchise_ratio_percent(
            store_summary.franchise_store_count if store_summary else None,
            store_summary.store_count if store_summary else None,
        )
        return OverviewInsightContext(
            trade_area_name=trade_area_name,
            district_name=district_name,
            industry_name=industry_name,
            quarter=quarter,
            strongest_age_group=strongest_age_group,
            peak_slot=peak_slot,
            peak_day=peak_day,
            closing_rate=_optional_float(
                store_summary.closing_rate if store_summary else None
            ),
            opening_rate=_optional_float(
                store_summary.opening_rate if store_summary else None
            ),
            franchise_ratio_percent=franchise_ratio_percent,
            store_count_change=(
                store_trend.store_count_change if store_trend else None
            ),
            qoq_growth_rate=_optional_float(row.get("growth_rate")),
            growth_level=scoring.grade_from_score(row["growth_score"]),
            transaction_level=scoring.grade_from_score(row["transaction_score"]),
            competition_level=scoring.grade_from_score(row["competition_score"]),
        )

    async def _get_overview_insight_patterns(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """기존 SalesRepository 패턴 조회에서 insight용 대표값만 추출한다."""
        try:
            # 하나의 AsyncSession을 공유하므로 원천 조회를 동시에 실행하지 않는다.
            time_slots = await self.sales_repo.get_sales_by_time(
                trade_area_code, industry_code, quarter
            )
            demographics = await self.sales_repo.get_sales_by_age_gender(
                trade_area_code, industry_code, quarter
            )
            days = await self.sales_repo.get_sales_by_day(
                trade_area_code, industry_code, quarter
            )
        except Exception:
            logger.exception(
                "인사이트 패턴 원천 데이터 조회에 실패했다 (reason=patterns_error)",
                extra={
                    "event": "analytics.overview_insight_data_failed",
                    "reason": "patterns_error",
                    "trade_area_code": trade_area_code,
                    "industry_code": industry_code,
                    "quarter": quarter,
                },
            )
            return None, None, None

        return (
            _first_pattern_value(demographics, "age_group", "is_primary"),
            _first_pattern_value(time_slots, "slot", "is_peak"),
            _first_pattern_value(days, "day", "is_peak"),
        )

    async def _get_overview_insight_store_summary(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> Optional[StoreSummarySchema]:
        """점포 요약을 조회하고 실패 시 결측으로 격리한다."""
        try:
            return await self.store_service.get_summary(
                trade_area_code=trade_area_code,
                industry_code=industry_code,
                quarter=quarter,
            )
        except Exception:
            logger.exception(
                "인사이트 점포 원천 데이터 조회에 실패했다 (reason=store_summary_error)",
                extra={
                    "event": "analytics.overview_insight_data_failed",
                    "reason": "store_summary_error",
                    "trade_area_code": trade_area_code,
                    "industry_code": industry_code,
                    "quarter": quarter,
                },
            )
            return None

    async def _get_overview_insight_store_trend(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> Optional[StoreTrendSchema]:
        """인사이트용 점포 추이를 조회하고 실패 시 결측으로 격리한다."""
        try:
            return await self.store_service.get_store_trend(
                trade_area_code=trade_area_code,
                industry_code=industry_code,
                quarter=quarter,
            )
        except Exception:
            logger.exception(
                "인사이트 점포 추이 원천 데이터 조회에 실패했다 (reason=store_trend_error)",
                extra={
                    "event": "analytics.overview_insight_data_failed",
                    "reason": "store_trend_error",
                    "trade_area_code": trade_area_code,
                    "industry_code": industry_code,
                    "quarter": quarter,
                },
            )
            return None

    def _build_overview_fallback_summary(
        self,
        *,
        growth_level: Optional[scoring.ScoreLevel],
        transaction_level: Optional[scoring.ScoreLevel],
        competition_level: Optional[scoring.ScoreLevel],
    ) -> str:
        return _build_insight(
            growth_level,
            transaction_level,
            competition_level,
        )

    async def _get_overview_insight_response(
        self,
        *,
        trade_area_code: str,
        trade_area_name: str,
        district_name: str,
        industry_code: str,
        industry_name: str,
        quarter: str,
        row: pd.Series,
        store_trend: Optional[StoreTrendSchema],
    ) -> OverviewInsightResponse:
        """분리된 /overview/insight 응답으로 Gemini 또는 fallback을 생성한다."""
        fallback = self._build_overview_fallback_summary(
            growth_level=scoring.grade_from_score(row["growth_score"]),
            transaction_level=scoring.grade_from_score(row["transaction_score"]),
            competition_level=scoring.grade_from_score(row["competition_score"]),
        )
        if self.insight_generator is None:
            return OverviewInsightResponse(
                summary=fallback,
                source="fallback",
                status="fallback",
            )

        patterns = await self._get_overview_insight_patterns(
            trade_area_code, industry_code, quarter
        )
        store_summary = await self._get_overview_insight_store_summary(
            trade_area_code, industry_code, quarter
        )
        context = self._build_overview_insight_context(
            trade_area_name=trade_area_name,
            district_name=district_name,
            industry_name=industry_name,
            quarter=quarter,
            row=row,
            patterns=patterns,
            store_summary=store_summary,
            store_trend=store_trend,
        )
        return await self._generate_overview_insight(
            trade_area_code=trade_area_code,
            industry_name=industry_name,
            quarter=quarter,
            context=context,
            fallback=fallback,
        )

    async def _generate_overview_insight(
        self,
        *,
        trade_area_code: str,
        industry_name: str,
        quarter: str,
        context: OverviewInsightContext,
        fallback: str,
    ) -> OverviewInsightResponse:
        log_context = {
            "event": "analytics.overview_insight_fallback",
            "trade_area_code": trade_area_code,
            "industry_name": industry_name,
            "quarter": quarter,
        }
        if self.insight_generator is None:
            logger.info(
                "인사이트 생성기가 없어 결정론적 fallback을 사용한다 "
                "(reason=generator_unavailable)",
                extra={
                    **log_context,
                    "reason": "generator_unavailable",
                    "elapsed_ms": 0,
                },
            )
            return OverviewInsightResponse(
                summary=fallback,
                source="fallback",
                status="fallback",
            )

        try:
            started_at = time.monotonic()
            generated = await asyncio.wait_for(
                self.insight_generator.generate(context),
                timeout=self.insight_timeout_seconds,
            )

            elapsed = time.monotonic() - started_at

            logger.info(
                "Gemini 인사이트 생성 호출 완료 (reason=provider_success)",
                extra={
                    **log_context,
                    "event": "analytics.overview_insight_provider_success",
                    "reason": "provider_success",
                    "elapsed_ms": round(elapsed * 1000, 2),
                },
            )

        except asyncio.TimeoutError:
            elapsed = time.monotonic() - started_at

            logger.warning(
                "인사이트 생성 시간이 초과되어 결정론적 fallback을 사용한다 "
                "(reason=timeout, elapsed=%.2fs, timeout=%.2fs)",
                elapsed,
                self.insight_timeout_seconds,
                extra={
                    **log_context,
                    "reason": "timeout",
                    "elapsed_ms": round(elapsed * 1000, 2),
                },
            )

            return OverviewInsightResponse(
                summary=fallback,
                source="fallback",
                status="fallback",
            )
        except Exception:
            logger.exception(
                "인사이트 생성 호출에 실패해 결정론적 fallback을 사용한다 "
                "(reason=generator_error)",
                extra={
                    **log_context,
                    "reason": "generator_error",
                    "elapsed_ms": round(
                        (time.monotonic() - started_at) * 1000,
                        2,
                    ),
                },
            )
            return OverviewInsightResponse(
                summary=fallback,
                source="fallback",
                status="fallback",
            )

        try:
            validated = _validate_generated_summary(generated)
            logger.info(
                "Gemini 인사이트 생성을 완료했다 (reason=generated)",
                extra={
                    "event": "analytics.overview_insight_generated",
                    "trade_area_code": trade_area_code,
                    "industry_name": industry_name,
                    "quarter": quarter,
                    "reason": "generated",
                    "elapsed_ms": round(elapsed * 1000, 2),
                },
            )
            return OverviewInsightResponse(
                summary=validated,
                source="gemini",
                status="generated",
            )
        except ValueError:
            logger.warning(
                "Gemini 출력 검증에 실패해 결정론적 fallback을 사용한다 "
                "(reason=validation)",
                extra={
                    **log_context,
                    "reason": "validation",
                    "elapsed_ms": round(elapsed * 1000, 2),
                },
            )
            return OverviewInsightResponse(
                summary=fallback,
                source="fallback",
                status="fallback",
            )

    async def _get_store_trend(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> Optional[StoreTrendSchema]:
        """점포 추이를 조회하며 현재·직전 분기 데이터가 없으면 None을 반환합니다."""
        return await self.store_service.get_store_trend(
            trade_area_code=trade_area_code,
            industry_code=industry_code,
            quarter=quarter,
        )

    async def _get_store_trends(
        self,
        trade_area_codes: List[str],
        industry_code: str,
        quarter: str,
    ) -> Dict[str, StoreTrendSchema]:
        """비교 대상 상권들의 점포 추이를 한 번의 저장소 호출로 조회합니다."""
        return await self.store_service.get_store_trends(
            trade_area_codes=trade_area_codes,
            industry_code=industry_code,
            quarter=quarter,
        )

    async def _compute_metrics(self, quarter: str, industry_code: str) -> pd.DataFrame:
        """모든 분석 화면에서 SalesRepository의 통합 점수 집단을 재사용한다.

        계산을 이 저장소 경계 안에서 처리하면 overview, competition, compare,
        recommendations가 /sales/summary에서 사용하는 CompetitionScore와 달라지는
        문제를 방지할 수 있다.
        """
        return await self.sales_repo.get_metrics_dataframe(quarter, industry_code)

    async def _trade_area_lookup(self) -> Dict[str, dict]:
        trade_areas = await self.trade_area_repo.get_all()
        return {ta["trdar_cd"]: ta for ta in trade_areas}

    async def get_recommendations(
        self,
        industry_code: str = "CS100010",
        quarter: str = "20254",
        region: Optional[str] = "서울 전체",
        keyword: Optional[str] = None,
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

        if keyword:
            needle = keyword.strip().lower()
            matching_codes = {
                code
                for code, ta in lookup.items()
                if needle in (ta.get("trdar_cd_nm") or "").lower()
            }
            metrics_df = metrics_df[metrics_df["trdar_cd"].isin(matching_codes)]

        # ExplorationScore가 산출 불가(NaN)인 상권은 "낮은 점수"가 아니라 "데이터 부족"이므로
        # 추천 후보에서 아예 제외한다 (0점으로 강등시키지 않는다).
        scored = metrics_df.dropna(subset=["exploration_score"])
        top = scored.sort_values("exploration_score", ascending=False).head(100)

        results = []
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            ta = lookup.get(row["trdar_cd"], {})
            growth_grade = scoring.signal_from_score(row["growth_score"])
            transaction_grade = scoring.signal_from_score(row["transaction_score"])
            competition_grade = scoring.signal_from_score(row["competition_score"])

            components = RecommendationComponents(
                sales_growth=ScoreComponent(
                    value=scoring.none_if_nan(row["growth_rate"]),
                    normalized_score=scoring.none_if_nan_round(row["growth_score"]),
                    benchmark_percentile=scoring.none_if_nan_round(
                        row["growth_percentile"]
                    ),
                ),
                transaction_volume=ScoreComponent(
                    value=row["transaction_count"],
                    normalized_score=scoring.none_if_nan_round(
                        row["transaction_score"]
                    ),
                    benchmark_percentile=scoring.none_if_nan_round(
                        row["volume_percentile"]
                    ),
                ),
                competition=ScoreComponent(
                    value=scoring.none_if_nan(row["competition_score"]),
                    normalized_score=scoring.none_if_nan_round(
                        row["competition_score"]
                    ),
                    benchmark_percentile=scoring.none_if_nan_round(
                        row["competition_percentile"]
                    ),
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
                    warning=_build_warning(
                        scoring.grade_from_score(row["competition_score"])
                    ),
                )
            )

        return results

    async def get_overview(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "20254",
    ) -> DistrictOverviewResponse:
        code, ta_name, district_name, industry_name, metrics_df, row = (
            await self._get_overview_data(trade_area_code, industry_code, quarter)
        )
        store_trend = await self._get_store_trend(code, industry_code, quarter)

        kpis = DistrictKpis(
            estimated_sales=int(row["sales"]),
            estimated_sales_formatted=_fmt_amount(row["sales"]),
            transaction_count=int(row["transaction_count"]),
            transaction_count_formatted=_fmt_count(row["transaction_count"]),
            seoul_rank=scoring.none_if_nan_round(row["seoul_rank"]),
            qoq_growth_rate=scoring.none_if_nan(row["growth_rate"]),
            sales_percentile=round(row["sales_percentile"]),
            growth_percentile=scoring.none_if_nan_round(row["growth_percentile"]),
            volume_percentile=round(row["volume_percentile"]),
            store_count=store_trend.store_count if store_trend else None,
            store_count_change=store_trend.store_count_change if store_trend else None,
            competition_level=scoring.grade_from_score(row["competition_score"]),
            sales_level=scoring.grade_from_score(100 - row["sales_percentile"]),
            volume_level=scoring.grade_from_score(100 - row["volume_percentile"]),
        )

        why_explore = {
            "growth_rate": kpis.qoq_growth_rate,
            "growth_percentile": kpis.growth_percentile,
            "volume_formatted": kpis.transaction_count_formatted,
            "volume_percentile": kpis.volume_percentile,
            "store_count": kpis.store_count,
            "competition_text": f"경쟁 여건 {kpis.competition_level or '정보 없음'}",
        }

        lookup = await self._trade_area_lookup()
        rankings = {
            "by_sales": self._ranking_items(metrics_df, "sales", "sales", code, lookup),
            "by_volume": self._ranking_items(
                metrics_df, "transaction_count", "transaction_count", code, lookup
            ),
            "by_growth": self._ranking_items(
                metrics_df, "growth_rate", "growth_rate", code, lookup
            ),
            "by_score": self._ranking_items(
                metrics_df, "exploration_score", "score", code, lookup
            ),
        }

        exploration_score = scoring.none_if_nan_round(row["exploration_score"])
        takeaway = DistrictTakeaway(
            # ExplorationScore가 산출 불가(NaN)면 0점이 아니라 None + 안내 문구로 표시한다.
            score=exploration_score,
            score_note=(
                None
                if exploration_score is not None
                else "일부 지표 부족으로 탐색 점수를 산출할 수 없습니다."
            ),
            growth_tag=(
                f"매출 성장률 {kpis.qoq_growth_rate:+.1f}%"
                if kpis.qoq_growth_rate is not None
                else "매출 성장률 산출 불가"
            ),
            volume_tag=f"거래건수 {kpis.transaction_count_formatted}",
            competition_tag=f"경쟁 여건 {kpis.competition_level or '정보 없음'}",
            summary=OVERVIEW_INSIGHT_PENDING_SUMMARY,
            disclaimer=(
                "탐색 점수는 창업 성공 확률·수익·투자 적합성을 보장하거나 "
                "예측하지 않는 데이터 기반 상대 지표입니다."
            ),
        )

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

    async def get_overview_insight(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "20254",
    ) -> OverviewInsightResponse:
        code, ta_name, district_name, industry_name, _, row = await self._get_overview_data(
            trade_area_code, industry_code, quarter
        )
        store_trend = await self._get_overview_insight_store_trend(
            code, industry_code, quarter
        )
        return await self._get_overview_insight_response(
            trade_area_code=code,
            trade_area_name=ta_name,
            district_name=district_name,
            industry_code=industry_code,
            industry_name=industry_name,
            quarter=quarter,
            row=row,
            store_trend=store_trend,
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
        # growth_rate/exploration_score가 산출 불가(NaN)인 상권은 0으로 대체하지 않고
        # 순위 후보에서 제외한다 (데이터 부족과 낮은 성과를 구분).
        candidates = (
            metrics_df.dropna(subset=[sort_col])
            if sort_col in ("growth_rate", "exploration_score")
            else metrics_df
        )
        top = candidates.sort_values(sort_col, ascending=False).head(top_n)
        items = []
        for rank, (_, row) in enumerate(top.iterrows(), start=1):
            ta = lookup.get(row["trdar_cd"], {})
            if value_kind == "sales":
                raw, formatted = row["sales"], _fmt_amount(row["sales"])
            elif value_kind == "transaction_count":
                raw, formatted = row["transaction_count"], _fmt_count(
                    row["transaction_count"]
                )
            elif value_kind == "growth_rate":
                raw = row["growth_rate"]
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
        quarter: str = "20254",
    ) -> DistrictPatternsResponse:
        code = trade_area_code.upper()
        time_slots = await self.sales_repo.get_sales_by_time(
            code, industry_code, quarter
        )
        demographics = await self.sales_repo.get_sales_by_age_gender(
            code, industry_code, quarter
        )
        gender = await self.sales_repo.get_gender_split(code, industry_code, quarter)
        days = await self.sales_repo.get_sales_by_day(code, industry_code, quarter)

        peak_slot = next((s["slot"] for s in time_slots if s["is_peak"]), None)
        when_data = {
            "peak_slot": peak_slot,
            "insight": (
                f"{peak_slot}에 소비가 가장 집중됩니다."
                if peak_slot
                else "시간대 데이터가 없습니다."
            ),
            "slots": time_slots,
        }

        primary_age = next((d for d in demographics if d["is_primary"]), None)
        who_data = {
            "primary_age_group": primary_age["age_group"] if primary_age else None,
            "primary_age_percentage": (
                primary_age["percentage"] if primary_age else None
            ),
            "gender": gender,
            "insight": (
                f"{primary_age['age_group']} 소비 비중이 가장 높습니다."
                if primary_age
                else "연령대 데이터가 없습니다."
            ),
            "demographics": demographics,
        }

        peak_day = next((d for d in days if d["is_peak"]), None)
        day_data = {
            "peak_day": peak_day["day"] if peak_day else None,
            "peak_diff_badge": (
                f"{peak_day['diff_from_average']:+d}%" if peak_day else None
            ),
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
        quarter: str = "20254",
    ) -> DistrictCompetitionResponse:
        code = trade_area_code.upper()
        metrics_df = await self._compute_metrics(quarter, industry_code)
        matched = (
            metrics_df[metrics_df["trdar_cd"] == code]
            if not metrics_df.empty
            else metrics_df
        )
        store_trend = await self._get_store_trend(code, industry_code, quarter)
        if matched.empty:
            return DistrictCompetitionResponse(
                trade_area_code=code,
                store_count=store_trend.store_count if store_trend else None,
                qoq_store_change=(
                    store_trend.store_count_change if store_trend else None
                ),
            )

        row = matched.iloc[0]
        competition_grade = scoring.grade_from_score(row["competition_score"])
        return DistrictCompetitionResponse(
            trade_area_code=code,
            store_count=store_trend.store_count if store_trend else None,
            qoq_store_change=store_trend.store_count_change if store_trend else None,
            competition_level=competition_grade,
            sales_level=scoring.grade_from_score(100 - row["sales_percentile"]),
            volume_level=scoring.grade_from_score(100 - row["volume_percentile"]),
            warning_text=_build_warning(competition_grade),
        )

    async def get_compare(
        self,
        trade_area_codes: List[str],
        industry_code: str = "CS100010",
        quarter: str = "20254",
    ) -> List[CompareDistrictData]:
        codes = [c.upper() for c in trade_area_codes] if trade_area_codes else []
        if not codes:
            return []

        metrics_df = await self._compute_metrics(quarter, industry_code)
        lookup = await self._trade_area_lookup()
        store_trends = await self._get_store_trends(codes, industry_code, quarter)

        results = []
        for code in codes:
            matched = (
                metrics_df[metrics_df["trdar_cd"] == code]
                if not metrics_df.empty
                else metrics_df
            )
            if matched.empty:
                continue
            row = matched.iloc[0]
            ta = lookup.get(code, {})
            store_trend = store_trends.get(code)

            demographics = await self.sales_repo.get_sales_by_age_gender(
                code, industry_code, quarter
            )
            primary_age = next((d for d in demographics if d["is_primary"]), None)
            time_slots = await self.sales_repo.get_sales_by_time(
                code, industry_code, quarter
            )
            peak_slot = next((s for s in time_slots if s["is_peak"]), None)
            days = await self.sales_repo.get_sales_by_day(code, industry_code, quarter)
            peak_day = next((d for d in days if d["is_peak"]), None)

            competition_grade = scoring.grade_from_score(row["competition_score"])

            results.append(
                CompareDistrictData(
                    trade_area_code=code,
                    trade_area_name=ta.get("trdar_cd_nm", code),
                    district=ta.get("signgu_cd_nm") or "-",
                    exploration_score=scoring.none_if_nan_round(
                        row["exploration_score"]
                    ),
                    estimated_sales_formatted=_fmt_amount(row["sales"]),
                    estimated_sales=int(row["sales"]),
                    transaction_count_formatted=_fmt_count(row["transaction_count"]),
                    transaction_count=int(row["transaction_count"]),
                    growth_rate=scoring.none_if_nan(row["growth_rate"]),
                    store_count=store_trend.store_count if store_trend else None,
                    store_count_change=(
                        store_trend.store_count_change if store_trend else None
                    ),
                    strongest_age_group=(
                        f"{primary_age['age_group']} ({primary_age['percentage']}%)"
                        if primary_age
                        else "-"
                    ),
                    strongest_time_period=(
                        f"{peak_slot['slot']} ({peak_slot['percentage']}%)"
                        if peak_slot
                        else "-"
                    ),
                    strongest_day=(
                        f"{peak_day['day']} ({peak_day['diff_from_average']:+d}%)"
                        if peak_day
                        else "-"
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
