from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.domain.store.repository import StoreRepository
from backend.app.domain.store.schemas import StoreSummarySchema
from backend.app.domain.store.service import StoreService

router = APIRouter(prefix="/stores", tags=["Store"])


def get_store_service(
    db: AsyncSession = Depends(get_db),
) -> StoreService:
    """요청 단위 DB 세션으로 점포 서비스 의존성을 구성합니다."""
    return StoreService(repository=StoreRepository(session=db))


@router.get("/summary", response_model=Optional[StoreSummarySchema])
async def get_summary(
    trade_area_code: str = Query(
        ...,
        description="조회할 상권 코드. 상권 목록 API의 trdar_cd를 사용하며 영문은 대문자로 변환해 조회합니다.",
        examples=["SEONGSU"],
    ),
    industry_code: str = Query(
        "CS100010",
        description="조회할 서비스 업종 코드. 업종 목록 API의 code를 사용하며 기본값은 커피·음료입니다.",
        examples=["CS100010"],
    ),
    quarter: str = Query(
        "2025 Q4",
        description="조회 기준 분기. YYYY QN 또는 DB 코드 YYYYQ 형식으로 전달할 수 있습니다.",
        examples=["2025 Q4"],
    ),
    service: StoreService = Depends(get_store_service),
):
    """선택한 상권·업종·분기의 점포 통계를 반환합니다.

    동일 업종·일반·프랜차이즈 점포 수와 개업·폐업률 및 개업·폐업 점포 수를 제공합니다.
    조건에 맞는 데이터가 없으면 HTTP 200과 null을 반환합니다.
    DB 연결 또는 조회가 실패하면 오류 응답을 반환합니다.
    """
    return await service.get_summary(trade_area_code, industry_code, quarter)
