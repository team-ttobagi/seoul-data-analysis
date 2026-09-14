import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.district.models import DistrictModel

logger = logging.getLogger(__name__)


class DistrictRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all(self) -> List[dict]:
        if not self.session:
            return []

        try:
            result = await self.session.execute(
                select(DistrictModel).order_by(DistrictModel.signgu_cd)
            )
            rows = result.scalars().all()
            return [
                {"signgu_cd": row.signgu_cd, "signgu_cd_nm": row.signgu_cd_nm}
                for row in rows
            ]
        except Exception:
            logger.exception("Failed to load districts from DB")
            return []

    async def get_by_code(self, code: str) -> Optional[dict]:
        if not self.session:
            return None

        try:
            stmt = select(DistrictModel).where(DistrictModel.signgu_cd == code.strip())
            result = await self.session.execute(stmt)
            r = result.scalar_one_or_none()
            if not r:
                return None
            return {"signgu_cd": r.signgu_cd, "signgu_cd_nm": r.signgu_cd_nm}
        except Exception:
            logger.exception("Failed to load district '%s' from DB", code)
            return None
