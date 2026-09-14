from typing import List, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.domain.district.repository import DistrictRepository
from backend.app.domain.district.schemas import DistrictResponse
from backend.app.domain.district.service import DistrictService

router = APIRouter(prefix="/districts", tags=["District"])


def get_district_service(
    db: Optional[AsyncSession] = Depends(get_db),
) -> DistrictService:
    return DistrictService(repository=DistrictRepository(session=db))


@router.get("", response_model=List[DistrictResponse])
async def list_districts(
    service: DistrictService = Depends(get_district_service),
):
    """지역 선택 드롭다운에 사용하는 전체 자치구 목록을 반환합니다.

    등록된 자치구의 코드와 이름을 자치구 코드 오름차순으로 조회합니다.
    업종이나 분기에 따른 필터 없이 반환하며, 상권 데이터의 signgu_cd와
    연결해 지역 선택에 사용합니다. 등록된 자치구가 없거나 DB 연결 또는
    조회가 실패하면 빈 배열을 반환합니다.
    """
    return await service.get_all_districts()


@router.get("/{district_code}", response_model=DistrictResponse)
async def get_district_by_code(
    district_code: str,
    service: DistrictService = Depends(get_district_service),
):
    """자치구 코드에 해당하는 자치구의 코드와 이름을 반환합니다.

    district_code 앞뒤의 공백을 제거한 뒤 등록된 자치구 코드와 일치하는
    자치구를 조회합니다. 자치구가 없거나 DB 연결 또는 조회가 실패하면
    HTTP 404 (DISTRICT_NOT_FOUND)를 반환합니다.
    """
    return await service.get_district(district_code)
