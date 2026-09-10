from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.trade_area.service import TradeAreaService
from backend.app.domain.trade_area.schemas import (
    TradeAreaResponse,
    TradeAreaSearchResponse,
)

router = APIRouter(prefix="/trade-areas", tags=["TradeArea"])


def get_trade_area_service(
    db: Optional[AsyncSession] = Depends(get_db),
) -> TradeAreaService:
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


@router.get("/search", response_model=List[TradeAreaSearchResponse])
async def search_trade_areas(
    signgu_cd: str,
    keyword: Optional[str] = None,
    service: TradeAreaService = Depends(get_trade_area_service),
):
    """선택한 자치구에 속한 상권 목록을 반환합니다.

    signgu_cd에 해당하는 자치구의 전체 상권을 조회합니다.

    keyword를 전달하면 해당 자치구 내에서 상권명에 검색어가 포함된
    전체 검색 결과를 반환합니다.

    검색 결과 개수는 Backend에서 임의로 제한하지 않으며,
    조건에 일치하는 상권이 없거나 DB 연결 또는 조회가 실패하면
    빈 배열을 반환합니다.

    응답에는 상권 코드, 상권명, 자치구 코드, 자치구명이 포함됩니다.
    """

    return await service.get_trade_areas_by_district(
        signgu_cd=signgu_cd,
        keyword=keyword,
    )


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
