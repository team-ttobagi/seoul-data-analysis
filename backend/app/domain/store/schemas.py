from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class StoreSummarySchema(BaseModel):
    quarter: str = Field(description="조회 기준 분기")
    trade_area_code: str = Field(description="조회 상권 코드")
    industry_code: str = Field(description="조회 업종 코드")
    store_count: int = Field(description="동일 업종 점포 수(개)")
    general_store_count: int = Field(description="일반 점포 수(개)")
    franchise_store_count: int = Field(description="프랜차이즈 점포 수(개)")
    opening_rate: float = Field(description="개업률(%)")
    opening_store_count: int = Field(description="개업 점포 수(개)")
    closing_rate: float = Field(description="폐업률(%)")
    closing_store_count: int = Field(description="폐업 점포 수(개)")

    model_config = ConfigDict(from_attributes=True)


class StoreTrendSchema(BaseModel):
    """점포 도메인이 분석 도메인에 제공하는 분기별 점포 추이 데이터."""

    store_count: int = Field(description="현재 분기의 동일 업종 점포 수(개)")
    store_count_change: Optional[int] = Field(
        default=None,
        description="동일 업종 점포 수의 전분기 대비 증감 수(개). 직전 분기 데이터가 없으면 null.",
    )

    model_config = ConfigDict(from_attributes=True)
