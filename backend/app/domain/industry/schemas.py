from typing import Optional
from pydantic import BaseModel, ConfigDict


class IndustryBase(BaseModel):
    svc_induty_cd: str
    svc_induty_cd_nm: str


class IndustryResponse(IndustryBase):
    model_config = ConfigDict(from_attributes=True)
