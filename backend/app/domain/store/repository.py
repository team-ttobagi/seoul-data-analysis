import logging
import re
from typing import Dict, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.domain.store.models import StoreModel
from backend.app.domain.store.schemas import StoreTrendSchema

logger = logging.getLogger(__name__)


def _normalize_quarter(quarter: str) -> str:
    """API에서 사용하는 YYYY QN 형식을 DB의 YYYYN 분기 코드로 변환합니다."""
    match = re.match(r"\s*(\d{4})\s*[Qq]?\s*(\d)\s*$", quarter)
    if match:
        return f"{match.group(1)}{match.group(2)}"
    return quarter.strip()


def _previous_quarter(quarter_code: str) -> str:
    """DB 분기 코드(YYYYN)의 직전 분기 코드를 반환합니다."""
    if len(quarter_code) != 5 or not quarter_code[:4].isdigit() or not quarter_code[4].isdigit():
        raise ValueError(f"Invalid quarter code: {quarter_code}")

    year, quarter = int(quarter_code[:4]), int(quarter_code[4])
    if quarter not in (1, 2, 3, 4):
        raise ValueError(f"Invalid quarter number: {quarter}")
    if quarter == 1:
        return f"{year - 1}4"
    return f"{year}{quarter - 1}"


class StoreRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_store_summary(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> Optional[dict]:
        """기준 분기·상권·서비스 업종 조합의 점포 통계 한 건을 조회합니다."""
        normalized_trade_area_code = trade_area_code.strip().upper()
        normalized_industry_code = industry_code.strip()
        quarter_code = _normalize_quarter(quarter)

        stmt = select(StoreModel).where(
            StoreModel.stdr_yyqu_cd == quarter_code,
            StoreModel.trdar_cd == normalized_trade_area_code,
            StoreModel.svc_induty_cd == normalized_industry_code,
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()

        if not row:
            return None

        return {
            "quarter": quarter,
            "trade_area_code": row.trdar_cd,
            "industry_code": row.svc_induty_cd,
            "store_count": row.similr_induty_stor_co,
            "general_store_count": row.stor_co,
            "franchise_store_count": row.frc_stor_co,
            "opening_rate": row.opbiz_rt,
            "opening_store_count": row.opbiz_stor_co,
            "closing_rate": row.clsbiz_rt,
            "closing_store_count": row.clsbiz_stor_co,
        }

    async def get_store_trend(
        self,
        trade_area_code: str,
        industry_code: str,
        quarter: str,
    ) -> Optional[StoreTrendSchema]:
        """상권 한 곳의 현재·직전 분기 점포 추이를 조회합니다."""
        normalized_trade_area_code = trade_area_code.strip().upper()
        trends = await self.get_store_trends(
            trade_area_codes=[normalized_trade_area_code],
            industry_code=industry_code,
            quarter=quarter,
        )
        return trends.get(normalized_trade_area_code)

    async def get_store_trends(
        self,
        trade_area_codes: Sequence[str],
        industry_code: str,
        quarter: str,
    ) -> Dict[str, StoreTrendSchema]:
        """여러 상권의 현재·직전 분기 점포 수를 한 번에 조회해 추이 DTO로 반환합니다."""
        normalized_trade_area_codes = list(
            dict.fromkeys(
                code.strip().upper()
                for code in trade_area_codes
                if code.strip()
            )
        )
        if not normalized_trade_area_codes:
            return {}

        normalized_industry_code = industry_code.strip()
        current_quarter = _normalize_quarter(quarter)
        previous_quarter = _previous_quarter(current_quarter)

        stmt = select(StoreModel).where(
            StoreModel.stdr_yyqu_cd.in_([current_quarter, previous_quarter]),
            StoreModel.trdar_cd.in_(normalized_trade_area_codes),
            StoreModel.svc_induty_cd == normalized_industry_code,
        )
        result = await self.session.execute(stmt)
        rows = {
            (row.trdar_cd, row.stdr_yyqu_cd): row
            for row in result.scalars().all()
        }

        trends: Dict[str, StoreTrendSchema] = {}
        for normalized_trade_area_code in normalized_trade_area_codes:
            current_row = rows.get(
                (normalized_trade_area_code, current_quarter)
            )
            previous_row = rows.get(
                (normalized_trade_area_code, previous_quarter)
            )
            if current_row is None:
                continue

            current_store_count = int(current_row.similr_induty_stor_co)
            previous_store_count = (
                int(previous_row.similr_induty_stor_co)
                if previous_row is not None
                else None
            )
            trends[normalized_trade_area_code] = StoreTrendSchema(
                store_count=current_store_count,
                store_count_change=(
                    current_store_count - previous_store_count
                    if previous_store_count is not None
                    else None
                ),
            )

        return trends
