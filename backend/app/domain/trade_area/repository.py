from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.domain.trade_area.models import TradeAreaModel


class TradeAreaRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all(self) -> List[dict]:
        # If DB session is available, query DB; otherwise use deterministic in-memory store
        if self.session:
            try:
                stmt = select(TradeAreaModel)
                result = await self.session.execute(stmt)
                rows = result.scalars().all()
                if rows:
                    return [
                        {
                            "code": r.code,
                            "name": r.name,
                            "district": r.district,
                            "type": r.trade_type,
                            "description": r.description,
                        }
                        for r in rows
                    ]
            except Exception:
                pass

        # In-memory fallback
        return [
            {"code": "SEONGSU", "name": "성수동", "district": "성동구", "type": "발달상권", "description": "트렌드 카페 및 복합 문화공간 밀집지"},
            {"code": "HONGDAE", "name": "홍대입구", "district": "마포구", "type": "발달상권", "description": "청년 문화, 예술 및 유동인구 최대 상권"},
            {"code": "SHAROSU", "name": "샤로수길", "district": "관악구", "type": "골목상권", "description": "서울대입구 1인 가구 및 청년 밀집 골목상권"},
            {"code": "KONKUK", "name": "건대입구", "district": "광진구", "type": "발달상권", "description": "대학생 및 동부권 핵심 엔터테인먼트 상권"},
            {"code": "GANGNAM", "name": "강남역", "district": "강남구", "type": "광역상권", "description": "서울 최대 오피스 직장인 및 교통 요충지"},
            {"code": "GAROSU", "name": "가로수길", "district": "강남구", "type": "발달상권", "description": "신사동 패션 및 고급 디저트 거리"},
            {"code": "IKSEON", "name": "익선동", "district": "종로구", "type": "관광특구", "description": "한옥 리모델링 감성 카페거리"},
            {"code": "EULJIRO", "name": "을지로3가", "district": "중구", "type": "골목상권", "description": "뉴트로 힙지로 문화 및 직장인 상권"},
        ]

    async def get_by_code(self, code: str) -> Optional[dict]:
        all_items = await self.get_all()
        for item in all_items:
            if item["code"].upper() == code.upper():
                return item
        return None
