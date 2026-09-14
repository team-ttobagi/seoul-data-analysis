from pydantic import BaseModel, ConfigDict, Field


class IndustryBase(BaseModel):
    code: str = Field(description="서비스 업종 코드(svc_induty_cd). 매출·분석 API의 industry_code로 사용합니다.")
    name: str = Field(description="업종 선택 드롭다운과 분석 화면에 표시하는 서비스 업종명.")


class IndustryResponse(IndustryBase):
    model_config = ConfigDict(from_attributes=True)
