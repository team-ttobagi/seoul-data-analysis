from typing import List
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.trade_area.schemas import (
    TradeAreaResponse,
    TradeAreaSearchResponse,
)
from backend.app.core.exceptions import TradeAreaNotFoundException


class TradeAreaService:
    def __init__(self, repository: TradeAreaRepository):
        self.repository = repository

    async def get_all_trade_areas(self) -> List[TradeAreaResponse]:
        trade_areas = await self.repository.get_all()
        return [TradeAreaResponse(**ta) for ta in trade_areas]

    async def get_trade_area(self, code: str) -> TradeAreaResponse:
        trade_area = await self.repository.get_by_code(code)
        if not trade_area:
            raise TradeAreaNotFoundException(trade_area_code=code)
        return TradeAreaResponse(**trade_area)

    async def get_trade_areas_by_district(
        self,
        signgu_cd: str,
        keyword: str | None = None,
    ) -> List[TradeAreaSearchResponse]:
        trade_areas = await self.repository.get_by_district(
            signgu_cd=signgu_cd,
            keyword=keyword,
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
