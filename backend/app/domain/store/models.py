from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.domain.industry.models import ServiceIndustryModel
    from backend.app.domain.trade_area.models import TradeAreaModel


class StoreModel(Base):
    __tablename__ = "store_data"

    store_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stdr_yyqu_cd: Mapped[str] = mapped_column(String, nullable=False)
    trdar_cd: Mapped[str] = mapped_column(
        String,
        ForeignKey("trade_area.trdar_cd"),
        nullable=False,
    )
    svc_induty_cd: Mapped[str] = mapped_column(
        String,
        ForeignKey("service_industry.svc_induty_cd"),
        nullable=False,
    )

    trade_area: Mapped["TradeAreaModel"] = relationship(
        "TradeAreaModel",
        back_populates="store_data",
    )
    service_industry: Mapped["ServiceIndustryModel"] = relationship(
        "ServiceIndustryModel",
        back_populates="store_data",
    )

    similr_induty_stor_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    stor_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    frc_stor_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    opbiz_rt: Mapped[float] = mapped_column(Float, nullable=False)
    opbiz_stor_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    clsbiz_rt: Mapped[float] = mapped_column(Float, nullable=False)
    clsbiz_stor_co: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "stdr_yyqu_cd",
            "trdar_cd",
            "svc_induty_cd",
            name="uq_store_data_period_area_industry",
        ),
    )
