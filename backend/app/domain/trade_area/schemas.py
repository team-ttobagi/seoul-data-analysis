from typing import Optional
from pydantic import BaseModel, ConfigDict


class TradeAreaBase(BaseModel):
    trdar_cd: str
    trdar_se_cd: str
    trdar_cd_nm: str
    signgu_cd: str
    signgu_cd_nm: Optional[str] = None


class TradeAreaResponse(TradeAreaBase):
    model_config = ConfigDict(from_attributes=True)
