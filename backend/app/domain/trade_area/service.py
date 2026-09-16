from typing import List
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.trade_area.schemas import (
    TradeAreaResponse,
    TradeAreaSearchResponse,
)
from backend.app.domain.sales.repository import SalesRepository
from backend.app.core.exceptions import TradeAreaNotFoundException


class TradeAreaService:
    def __init__(
        self,
        repository: TradeAreaRepository,
        sales_repo: SalesRepository,
    ):
        self.repository = repository
        self.sales_repo = sales_repo

    async def _filter_scored_trade_areas(
        self,
        trade_areas: List[dict],
        industry_code: str,
        quarter: str,
    ) -> List[dict]:
        metrics_df = await self.sales_repo.get_metrics_dataframe(
            quarter,
            industry_code,
        )
        if metrics_df.empty or "exploration_score" not in metrics_df:
            return []

        scored_codes = set(
            metrics_df.dropna(subset=["exploration_score"])["trdar_cd"]
        )
        return [
            trade_area
            for trade_area in trade_areas
            if trade_area.get("trdar_cd") in scored_codes
        ]

    async def get_all_trade_areas(self) -> List[TradeAreaResponse]:
        trade_areas = await self.repository.get_all()
        return [TradeAreaResponse(**ta) for ta in trade_areas]

    async def get_trade_area(self, code: str) -> TradeAreaResponse:
        trade_area = await self.repository.get_by_code(code)
        if not trade_area:
            raise TradeAreaNotFoundException(trade_area_code=code)
        return TradeAreaResponse(**trade_area)

    async def get_trade_areas_by_filters(
        self,
        industry_code: str,
        signgu_cd: str,
        quarter: str,
    ) -> List[TradeAreaSearchResponse]:
        trade_areas = await self.repository.get_by_filters(
            industry_code=industry_code,
            signgu_cd=signgu_cd,
            quarter=quarter,
        )
        trade_areas = await self._filter_scored_trade_areas(
            trade_areas,
            industry_code,
            quarter,
        )

        return [
            TradeAreaSearchResponse(
                code=ta["trdar_cd"],
                name=ta["trdar_cd_nm"],
                district_code=ta["signgu_cd"],
                district_name=ta["signgu_cd_nm"],
            )
            for ta in trade_areas
        ]
