from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession


class SalesRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_sales_summary(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> Optional[dict]:
        code = trade_area_code.upper()
        # Seeded factual data
        summaries = {
            "SEONGSU": {
                "quarter": quarter,
                "trade_area_code": "SEONGSU",
                "industry_code": industry_code,
                "estimated_sales": 1280000000,
                "estimated_sales_formatted": "12.8억",
                "transaction_count": 450000,
                "transaction_count_formatted": "45만",
                "qoq_growth_rate": 8.2,
                "seoul_rank": 7,
                "sales_percentile": 18,
                "volume_percentile": 12,
            },
            "HONGDAE": {
                "quarter": quarter,
                "trade_area_code": "HONGDAE",
                "industry_code": industry_code,
                "estimated_sales": 1620000000,
                "estimated_sales_formatted": "16.2억",
                "transaction_count": 580000,
                "transaction_count_formatted": "58만",
                "qoq_growth_rate": 6.8,
                "seoul_rank": 2,
                "sales_percentile": 5,
                "volume_percentile": 5,
            },
            "SHAROSU": {
                "quarter": quarter,
                "trade_area_code": "SHAROSU",
                "industry_code": industry_code,
                "estimated_sales": 740000000,
                "estimated_sales_formatted": "7.4억",
                "transaction_count": 280000,
                "transaction_count_formatted": "28만",
                "qoq_growth_rate": 14.1,
                "seoul_rank": 18,
                "sales_percentile": 28,
                "volume_percentile": 38,
            },
            "KONKUK": {
                "quarter": quarter,
                "trade_area_code": "KONKUK",
                "industry_code": industry_code,
                "estimated_sales": 890000000,
                "estimated_sales_formatted": "8.9억",
                "transaction_count": 320000,
                "transaction_count_formatted": "32만",
                "qoq_growth_rate": 5.2,
                "seoul_rank": 12,
                "sales_percentile": 22,
                "volume_percentile": 30,
            },
            "GANGNAM": {
                "quarter": quarter,
                "trade_area_code": "GANGNAM",
                "industry_code": industry_code,
                "estimated_sales": 1850000000,
                "estimated_sales_formatted": "18.5억",
                "transaction_count": 620000,
                "transaction_count_formatted": "62만",
                "qoq_growth_rate": 2.1,
                "seoul_rank": 1,
                "sales_percentile": 2,
                "volume_percentile": 2,
            },
        }
        return summaries.get(code, summaries["SEONGSU"])

    async def get_sales_by_time(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> List[dict]:
        code = trade_area_code.upper()
        if code == "HONGDAE":
            return [
                {"slot": "06-11시", "percentage": 8, "sales_amount": 129600000, "is_peak": False},
                {"slot": "11-14시", "percentage": 16, "sales_amount": 259200000, "is_peak": False},
                {"slot": "14-17시", "percentage": 22, "sales_amount": 356400000, "is_peak": False},
                {"slot": "17-21시", "percentage": 38, "sales_amount": 615600000, "is_peak": True},
                {"slot": "21-24시", "percentage": 16, "sales_amount": 259200000, "is_peak": False},
            ]
        # Default SEONGSU
        return [
            {"slot": "06-11시", "percentage": 10, "sales_amount": 128000000, "is_peak": False},
            {"slot": "11-14시", "percentage": 18, "sales_amount": 230400000, "is_peak": False},
            {"slot": "14-17시", "percentage": 24, "sales_amount": 307200000, "is_peak": False},
            {"slot": "17-21시", "percentage": 36, "sales_amount": 460800000, "is_peak": True},
            {"slot": "21-24시", "percentage": 12, "sales_amount": 153600000, "is_peak": False},
        ]

    async def get_sales_by_age_gender(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> List[dict]:
        code = trade_area_code.upper()
        if code == "HONGDAE":
            return [
                {"age_group": "10대", "percentage": 12, "female_ratio": 55, "male_ratio": 45, "dominant_gender": "female", "is_primary": False},
                {"age_group": "20대", "percentage": 52, "female_ratio": 58, "male_ratio": 42, "dominant_gender": "female", "is_primary": True},
                {"age_group": "30대", "percentage": 24, "female_ratio": 48, "male_ratio": 52, "dominant_gender": "male", "is_primary": False},
                {"age_group": "40대+", "percentage": 12, "female_ratio": 45, "male_ratio": 55, "dominant_gender": "male", "is_primary": False},
            ]
        return [
            {"age_group": "10대", "percentage": 15, "female_ratio": 52, "male_ratio": 48, "dominant_gender": "female", "is_primary": False},
            {"age_group": "20대", "percentage": 45, "female_ratio": 65, "male_ratio": 35, "dominant_gender": "female", "is_primary": True},
            {"age_group": "30대", "percentage": 25, "female_ratio": 52, "male_ratio": 48, "dominant_gender": "female", "is_primary": False},
            {"age_group": "40대+", "percentage": 15, "female_ratio": 40, "male_ratio": 60, "dominant_gender": "male", "is_primary": False},
        ]

    async def get_sales_by_day(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> List[dict]:
        code = trade_area_code.upper()
        if code == "HONGDAE":
            return [
                {"day": "월", "percentage": 11, "diff_from_average": -15, "is_peak": False},
                {"day": "화", "percentage": 12, "diff_from_average": -10, "is_peak": False},
                {"day": "수", "percentage": 13, "diff_from_average": -5, "is_peak": False},
                {"day": "목", "percentage": 14, "diff_from_average": 2, "is_peak": False},
                {"day": "금", "percentage": 18, "diff_from_average": 22, "is_peak": False},
                {"day": "토", "percentage": 20, "diff_from_average": 34, "is_peak": True},
                {"day": "일", "percentage": 12, "diff_from_average": -8, "is_peak": False},
            ]
        return [
            {"day": "월", "percentage": 12, "diff_from_average": -10, "is_peak": False},
            {"day": "화", "percentage": 13, "diff_from_average": -5, "is_peak": False},
            {"day": "수", "percentage": 14, "diff_from_average": 0, "is_peak": False},
            {"day": "목", "percentage": 15, "diff_from_average": 6, "is_peak": False},
            {"day": "금", "percentage": 21, "diff_from_average": 21, "is_peak": True},
            {"day": "토", "percentage": 14, "diff_from_average": 2, "is_peak": False},
            {"day": "일", "percentage": 11, "diff_from_average": -14, "is_peak": False},
        ]

    async def get_store_summary(
        self, trade_area_code: str, industry_code: str, quarter: str
    ) -> dict:
        code = trade_area_code.upper()
        stores = {
            "SEONGSU": {
                "store_count": 134,
                "store_count_change": 12,
                "competition_level": "매우 높음",
                "sales_level": "높음",
                "volume_level": "높음",
                "warning_text": "수요도 크지만 동일 업종 공급 역시 빠르게 증가하고 있습니다.",
            },
            "HONGDAE": {
                "store_count": 182,
                "store_count_change": 8,
                "competition_level": "매우 높음",
                "sales_level": "매우 높음",
                "volume_level": "매우 높음",
                "warning_text": "상권 활성도가 높은 만큼 점포 간 간격이 좁고 폐업률 변동성이 큽니다.",
            },
            "SHAROSU": {
                "store_count": 58,
                "store_count_change": 3,
                "competition_level": "보통",
                "sales_level": "보통",
                "volume_level": "보통",
                "warning_text": "비교적 안정적이나 최근 신규 카페 입점이 점진적으로 늘어나는 추세입니다.",
            },
            "KONKUK": {
                "store_count": 96,
                "store_count_change": 5,
                "competition_level": "높음",
                "sales_level": "보통",
                "volume_level": "보통",
                "warning_text": "주요 번화가 집중 입점으로 신규 진입 시 목 좋은 입지 선점이 필수적입니다.",
            },
            "GANGNAM": {
                "store_count": 240,
                "store_count_change": 15,
                "competition_level": "매우 높음",
                "sales_level": "매우 높음",
                "volume_level": "매우 높음",
                "warning_text": "대형 프랜차이즈 간 출혈 경쟁 및 높은 임대료 부담이 존재합니다.",
            },
        }
        return stores.get(code, stores["SEONGSU"])
