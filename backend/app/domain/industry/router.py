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
    return await service.get_all_industries()


@router.get("/{industry_code}", response_model=IndustryResponse)
async def get_industry_by_code(
    industry_code: str,
    service: IndustryService = Depends(get_industry_service),
):
    return await service.get_industry(industry_code)
