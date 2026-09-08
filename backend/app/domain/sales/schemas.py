from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class SalesSummarySchema(BaseModel):
    quarter: str
    trade_area_code: str
    industry_code: str
    estimated_sales: int
    estimated_sales_formatted: str
    transaction_count: int
    transaction_count_formatted: str
    qoq_growth_rate: float
    seoul_rank: int
    sales_percentile: int
    volume_percentile: int


class SalesByDaySchema(BaseModel):
    day: str
    percentage: int
    diff_from_average: int
    is_peak: bool


class SalesByTimeSchema(BaseModel):
    slot: str
    percentage: int
    sales_amount: int
    is_peak: bool


class SalesByAgeGenderSchema(BaseModel):
    age_group: str
    percentage: int
    female_ratio: int
    male_ratio: int
    dominant_gender: str
    is_primary: bool


