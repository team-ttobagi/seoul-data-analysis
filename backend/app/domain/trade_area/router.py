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
    """상권 검색·선택에 사용하는 전체 상권 목록을 반환합니다.

    등록된 상권의 코드, 구분 코드, 이름과 소속 자치구 정보를 조회합니다.
    업종·분기·자치구에 따른 필터 없이 전체 목록을 반환합니다.
    등록된 상권이 없거나 DB 연결 또는 조회가 실패하면 빈 배열을 반환하며,
    연결된 자치구 정보가 없는 상권의 signgu_cd_nm은 null입니다.
    """
    return await service.get_all_trade_areas()


@router.get("/{trade_area_code}", response_model=TradeAreaResponse)
async def get_trade_area_by_code(
    trade_area_code: str,
    service: TradeAreaService = Depends(get_trade_area_service),
):
    """상권 코드에 해당하는 상권의 기본 정보와 소속 자치구를 반환합니다.

    trade_area_code가 등록된 상권 코드와 정확히 일치하는 상권을 조회합니다.
    상권이 없거나 DB 연결 또는 조회가 실패하면 HTTP 404
    (TRADE_AREA_NOT_FOUND)를 반환합니다.
    상권은 존재하지만 연결된 자치구 정보가 없으면 signgu_cd_nm은 null입니다.
    """
    return await service.get_trade_area(trade_area_code)
