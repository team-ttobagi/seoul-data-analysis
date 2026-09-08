from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.sales.service import SalesService
from backend.app.domain.sales.schemas import (
    SalesSummarySchema,
    SalesByDaySchema,
    SalesByTimeSchema,
    SalesByAgeGenderSchema,
)

router = APIRouter(prefix="/sales", tags=["Sales"])


def get_sales_service(db: Optional[AsyncSession] = Depends(get_db)) -> SalesService:
    repository = SalesRepository(session=db)
    return SalesService(repository=repository)


@router.get("/summary", response_model=Optional[SalesSummarySchema])
async def get_summary(
    trade_area_code: str = Query(..., description="Trade area code"),
    industry_code: str = Query("CS100010", description="Industry code"),
    quarter: str = Query("2025 Q4", description="Quarter"),
    service: SalesService = Depends(get_sales_service),
):
    return await service.get_summary(trade_area_code, industry_code, quarter)
