from sqlalchemy import Column, Integer, BigInteger, Numeric, String, Boolean, DateTime, func, Index
from backend.app.core.database import Base


class SalesSummaryModel(Base):
    __tablename__ = "sales_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quarter = Column(String(20), nullable=False, index=True)
    trade_area_code = Column(String(50), nullable=False, index=True)
    industry_code = Column(String(50), nullable=False, index=True)
    estimated_sales = Column(BigInteger, nullable=False)  # in KRW
    transaction_count = Column(Integer, nullable=False)
    qoq_growth_rate = Column(Numeric(5, 2), nullable=False)  # e.g. 12.40%
    seoul_rank = Column(Integer, nullable=False)
    sales_percentile = Column(Integer, nullable=False)
    volume_percentile = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_sales_quarter_ta_ind", "quarter", "trade_area_code", "industry_code"),
    )


class SalesByDayModel(Base):
    __tablename__ = "sales_by_day"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quarter = Column(String(20), nullable=False, index=True)
    trade_area_code = Column(String(50), nullable=False, index=True)
    industry_code = Column(String(50), nullable=False, index=True)
    day_name = Column(String(10), nullable=False)  # 월, 화, 수, 목, 금, 토, 일
    sales_percentage = Column(Integer, nullable=False)
    diff_from_average = Column(Integer, nullable=False)
    is_peak = Column(Boolean, default=False)


class SalesByTimeModel(Base):
    __tablename__ = "sales_by_time"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quarter = Column(String(20), nullable=False, index=True)
    trade_area_code = Column(String(50), nullable=False, index=True)
    industry_code = Column(String(50), nullable=False, index=True)
    time_slot = Column(String(20), nullable=False)  # 06-11시, 11-14시, etc.
    sales_percentage = Column(Integer, nullable=False)
    sales_amount = Column(BigInteger, nullable=False)
    is_peak = Column(Boolean, default=False)


class SalesByAgeGenderModel(Base):
    __tablename__ = "sales_by_age_gender"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quarter = Column(String(20), nullable=False, index=True)
    trade_area_code = Column(String(50), nullable=False, index=True)
    industry_code = Column(String(50), nullable=False, index=True)
    age_group = Column(String(20), nullable=False)  # 10대, 20대, 30대, 40대+
    sales_percentage = Column(Integer, nullable=False)
    female_ratio = Column(Integer, nullable=False)
    male_ratio = Column(Integer, nullable=False)
    is_primary = Column(Boolean, default=False)


class StoreSummaryModel(Base):
    __tablename__ = "store_summary"

    id = Column(Integer, primary_key=True, autoincrement=True)
    quarter = Column(String(20), nullable=False, index=True)
    trade_area_code = Column(String(50), nullable=False, index=True)
    industry_code = Column(String(50), nullable=False, index=True)
    store_count = Column(Integer, nullable=False)
    store_count_change = Column(Integer, nullable=False)
    competition_level = Column(String(20), nullable=False)
    sales_level = Column(String(20), nullable=False)
    volume_level = Column(String(20), nullable=False)
    warning_text = Column(String(255), nullable=True)
