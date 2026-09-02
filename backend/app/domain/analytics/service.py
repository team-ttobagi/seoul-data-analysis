from typing import List, Dict, Any, Optional
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
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.sales.repository import SalesRepository


class AnalyticsService:
    def __init__(
        self,
        trade_area_repo: TradeAreaRepository,
        sales_repo: SalesRepository,
    ):
        self.trade_area_repo = trade_area_repo
        self.sales_repo = sales_repo

    def calculate_exploration_score(
        self,
        sales_growth_norm: int,
        transaction_volume_norm: int,
        competition_norm: int,
    ) -> int:
        """
        Exploration Score formula:
        sales_growth_weight = 0.40
        transaction_volume_weight = 0.35
        competition_weight = 0.25 (competition contributes inversely or normalized appropriately)
        """
        sales_growth_weight = 0.40
        transaction_volume_weight = 0.35
        competition_weight = 0.25

        raw_score = (
            sales_growth_weight * sales_growth_norm
            + transaction_volume_weight * transaction_volume_norm
            + competition_weight * competition_norm
        )
        return int(round(raw_score))

    async def get_recommendations(
        self,
        industry_code: str = "CS100010",
        quarter: str = "2026 Q2",
        region: Optional[str] = "서울 전체",
    ) -> List[RecommendationItemResponse]:
        # Pre-calculated deterministic candidates adhering to Seoul Open Data patterns
        data = [
            {
                "rank": 1,
                "trade_area_code": "SEONGSU",
                "trade_area_name": "성수동",
                "district": "성동구",
                "growth_val": 12.4,
                "growth_norm": 91,
                "growth_percentile": 18,
                "volume_val": 450000,
                "volume_norm": 85,
                "volume_percentile": 12,
                "comp_val": 134,
                "comp_norm": 62,
                "comp_percentile": 88,
                "signals": {"growth": "high", "transaction": "high", "competition": "high"},
                "insight": "성장성과 거래 활성도가 높지만 경쟁도 강합니다.",
                "warning": "동일 업종 134개로 공급 집중 심화",
            },
            {
                "rank": 2,
                "trade_area_code": "HONGDAE",
                "trade_area_name": "홍대입구",
                "district": "마포구",
                "growth_val": 6.8,
                "growth_norm": 76,
                "growth_percentile": 25,
                "volume_val": 580000,
                "volume_norm": 94,
                "volume_percentile": 5,
                "comp_val": 182,
                "comp_norm": 52,
                "comp_percentile": 95,
                "signals": {"growth": "medium", "transaction": "high", "competition": "high"},
                "insight": "서울 최대 거래량을 자랑하지만 동일 업종 진입 밀도가 최상위권입니다.",
                "warning": "임대료 및 과밀 경쟁 유의",
            },
            {
                "rank": 3,
                "trade_area_code": "SHAROSU",
                "trade_area_name": "샤로수길",
                "district": "관악구",
                "growth_val": 14.1,
                "growth_norm": 95,
                "growth_percentile": 9,
                "volume_val": 280000,
                "volume_norm": 68,
                "volume_percentile": 38,
                "comp_val": 58,
                "comp_norm": 82,
                "comp_percentile": 45,
                "signals": {"growth": "high", "transaction": "medium", "competition": "low"},
                "insight": "1인 청년 가구의 소비 증가세가 뚜렷하며 상대적 경쟁 부담이 낮습니다.",
                "warning": None,
            },
            {
                "rank": 4,
                "trade_area_code": "KONKUK",
                "trade_area_name": "건대입구",
                "district": "광진구",
                "growth_val": 5.2,
                "growth_norm": 70,
                "growth_percentile": 34,
                "volume_val": 320000,
                "volume_norm": 74,
                "volume_percentile": 30,
                "comp_val": 96,
                "comp_norm": 69,
                "comp_percentile": 65,
                "signals": {"growth": "medium", "transaction": "medium", "competition": "medium"},
                "insight": "안정적인 대학생 배후 수요를 기반으로 꾸준한 소비 흐름을 보입니다.",
                "warning": None,
            },
            {
                "rank": 5,
                "trade_area_code": "GANGNAM",
                "trade_area_name": "강남역",
                "district": "강남구",
                "growth_val": 2.1,
                "growth_norm": 55,
                "growth_percentile": 62,
                "volume_val": 620000,
                "volume_norm": 98,
                "volume_percentile": 2,
                "comp_val": 240,
                "comp_norm": 42,
                "comp_percentile": 99,
                "signals": {"growth": "low", "transaction": "high", "competition": "high"},
                "insight": "거래 규모는 서울 최고이나 성장 정체와 초대형 프랜차이즈 과밀 상태입니다.",
                "warning": "초기 고정비 및 포화 경쟁 경계",
            },
        ]

        results = []
        for d in data:
            calc_score = self.calculate_exploration_score(
                sales_growth_norm=d["growth_norm"],
                transaction_volume_norm=d["volume_norm"],
                competition_norm=d["comp_norm"],
            )

            components = RecommendationComponents(
                sales_growth=ScoreComponent(
                    value=d["growth_val"],
                    normalized_score=d["growth_norm"],
                    benchmark_percentile=d["growth_percentile"],
                ),
                transaction_volume=ScoreComponent(
                    value=d["volume_val"],
                    normalized_score=d["volume_norm"],
                    benchmark_percentile=d["volume_percentile"],
                ),
                competition=ScoreComponent(
                    value=d["comp_val"],
                    normalized_score=d["comp_norm"],
                    benchmark_percentile=d["comp_percentile"],
                ),
            )

            results.append(
                RecommendationItemResponse(
                    rank=d["rank"],
                    trade_area_code=d["trade_area_code"],
                    trade_area_name=d["trade_area_name"],
                    district=d["district"],
                    score=calc_score,
                    signals=d["signals"],
                    components=components,
                    insight=d["insight"],
                    warning=d["warning"],
                )
            )

        return results

    async def get_overview(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> DistrictOverviewResponse:
        code = trade_area_code.upper()
        trade_area = await self.trade_area_repo.get_by_code(code)
        ta_name = trade_area["name"] if trade_area else "성수동"
        district_name = trade_area["district"] if trade_area else "성동구"

        summary = await self.sales_repo.get_sales_summary(code, industry_code, quarter)
        store = await self.sales_repo.get_store_summary(code, industry_code, quarter)

        kpis = DistrictKpis(
            estimated_sales=summary["estimated_sales"],
            estimated_sales_formatted=summary["estimated_sales_formatted"],
            transaction_count=summary["transaction_count"],
            transaction_count_formatted=summary["transaction_count_formatted"],
            seoul_rank=summary["seoul_rank"],
            qoq_growth_rate=summary["qoq_growth_rate"],
            sales_percentile=summary["sales_percentile"],
            volume_percentile=summary["volume_percentile"],
            store_count=store["store_count"],
            store_count_change=store["store_count_change"],
            competition_level=store["competition_level"],
            sales_level=store["sales_level"],
            volume_level=store["volume_level"],
        )

        why_explore = {
            "growth_rate": summary["qoq_growth_rate"],
            "growth_percentile": summary["sales_percentile"],
            "volume_formatted": summary["transaction_count_formatted"],
            "volume_percentile": summary["volume_percentile"],
            "store_count": store["store_count"],
            "competition_text": f"경쟁 {store['competition_level']}",
        }

        rankings = {
            "by_sales": [
                DistrictRankingItem(rank=1, trade_area_code="GANGNAM", trade_area_name="강남역", sales_formatted="18.5억", sales_raw=1850000000, is_current=False),
                DistrictRankingItem(rank=2, trade_area_code="HONGDAE", trade_area_name="홍대입구", sales_formatted="16.2억", sales_raw=1620000000, is_current=(code == "HONGDAE")),
                DistrictRankingItem(rank=3, trade_area_code="SEONGSU", trade_area_name="성수동", sales_formatted="12.8억", sales_raw=1280000000, is_current=(code == "SEONGSU")),
                DistrictRankingItem(rank=4, trade_area_code="GAROSU", trade_area_name="가로수길", sales_formatted="11.7억", sales_raw=1170000000, is_current=False),
                DistrictRankingItem(rank=5, trade_area_code="KONKUK", trade_area_name="건대입구", sales_formatted="8.9억", sales_raw=890000000, is_current=(code == "KONKUK")),
            ],
            "by_volume": [
                DistrictRankingItem(rank=1, trade_area_code="GANGNAM", trade_area_name="강남역", sales_formatted="62만", sales_raw=620000, is_current=False),
                DistrictRankingItem(rank=2, trade_area_code="HONGDAE", trade_area_name="홍대입구", sales_formatted="58만", sales_raw=580000, is_current=(code == "HONGDAE")),
                DistrictRankingItem(rank=3, trade_area_code="SEONGSU", trade_area_name="성수동", sales_formatted="45만", sales_raw=450000, is_current=(code == "SEONGSU")),
                DistrictRankingItem(rank=4, trade_area_code="GAROSU", trade_area_name="가로수길", sales_formatted="36만", sales_raw=360000, is_current=False),
                DistrictRankingItem(rank=5, trade_area_code="KONKUK", trade_area_name="건대입구", sales_formatted="32만", sales_raw=320000, is_current=(code == "KONKUK")),
            ],
            "by_growth": [
                DistrictRankingItem(rank=1, trade_area_code="SHAROSU", trade_area_name="샤로수길", sales_formatted="+14.1%", sales_raw=14.1, is_current=(code == "SHAROSU")),
                DistrictRankingItem(rank=2, trade_area_code="SEONGSU", trade_area_name="성수동", sales_formatted="+12.4%", sales_raw=12.4, is_current=(code == "SEONGSU")),
                DistrictRankingItem(rank=3, trade_area_code="EULJIRO", trade_area_name="을지로3가", sales_formatted="+9.2%", sales_raw=9.2, is_current=False),
                DistrictRankingItem(rank=4, trade_area_code="HONGDAE", trade_area_name="홍대입구", sales_formatted="+6.8%", sales_raw=6.8, is_current=(code == "HONGDAE")),
                DistrictRankingItem(rank=5, trade_area_code="KONKUK", trade_area_name="건대입구", sales_formatted="+5.2%", sales_raw=5.2, is_current=(code == "KONKUK")),
            ],
            "by_score": [
                DistrictRankingItem(rank=1, trade_area_code="SEONGSU", trade_area_name="성수동", sales_formatted="82점", sales_raw=82, is_current=(code == "SEONGSU")),
                DistrictRankingItem(rank=2, trade_area_code="HONGDAE", trade_area_name="홍대입구", sales_formatted="78점", sales_raw=78, is_current=(code == "HONGDAE")),
                DistrictRankingItem(rank=3, trade_area_code="SHAROSU", trade_area_name="샤로수길", sales_formatted="74점", sales_raw=74, is_current=(code == "SHAROSU")),
                DistrictRankingItem(rank=4, trade_area_code="KONKUK", trade_area_name="건대입구", sales_formatted="71점", sales_raw=71, is_current=(code == "KONKUK")),
                DistrictRankingItem(rank=5, trade_area_code="GANGNAM", trade_area_name="강남역", sales_formatted="69점", sales_raw=69, is_current=(code == "GANGNAM")),
            ],
        }

        score = 82 if code == "SEONGSU" else (78 if code == "HONGDAE" else 74)
        takeaway = {
            "score": score,
            "growth_tag": "매출 증가율 +++",
            "volume_tag": "거래건수 +++",
            "competition_tag": "경쟁 강도 -",
            "summary": f"{ta_name}은 거래량과 매출 성장성은 높은 편이지만 동일 업종 경쟁도 강합니다.",
            "disclaimer": "실제 창업 성공 가능성을 의미하지 않는 데이터 기반 탐색 지표입니다.",
        }

        return DistrictOverviewResponse(
            trade_area_code=code,
            trade_area_name=ta_name,
            district=district_name,
            industry_code=industry_code,
            industry_name="커피·음료",
            quarter=quarter,
            kpis=kpis,
            why_explore=why_explore,
            rankings=rankings,
            takeaway=takeaway,
        )

    async def get_patterns(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> DistrictPatternsResponse:
        code = trade_area_code.upper()
        time_slots = await self.sales_repo.get_sales_by_time(code, industry_code, quarter)
        demographics = await self.sales_repo.get_sales_by_age_gender(code, industry_code, quarter)
        days = await self.sales_repo.get_sales_by_day(code, industry_code, quarter)

        when_data = {
            "peak_slot": "17–21시",
            "insight": "저녁 17–21시에 소비가 가장 집중됩니다.",
            "slots": time_slots,
        }

        who_data = {
            "primary_target": "20대 여성",
            "target_badge": "주요 고객층",
            "insight": "20대 여성 소비 비중이 가장 높습니다.",
            "demographics": demographics,
        }

        day_data = {
            "peak_day": "금요일",
            "peak_diff_badge": "+21%",
            "insight": "금요일 매출이 주중 평균보다 21% 높습니다.",
            "days": days,
        }

        return DistrictPatternsResponse(when=when_data, who=who_data, day=day_data)

    async def get_competition(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> DistrictCompetitionResponse:
        code = trade_area_code.upper()
        store = await self.sales_repo.get_store_summary(code, industry_code, quarter)
        return DistrictCompetitionResponse(
            trade_area_code=code,
            store_count=store["store_count"],
            qoq_store_change=store["store_count_change"],
            competition_level=store["competition_level"],
            sales_level=store["sales_level"],
            volume_level=store["volume_level"],
            warning_text=store["warning_text"],
        )

    async def get_compare(
        self, trade_area_codes: List[str], industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> List[CompareDistrictData]:
        all_districts = {
            "SEONGSU": CompareDistrictData(
                trade_area_code="SEONGSU",
                trade_area_name="성수동",
                district="성동구",
                exploration_score=82,
                estimated_sales_formatted="12.8억",
                estimated_sales=1280000000,
                transaction_count_formatted="45만",
                transaction_count=450000,
                growth_rate=12.4,
                store_count=134,
                store_count_change=12,
                strongest_age_group="20대 여성 (45%)",
                strongest_time_period="17–21시 (36%)",
                strongest_day="금요일 (+21%)",
                competition_level="매우 높음",
                key_insight="트렌드 리딩 및 높은 매출 성장, 출점 과밀 주의",
            ),
            "HONGDAE": CompareDistrictData(
                trade_area_code="HONGDAE",
                trade_area_name="홍대입구",
                district="마포구",
                exploration_score=78,
                estimated_sales_formatted="16.2억",
                estimated_sales=1620000000,
                transaction_count_formatted="58만",
                transaction_count=580000,
                growth_rate=6.8,
                store_count=182,
                store_count_change=8,
                strongest_age_group="20대 남녀 (52%)",
                strongest_time_period="18–22시 (38%)",
                strongest_day="토요일 (+34%)",
                competition_level="매우 높음",
                key_insight="압도적 유동 거래량, 심야 및 주말 집중",
            ),
            "SHAROSU": CompareDistrictData(
                trade_area_code="SHAROSU",
                trade_area_name="샤로수길",
                district="관악구",
                exploration_score=74,
                estimated_sales_formatted="7.4억",
                estimated_sales=740000000,
                transaction_count_formatted="28만",
                transaction_count=280000,
                growth_rate=14.1,
                store_count=58,
                store_count_change=3,
                strongest_age_group="20대 1인가구 (48%)",
                strongest_time_period="18–21시 (32%)",
                strongest_day="금요일 (+18%)",
                competition_level="보통",
                key_insight="가장 높은 성장률(+14.1%), 상대적 경쟁 부담 완만",
            ),
            "KONKUK": CompareDistrictData(
                trade_area_code="KONKUK",
                trade_area_name="건대입구",
                district="광진구",
                exploration_score=71,
                estimated_sales_formatted="8.9억",
                estimated_sales=890000000,
                transaction_count_formatted="32만",
                transaction_count=320000,
                growth_rate=5.2,
                store_count=96,
                store_count_change=5,
                strongest_age_group="20대 학생 (50%)",
                strongest_time_period="17–21시 (34%)",
                strongest_day="금/토 (+16%)",
                competition_level="높음",
                key_insight="대학생 배후 수요 안정적, 저녁 시간대 집중",
            ),
            "GANGNAM": CompareDistrictData(
                trade_area_code="GANGNAM",
                trade_area_name="강남역",
                district="강남구",
                exploration_score=69,
                estimated_sales_formatted="18.5억",
                estimated_sales=1850000000,
                transaction_count_formatted="62만",
                transaction_count=620000,
                growth_rate=2.1,
                store_count=240,
                store_count_change=15,
                strongest_age_group="30대 직장인 (46%)",
                strongest_time_period="11–14시 (38%)",
                strongest_day="목/금 (+14%)",
                competition_level="매우 높음",
                key_insight="서울 최대 거래 규모이나 대형 프랜차이즈 과밀",
            ),
        }

        codes = trade_area_codes if trade_area_codes else ["SEONGSU", "HONGDAE", "SHAROSU"]
        return [all_districts.get(c.upper(), all_districts["SEONGSU"]) for c in codes]
