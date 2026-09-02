import asyncio
from backend.app.core.database import engine, Base, AsyncSessionLocal
from backend.app.domain.trade_area.models import TradeAreaModel
from backend.app.domain.industry.models import ServiceIndustryModel
from backend.app.domain.sales.models import (
    SalesSummaryModel,
    SalesByDayModel,
    SalesByTimeModel,
    SalesByAgeGenderModel,
    StoreSummaryModel,
)


async def seed_database():
    print("[SEOUL DATA PLAYGROUND] Initializing and Seeding Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Seed Trade Areas
        trade_areas = [
            TradeAreaModel(code="SEONGSU", name="성수동", district="성동구", trade_type="발달상권", description="트렌드 카페 및 복합 문화공간 밀집지"),
            TradeAreaModel(code="HONGDAE", name="홍대입구", district="마포구", trade_type="발달상권", description="청년 문화, 예술 및 유동인구 최대 상권"),
            TradeAreaModel(code="SHAROSU", name="샤로수길", district="관악구", trade_type="골목상권", description="서울대입구 1인 가구 및 청년 밀집 골목상권"),
            TradeAreaModel(code="KONKUK", name="건대입구", district="광진구", trade_type="발달상권", description="대학생 및 동부권 핵심 엔터테인먼트 상권"),
            TradeAreaModel(code="GANGNAM", name="강남역", district="강남구", trade_type="광역상권", description="서울 최대 오피스 직장인 및 교통 요충지"),
            TradeAreaModel(code="GAROSU", name="가로수길", district="강남구", trade_type="발달상권", description="신사동 패션 및 고급 디저트 거리"),
            TradeAreaModel(code="IKSEON", name="익선동", district="종로구", trade_type="관광특구", description="한옥 리모델링 감성 카페거리"),
            TradeAreaModel(code="EULJIRO", name="을지로3가", district="중구", trade_type="골목상권", description="뉴트로 힙지로 문화 및 직장인 상권"),
        ]

        # Seed Industries
        industries = [
            ServiceIndustryModel(code="CS100010", name="커피·음료", category="외식업", description="카페, 디저트 및 음료 전문점"),
            ServiceIndustryModel(code="CS100001", name="한식", category="외식업", description="한식 일반 음식점 및 식당"),
            ServiceIndustryModel(code="CS100007", name="치킨", category="외식업", description="치킨 및 닭강정 전문점"),
            ServiceIndustryModel(code="CS200001", name="편의점", category="서비스업", description="종합 편의점 및 소매 유통"),
            ServiceIndustryModel(code="CS300001", name="의류", category="도소매업", description="패션, 캐주얼 및 부티크 의류"),
            ServiceIndustryModel(code="CS300002", name="미용", category="서비스업", description="헤어샵, 네일 및 뷰티 케어"),
        ]

        session.add_all(trade_areas)
        session.add_all(industries)

        try:
            await session.commit()
            print("[SEOUL DATA PLAYGROUND] Database successfully seeded.")
        except Exception as e:
            await session.rollback()
            print(f"[SEOUL DATA PLAYGROUND] Seed note: {e}")


if __name__ == "__main__":
    asyncio.run(seed_database())
