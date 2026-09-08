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
    return await service.get_all_districts()


@router.get("/{district_code}", response_model=DistrictResponse)
async def get_district_by_code(
    district_code: str,
    service: DistrictService = Depends(get_district_service),
):
    return await service.get_district(district_code)
