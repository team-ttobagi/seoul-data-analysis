import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.domain.industry.models import ServiceIndustryModel

logger = logging.getLogger(__name__)


class IndustryRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all(self) -> List[dict]:
        if not self.session:
            return []

        try:
            stmt = select(ServiceIndustryModel)
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            return [
                {
                    "code": r.svc_induty_cd,
                    "name": r.svc_induty_cd_nm,
                    "category": None,
                    "description": None,
                }
                for r in rows
            ]
        except Exception:
            logger.exception("Failed to load industries from DB")
            return []

    async def get_by_code(self, code: str) -> Optional[dict]:
        if not self.session:
            return None

        try:
            stmt = select(ServiceIndustryModel).where(ServiceIndustryModel.svc_induty_cd == code)
            result = await self.session.execute(stmt)
            r = result.scalar_one_or_none()
            if not r:
                return None
            return {
                "code": r.svc_induty_cd,
                "name": r.svc_induty_cd_nm,
                "category": None,
                "description": None,
            }
        except Exception:
            logger.exception("Failed to load industry '%s' from DB", code)
            return None
