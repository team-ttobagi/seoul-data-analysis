from sqlalchemy import Column, String, Text, DateTime, func
from backend.app.core.database import Base


class ServiceIndustryModel(Base):
    __tablename__ = "service_industry"

    code = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
