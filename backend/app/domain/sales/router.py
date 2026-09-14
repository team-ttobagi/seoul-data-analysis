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
        description="조회 기준 분기. YYYY QN 형식이며 N은 1~4입니다. 미입력 시 2025년 4분기를 조회합니다.",
        examples=["2025 Q4"],
    ),
    service: SalesService = Depends(get_sales_service),
):
    """선택한 상권·업종·분기의 매출 요약과 서울 비교 지표를 반환합니다.

    분기 추정 매출액, 거래건수, QoQ 매출 성장률, 서울 종합 순위와
    매출·거래건수의 Benchmark Percentile을 제공합니다. 순위와 Percentile은
    동일 분기·동일 업종의 서울 상권을 비교하며, 상권 상세 개요 API와 같은
    계산 결과를 사용합니다.

    조회 조건에 맞는 매출 데이터가 없거나 DB 연결 또는 매출 조회가 실패하면
    HTTP 200과 null을 반환합니다. 전분기 매출이 없거나 0 이하이면
    qoq_growth_rate는 null이며, 서울 종합 순위에 필요한 4개 Benchmark
    Percentile 중 하나라도 산출할 수 없으면 seoul_rank는 null입니다.
    여기서 CompetitionScore는 동일 분기·업종의 점포 수 50% + 점포당 거래건수
    30% + 폐업률 20%로 산출하며, 애널리틱스 API와 같은 계산 결과를 사용합니다.
    """
    return await service.get_summary(trade_area_code, industry_code, quarter)
