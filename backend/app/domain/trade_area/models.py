from typing import TYPE_CHECKING, List

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.domain.sales.models import SalesDataModel


class TradeAreaTypeModel(Base):
    __tablename__ = "trade_area_type"

    trdar_se_cd: Mapped[str] = mapped_column(String, primary_key=True)
    trdar_se_cd_nm: Mapped[str] = mapped_column(String, nullable=False)

    trade_areas: Mapped[List["TradeAreaModel"]] = relationship(
        "TradeAreaModel",
        back_populates="trade_area_type",
    )


class TradeAreaModel(Base):
    __tablename__ = "trade_area"

    trdar_cd: Mapped[str] = mapped_column(String, primary_key=True)
    trdar_se_cd: Mapped[str] = mapped_column(
        String,
        ForeignKey("trade_area_type.trdar_se_cd"),
        nullable=False,
    )
    trdar_cd_nm: Mapped[str] = mapped_column(String, nullable=False)

    trade_area_type: Mapped["TradeAreaTypeModel"] = relationship(
        "TradeAreaTypeModel",
        back_populates="trade_areas",
    )
    sales_data: Mapped[List["SalesDataModel"]] = relationship(
        "SalesDataModel",
        back_populates="trade_area",
    )
