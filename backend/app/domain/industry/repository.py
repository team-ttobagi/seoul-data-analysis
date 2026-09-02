from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.domain.industry.models import ServiceIndustryModel


class IndustryRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all(self) -> List[dict]:
        if self.session:
            try:
                stmt = select(ServiceIndustryModel)
                result = await self.session.execute(stmt)
                rows = result.scalars().all()
                if rows:
                    return [
                        {
                            "code": r.code,
                            "name": r.name,
                            "category": r.category,
                            "description": r.description,
                        }
                        for r in rows
                    ]
            except Exception:
                pass

        return [
            {"code": "CS100010", "name": "커피·음료", "category": "외식업", "description": "카페, 디저트 및 음료 전문점"},
            {"code": "CS100001", "name": "한식", "category": "외식업", "description": "한식 일반 음식점 및 식당"},
            {"code": "CS100007", "name": "치킨", "category": "외식업", "description": "치킨 및 닭강정 전문점"},
            {"code": "CS200001", "name": "편의점", "category": "서비스업", "description": "종합 편의점 및 소매 유통"},
            {"code": "CS300001", "name": "의류", "category": "도소매업", "description": "패션, 캐주얼 및 부티크 의류"},
            {"code": "CS300002", "name": "미용", "category": "서비스업", "description": "헤어샵, 네일 및 뷰티 케어"},
        ]

    async def get_by_code(self, code: str) -> Optional[dict]:
        all_items = await self.get_all()
        for item in all_items:
            if item["code"].upper() == code.upper():
                return item
        return None
