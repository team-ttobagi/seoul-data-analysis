from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.analytics.service import AnalyticsService
from backend.app.domain.analytics.schemas import (
    RecommendationItemResponse,
    DistrictOverviewResponse,
    DistrictPatternsResponse,
    DistrictCompetitionResponse,
    CompareDistrictData,
)

router = APIRouter(tags=["Analytics"])


def get_analytics_service(db: Optional[AsyncSession] = Depends(get_db)) -> AnalyticsService:
    trade_area_repo = TradeAreaRepository(session=db)
    sales_repo = SalesRepository(session=db)
    return AnalyticsService(trade_area_repo=trade_area_repo, sales_repo=sales_repo)


@router.get("/analytics/recommendations", response_model=List[RecommendationItemResponse])
async def get_recommendations(
    industry_code: str = Query("CS100010", description="Industry code, default coffee/beverage"),
    quarter: str = Query("2025 Q4", description="Quarter"),
    region: Optional[str] = Query("서울 전체", description="Administrative region"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_recommendations(industry_code, quarter, region)


@router.get("/trade-areas/{trade_area_code}/overview", response_model=DistrictOverviewResponse)
async def get_district_overview(
    trade_area_code: str,
    industry_code: str = Query("CS100010", description="Industry code"),
    quarter: str = Query("2025 Q4", description="Quarter"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_overview(trade_area_code, industry_code, quarter)


@router.get("/trade-areas/{trade_area_code}/patterns", response_model=DistrictPatternsResponse)
async def get_district_patterns(
    trade_area_code: str,
    industry_code: str = Query("CS100010", description="Industry code"),
    quarter: str = Query("2025 Q4", description="Quarter"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_patterns(trade_area_code, industry_code, quarter)


@router.get("/trade-areas/{trade_area_code}/competition", response_model=DistrictCompetitionResponse)
async def get_district_competition(
    trade_area_code: str,
    industry_code: str = Query("CS100010", description="Industry code"),
    quarter: str = Query("2025 Q4", description="Quarter"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    return await service.get_competition(trade_area_code, industry_code, quarter)


@router.get("/compare", response_model=List[CompareDistrictData])
async def get_compare_districts(
    trade_area_codes: str = Query(..., description="Comma-separated trade area codes"),
    industry_code: str = Query("CS100010", description="Industry code"),
    quarter: str = Query("2025 Q4", description="Quarter"),
    service: AnalyticsService = Depends(get_analytics_service),
):
    codes = [c.strip() for c in trade_area_codes.split(",") if c.strip()]
    return await service.get_compare(codes, industry_code, quarter)
