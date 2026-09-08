from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.district.models import DistrictModel


class DistrictRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all(self) -> List[dict]:
        if self.session:
            try:
                result = await self.session.execute(
                    select(DistrictModel).order_by(DistrictModel.signgu_cd)
                )
                rows = result.scalars().all()
                if rows:
                    return [
                        {
                            "signgu_cd": row.signgu_cd,
                            "signgu_cd_nm": row.signgu_cd_nm,
                        }
                        for row in rows
                    ]
            except Exception:
                pass

        return [
            {"signgu_cd": code, "signgu_cd_nm": name}
            for code, name in (
                ("11680", "강남구"),
                ("11500", "강서구"),
                ("11440", "마포구"),
                ("11620", "관악구"),
                ("11215", "광진구"),
                ("11110", "종로구"),
                ("11140", "중구"),
                ("11200", "성동구"),
            )
        ]

    async def get_by_code(self, code: str) -> Optional[dict]:
        normalized_code = code.strip()
        for district in await self.get_all():
            if district["signgu_cd"] == normalized_code:
                return district
        return None
