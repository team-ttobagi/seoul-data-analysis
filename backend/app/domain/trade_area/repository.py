import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import exists, select
from sqlalchemy.orm import selectinload
from backend.app.domain.sales.models import SalesDataModel
from backend.app.domain.trade_area.models import TradeAreaModel

logger = logging.getLogger(__name__)


class TradeAreaRepository:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session

    async def get_all(self) -> List[dict]:
        if not self.session:
            return []

        try:
            stmt = (
                select(TradeAreaModel)
                .options(selectinload(TradeAreaModel.district))
                .order_by(
                    TradeAreaModel.trdar_cd_nm,
                    TradeAreaModel.trdar_cd,
                )
            )
            result = await self.session.execute(stmt)
            rows = result.scalars().all()
            return [_to_dict(r) for r in rows]
        except Exception:
            logger.exception("Failed to load trade areas from DB")
            return []

    async def get_by_code(self, code: str) -> Optional[dict]:
        if not self.session:
            return None

        try:
            stmt = (
                select(TradeAreaModel)
                .options(selectinload(TradeAreaModel.district))
                .where(TradeAreaModel.trdar_cd == code)
            )
            result = await self.session.execute(stmt)
            r = result.scalar_one_or_none()
            return _to_dict(r) if r else None
        except Exception:
            logger.exception("Failed to load trade area '%s' from DB", code)
            return None

    async def get_by_filters(
        self,
        industry_code: str,
        signgu_cd: str,
        quarter: str,
    ) -> List[dict]:
        if not self.session:
            return []

        try:
            matching_sales = exists(
                select(SalesDataModel.sales_id).where(
                    SalesDataModel.trdar_cd == TradeAreaModel.trdar_cd,
                    SalesDataModel.svc_induty_cd == industry_code.strip(),
                    SalesDataModel.stdr_yyqu_cd == quarter.strip(),
                )
            )
            stmt = (
                select(TradeAreaModel)
                .options(selectinload(TradeAreaModel.district))
                .where(
                    TradeAreaModel.signgu_cd == signgu_cd.strip(),
                    matching_sales,
                )
            )
            stmt = stmt.order_by(
                TradeAreaModel.trdar_cd_nm,
                TradeAreaModel.trdar_cd,
            )

            result = await self.session.execute(stmt)
            rows = result.scalars().all()

            return [_to_dict(r) for r in rows]

        except Exception:
            logger.exception(
                "Failed to load trade areas by industry '%s', district '%s', quarter '%s'",
                industry_code,
                signgu_cd,
                quarter,
            )
            return []


def _to_dict(r: TradeAreaModel) -> dict:
    return {
        "trdar_cd": r.trdar_cd,
        "trdar_se_cd": r.trdar_se_cd,
        "trdar_cd_nm": r.trdar_cd_nm,
        "signgu_cd": r.signgu_cd,
        "signgu_cd_nm": r.district.signgu_cd_nm if r.district else None,
    }
