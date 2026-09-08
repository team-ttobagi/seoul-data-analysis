from pydantic import BaseModel, ConfigDict


class IndustryBase(BaseModel):
    code: str
    name: str


class IndustryResponse(IndustryBase):
    model_config = ConfigDict(from_attributes=True)
