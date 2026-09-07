from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base

if TYPE_CHECKING:
    from backend.app.domain.sales.models import SalesDataModel


class ServiceIndustryModel(Base):
    __tablename__ = "service_industry"

    svc_induty_cd: Mapped[str] = mapped_column(String, primary_key=True)
    svc_induty_cd_nm: Mapped[str] = mapped_column(String, nullable=False)

    sales_data: Mapped[List["SalesDataModel"]] = relationship(
        "SalesDataModel",
        back_populates="service_industry",
    )
