from typing import Optional
from pydantic import BaseModel, ConfigDict


class IndustryBase(BaseModel):
    code: str
    name: str
    category: Optional[str] = None
    description: Optional[str] = None


class IndustryResponse(IndustryBase):
    model_config = ConfigDict(from_attributes=True)
