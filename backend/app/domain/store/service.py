from typing import Dict, Optional, Sequence

from backend.app.domain.store.repository import StoreRepository
from backend.app.domain.store.schemas import StoreSummarySchema, StoreTrendSchema


class StoreService:
    def __init__(self, repository: StoreRepository):
        self.repository = repository

    async def get_summary(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> Optional[StoreSummarySchema]:
        """점포 요약 원천 데이터를 API 응답 스키마로 변환합니다."""
        data = await self.repository.get_store_summary(
            trade_area_code,
            industry_code,
            quarter,
        )
        return StoreSummarySchema(**data) if data else None

    async def get_store_trend(
        self,
        trade_area_code: str,
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> Optional[StoreTrendSchema]:
        """현재·직전 분기의 점포 추이를 조회해 분석용 DTO로 반환합니다."""
        return await self.repository.get_store_trend(
            trade_area_code,
            industry_code,
            quarter,
        )

    async def get_store_trends(
        self,
        trade_area_codes: Sequence[str],
        industry_code: str = "CS100010",
        quarter: str = "2025 Q4",
    ) -> Dict[str, StoreTrendSchema]:
        """여러 상권의 점포 추이를 조회해 상권 코드별 DTO로 반환합니다."""
        return await self.repository.get_store_trends(
            trade_area_codes,
            industry_code,
            quarter,
        )
