from typing import List
from backend.app.domain.industry.repository import IndustryRepository
from backend.app.domain.industry.schemas import IndustryResponse
from backend.app.core.exceptions import IndustryNotFoundException


class IndustryService:
    def __init__(self, repository: IndustryRepository):
        self.repository = repository

    async def get_all_industries(self) -> List[IndustryResponse]:
        industries = await self.repository.get_all()
        return [IndustryResponse(**ind) for ind in industries]

    async def get_industry(self, code: str) -> IndustryResponse:
        industry = await self.repository.get_by_code(code)
        if not industry:
            raise IndustryNotFoundException(industry_code=code)
        return IndustryResponse(**industry)
