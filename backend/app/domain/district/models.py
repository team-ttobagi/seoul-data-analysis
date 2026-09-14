from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.domain.trade_area.models import TradeAreaModel


class DistrictModel(Base):
    __tablename__ = "district"

    signgu_cd: Mapped[str] = mapped_column(String, primary_key=True)
    signgu_cd_nm: Mapped[str] = mapped_column(String, nullable=False)

    trade_areas: Mapped[List["TradeAreaModel"]] = relationship(
        "TradeAreaModel",
        back_populates="district",
    )
