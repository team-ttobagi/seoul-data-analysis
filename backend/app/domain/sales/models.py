from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.domain.industry.models import ServiceIndustryModel
    from backend.app.domain.trade_area.models import TradeAreaModel


class SalesDataModel(Base):
    __tablename__ = "sales_data"

    sales_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    stdr_yyqu_cd: Mapped[str] = mapped_column(String, nullable=False)
    trdar_cd: Mapped[str] = mapped_column(String, ForeignKey("trade_area.trdar_cd"), nullable=False)
    svc_induty_cd: Mapped[str] = mapped_column(
        String,
        ForeignKey("service_industry.svc_induty_cd"),
        nullable=False,
    )

    trade_area: Mapped["TradeAreaModel"] = relationship(
        "TradeAreaModel",
        back_populates="sales_data",
    )
    service_industry: Mapped["ServiceIndustryModel"] = relationship(
        "ServiceIndustryModel",
        back_populates="sales_data",
    )

    thsmon_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    thsmon_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mdwk_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    wkend_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mdwk_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    wkend_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)

    mon_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tues_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    wed_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    thur_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fri_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sat_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sun_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mon_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tues_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    wed_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    thur_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fri_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sat_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sun_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)

    tmzon_00_06_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_06_11_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_11_14_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_14_17_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_17_21_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_21_24_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_00_06_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_06_11_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_11_14_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_14_17_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_17_21_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    tmzon_21_24_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)

    ml_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fml_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ml_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    fml_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)

    agrde_10_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_20_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_30_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_40_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_50_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_60_above_selng_amt: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_10_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_20_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_30_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_40_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_50_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)
    agrde_60_above_selng_co: Mapped[int] = mapped_column(BigInteger, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "stdr_yyqu_cd",
            "trdar_cd",
            "svc_induty_cd",
            name="uq_sales_data_period_area_industry",
        ),
    )
