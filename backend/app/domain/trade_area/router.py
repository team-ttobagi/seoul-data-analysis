from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.trade_area.service import TradeAreaService
from backend.app.domain.trade_area.schemas import TradeAreaResponse

router = APIRouter(prefix="/trade-areas", tags=["TradeArea"])


def get_trade_area_service(db: Optional[AsyncSession] = Depends(get_db)) -> TradeAreaService:
    repository = TradeAreaRepository(session=db)
    return TradeAreaService(repository=repository)


@router.get("", response_model=List[TradeAreaResponse])
async def list_trade_areas(
    service: TradeAreaService = Depends(get_trade_area_service),
):
    return await service.get_all_trade_areas()


@router.get("/{trade_area_code}", response_model=TradeAreaResponse)
async def get_trade_area_by_code(
    trade_area_code: str,
    service: TradeAreaService = Depends(get_trade_area_service),
):
    return await service.get_trade_area(trade_area_code)
