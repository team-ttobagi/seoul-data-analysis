from typing import List, Optional, Dict, Any
from pydantic import BaseModel


class ScoreComponent(BaseModel):
    value: float
    normalized_score: int
    unit: Optional[str] = None
    benchmark_percentile: Optional[int] = None


class RecommendationComponents(BaseModel):
    sales_growth: ScoreComponent
    transaction_volume: ScoreComponent
    competition: ScoreComponent


class RecommendationItemResponse(BaseModel):
    rank: int
    trade_area_code: str
    trade_area_name: str
    district: str
    score: int
    signals: Dict[str, str]
    components: RecommendationComponents
    insight: str
    warning: Optional[str] = None


class DistrictKpis(BaseModel):
    estimated_sales: int
    estimated_sales_formatted: str
    transaction_count: int
    transaction_count_formatted: str
    seoul_rank: int
    qoq_growth_rate: Optional[float] = None
    sales_percentile: int
    volume_percentile: int
    competition_level: Optional[str] = None
    sales_level: Optional[str] = None
    volume_level: Optional[str] = None


class DistrictRankingItem(BaseModel):
    rank: int
    trade_area_code: str
    trade_area_name: str
    sales_formatted: str
    sales_raw: float
    is_current: bool
    score: Optional[int] = None
    growth_rate: Optional[float] = None
    transaction_count: Optional[int] = None


class DistrictOverviewResponse(BaseModel):
    trade_area_code: str
    trade_area_name: str
    district: str
    industry_code: str
    industry_name: str
    quarter: str
    kpis: DistrictKpis
    why_explore: Dict[str, Any]
    rankings: Dict[str, List[DistrictRankingItem]]
    takeaway: Dict[str, Any]


class TimeSlotSales(BaseModel):
    slot: str
    percentage: int
    is_peak: bool
    sales_amount: int


class AgeGenderSales(BaseModel):
    age_group: str
    percentage: int
    is_primary: bool


class GenderSales(BaseModel):
    female_ratio: int
    male_ratio: int
    dominant_gender: str


class DaySales(BaseModel):
    day: str
    percentage: int
    diff_from_average: int
    is_peak: bool


class DistrictPatternsResponse(BaseModel):
    when: Dict[str, Any]
    who: Dict[str, Any]
    day: Dict[str, Any]


class DistrictCompetitionResponse(BaseModel):
    trade_area_code: str
    competition_level: Optional[str] = None
    sales_level: Optional[str] = None
    volume_level: Optional[str] = None
    warning_text: Optional[str] = None


class CompareDistrictData(BaseModel):
    trade_area_code: str
    trade_area_name: str
    district: str
    exploration_score: int
    estimated_sales_formatted: str
    estimated_sales: int
    transaction_count_formatted: str
    transaction_count: int
    growth_rate: Optional[float] = None
    strongest_age_group: str
    strongest_time_period: str
    strongest_day: str
    competition_level: Optional[str] = None
    key_insight: str
