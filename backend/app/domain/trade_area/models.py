from sqlalchemy import Column, String, Text, DateTime, func
from backend.app.core.database import Base


class TradeAreaModel(Base):
    __tablename__ = "trade_area"

    code = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    district = Column(String(50), nullable=False, index=True)  # 성동구, 마포구, etc.
    trade_type = Column(String(50), nullable=False)  # 발달상권, 골목상권, etc.
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
