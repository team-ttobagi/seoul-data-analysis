from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.domain.industry.repository import IndustryRepository
from backend.app.domain.industry.service import IndustryService
from backend.app.domain.industry.schemas import IndustryResponse

router = APIRouter(prefix="/industries", tags=["Industry"])


def get_industry_service(db: Optional[AsyncSession] = Depends(get_db)) -> IndustryService:
    repository = IndustryRepository(session=db)
    return IndustryService(repository=repository)


@router.get("", response_model=List[IndustryResponse])
async def list_industries(
    service: IndustryService = Depends(get_industry_service),
):
    """업종 선택 드롭다운에 사용하는 전체 서비스 업종 목록을 반환합니다.

    등록된 모든 업종의 코드와 이름을 조회합니다. 상권이나 분기에 따른
    필터 없이 반환하며, 각 code를 매출·분석 API의 industry_code로 사용합니다.
    등록된 업종이 없거나 DB 연결 또는 조회가 실패하면 빈 배열을 반환합니다.
    """
    return await service.get_all_industries()


@router.get("/{industry_code}", response_model=IndustryResponse)
async def get_industry_by_code(
    industry_code: str,
    service: IndustryService = Depends(get_industry_service),
):
    """서비스 업종 코드에 해당하는 업종의 코드와 이름을 반환합니다.

    industry_code가 등록된 서비스 업종 코드와 정확히 일치하는 업종을 조회합니다.
    업종이 없거나 DB 연결 또는 조회가 실패하면 HTTP 404
    (INDUSTRY_NOT_FOUND)를 반환합니다.
    """
    return await service.get_industry(industry_code)
