from typing import Optional
from pydantic import BaseModel, ConfigDict


class IndustryBase(BaseModel):
    code: str
    name: str
    category: str
    description: Optional[str] = None


class IndustryResponse(IndustryBase):
    model_config = ConfigDict(from_attributes=True)
