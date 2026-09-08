from typing import List

from backend.app.core.exceptions import DistrictNotFoundException
from backend.app.domain.district.repository import DistrictRepository
from backend.app.domain.district.schemas import DistrictResponse


class DistrictService:
    def __init__(self, repository: DistrictRepository):
        self.repository = repository

    async def get_all_districts(self) -> List[DistrictResponse]:
        districts = await self.repository.get_all()
        return [DistrictResponse(**district) for district in districts]

    async def get_district(self, code: str) -> DistrictResponse:
        district = await self.repository.get_by_code(code)
        if not district:
            raise DistrictNotFoundException(district_code=code)
        return DistrictResponse(**district)
