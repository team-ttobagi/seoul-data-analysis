import pytest
from sqlalchemy import func, select

from backend.app.core.database import AsyncSessionLocal
from backend.app.domain.sales.models import SalesDataModel
from backend.app.domain.sales.sync_service import SalesSyncService
from backend.app.external.seoul_openapi import SeoulOpenAPIClient


@pytest.mark.asyncio
async def test_sales_sync_to_supabase():
    # 1. 실제 서울 API 데이터 수집
    api_client = SeoulOpenAPIClient()
    rows = await api_client.fetch_all("20261")

    assert rows

    # 처음에는 1건만 테스트
    test_row = rows[0]

    quarter = str(test_row["STDR_YYQU_CD"])
    trdar_cd = str(test_row["TRDAR_CD"])
    svc_induty_cd = str(test_row["SVC_INDUTY_CD"])

    async with AsyncSessionLocal() as session:
        service = SalesSyncService(session)

        # 2. 첫 번째 적재
        result = await service.sync([test_row])

        assert result == 1

        # 3. 실제 DB에 저장됐는지 확인
        stmt = (
            select(func.count())
            .select_from(SalesDataModel)
            .where(
                SalesDataModel.stdr_yyqu_cd == quarter,
                SalesDataModel.trdar_cd == trdar_cd,
                SalesDataModel.svc_induty_cd == svc_induty_cd,
            )
        )

        count = await session.scalar(stmt)

        assert count == 1

        # 4. 같은 데이터 재실행
        result = await service.sync([test_row])

        assert result == 1

        count = await session.scalar(stmt)

        # 재실행해도 중복되면 안 됨
        assert count == 1
