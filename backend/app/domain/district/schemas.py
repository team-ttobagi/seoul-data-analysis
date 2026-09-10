from pydantic import BaseModel, ConfigDict, Field


class DistrictResponse(BaseModel):
    signgu_cd: str = Field(description="자치구 코드. 상권의 소속 자치구와 지역 선택값을 연결하는 식별자입니다.")
    signgu_cd_nm: str = Field(description="지역 선택 드롭다운과 상권 정보에 표시하는 자치구명.")

    model_config = ConfigDict(from_attributes=True)
