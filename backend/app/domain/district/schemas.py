from pydantic import BaseModel, ConfigDict


class DistrictResponse(BaseModel):
    signgu_cd: str
    signgu_cd_nm: str

    model_config = ConfigDict(from_attributes=True)
