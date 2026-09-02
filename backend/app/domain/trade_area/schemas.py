from typing import Optional
from pydantic import BaseModel, ConfigDict


class TradeAreaBase(BaseModel):
    code: str
    name: str
    district: str
    type: str
    description: Optional[str] = None


class TradeAreaResponse(TradeAreaBase):
    model_config = ConfigDict(from_attributes=True)
