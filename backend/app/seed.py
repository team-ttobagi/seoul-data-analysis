import asyncio

from backend.app.core.database import AsyncSessionLocal, Base, engine
from backend.app.domain.district.models import DistrictModel
from backend.app.domain.industry.models import ServiceIndustryModel
from backend.app.domain.trade_area.models import TradeAreaModel, TradeAreaTypeModel


async def seed_database() -> None:
    print("[SEOUL DATA PLAYGROUND] Initializing and Seeding Database...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    districts = [
        DistrictModel(signgu_cd=code, signgu_cd_nm=name)
        for code, name in (("11200", "성동구"), ("11440", "마포구"), ("11620", "관악구"), ("11215", "광진구"), ("11680", "강남구"), ("11110", "종로구"), ("11140", "중구"))
    ]
    trade_area_types = [
        TradeAreaTypeModel(trdar_se_cd=code, trdar_se_cd_nm=name)
        for code, name in (("A", "발달상권"), ("B", "골목상권"), ("C", "광역상권"), ("D", "관광특구"))
    ]
    trade_areas = [
        TradeAreaModel(trdar_cd=code, trdar_se_cd=area_type, trdar_cd_nm=name, signgu_cd=district)
        for code, area_type, name, district in (
            ("SEONGSU", "A", "성수동", "11200"), ("HONGDAE", "A", "홍대입구", "11440"),
            ("SHAROSU", "B", "샤로수길", "11620"), ("KONKUK", "A", "건대입구", "11215"),
            ("GANGNAM", "C", "강남역", "11680"), ("GAROSU", "A", "가로수길", "11680"),
            ("IKSEON", "D", "익선동", "11110"), ("EULJIRO", "B", "을지로3가", "11140"),
        )
    ]
    industries = [
        ServiceIndustryModel(svc_induty_cd=code, svc_induty_cd_nm=name)
        for code, name in (("CS100010", "커피·음료"), ("CS100001", "한식"), ("CS100007", "치킨"), ("CS200001", "편의점"), ("CS300001", "의류"), ("CS300002", "미용"))
    ]

    async with AsyncSessionLocal() as session:
        session.add_all(districts + trade_area_types + trade_areas + industries)
        try:
            await session.commit()
            print("[SEOUL DATA PLAYGROUND] Database successfully seeded.")
        except Exception as exc:
            await session.rollback()
            print(f"[SEOUL DATA PLAYGROUND] Seed failed: {exc}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
