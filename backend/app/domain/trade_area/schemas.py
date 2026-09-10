from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TradeAreaBase(BaseModel):
    trdar_cd: str = Field(description="상권 고유 코드. 상권 상세·매출·분석 API의 trade_area_code로 사용합니다.")
    trdar_se_cd: str = Field(description="상권 구분 코드. trade_area_type에 등록된 상권 유형을 식별합니다.")
    trdar_cd_nm: str = Field(description="상권 검색·선택 목록과 상세 화면에 표시하는 상권명.")
    signgu_cd: str = Field(description="상권이 속한 자치구 코드. 자치구 API의 signgu_cd와 대응합니다.")
    signgu_cd_nm: Optional[str] = Field(
        default=None,
        description="상권이 속한 자치구명. 연결된 자치구 정보가 없으면 null입니다.",
    )


class TradeAreaResponse(TradeAreaBase):
    model_config = ConfigDict(from_attributes=True)
