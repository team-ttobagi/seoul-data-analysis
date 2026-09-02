from typing import List, Optional
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.sales.schemas import (
    SalesSummarySchema,
    SalesByDaySchema,
    SalesByTimeSchema,
    SalesByAgeGenderSchema,
    StoreSummarySchema,
)


class SalesService:
    def __init__(self, repository: SalesRepository):
        self.repository = repository

    async def get_summary(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> Optional[SalesSummarySchema]:
        data = await self.repository.get_sales_summary(trade_area_code, industry_code, quarter)
        if data:
            return SalesSummarySchema(**data)
        return None

    async def get_by_time(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> List[SalesByTimeSchema]:
        items = await self.repository.get_sales_by_time(trade_area_code, industry_code, quarter)
        return [SalesByTimeSchema(**item) for item in items]

    async def get_by_age_gender(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> List[SalesByAgeGenderSchema]:
        items = await self.repository.get_sales_by_age_gender(trade_area_code, industry_code, quarter)
        return [SalesByAgeGenderSchema(**item) for item in items]

    async def get_by_day(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> List[SalesByDaySchema]:
        items = await self.repository.get_sales_by_day(trade_area_code, industry_code, quarter)
        return [SalesByDaySchema(**item) for item in items]

    async def get_store_summary(
        self, trade_area_code: str, industry_code: str = "CS100010", quarter: str = "2026 Q2"
    ) -> StoreSummarySchema:
        data = await self.repository.get_store_summary(trade_area_code, industry_code, quarter)
        return StoreSummarySchema(**data)
