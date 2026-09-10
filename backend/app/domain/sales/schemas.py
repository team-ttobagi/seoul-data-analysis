from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SalesSummarySchema(BaseModel):
    quarter: str = Field(description="매출 조회 기준 분기. 요청한 quarter 문자열을 그대로 반환합니다.")
    trade_area_code: str = Field(description="매출을 조회한 상권 코드. 요청값의 영문을 대문자로 변환한 값입니다.")
    industry_code: str = Field(description="매출을 조회한 서비스 업종 코드(svc_induty_cd).")
    estimated_sales: int = Field(
        description="선택한 분기·상권·업종의 추정 매출액(원). 원천 데이터의 thsmon_selng_amt입니다.",
    )
    estimated_sales_formatted: str = Field(
        description="매출액 표시 문자열. 1억 원 이상은 억, 1만 원 이상은 만 단위로 축약하며 원 접미사는 포함하지 않습니다.",
    )
    transaction_count: int = Field(
        description="선택한 분기·상권·업종의 거래건수(건). 원천 데이터의 thsmon_selng_co입니다.",
    )
    transaction_count_formatted: str = Field(
        description="거래건수 표시 문자열. 1만 건 이상은 만 단위로 축약하며 건 접미사는 포함하지 않습니다.",
    )
    qoq_growth_rate: Optional[float] = Field(
        default=None,
        description=(
            "QoQ 매출 성장률(GrowthRate, %). (현재 분기 매출 - 전분기 매출) / 전분기 매출 × 100이며, "
            "전분기 매출이 없거나 0 이하이면 null입니다."
        ),
    )
    seoul_rank: Optional[int] = Field(
        default=None,
        description=(
            "동일 분기·동일 업종의 서울 종합 순위. 매출·성장·거래건수·CompetitionScore의 "
            "4개 Benchmark Percentile 평균이 낮을수록 상위이며 동점은 같은 순위입니다. "
            "전분기 매출·거래건수 부재 또는 0 이하, 현재 거래건수 0 이하, 업종별 매출 분포 부재 등으로 "
            "필요한 Percentile을 산출하지 못하면 null입니다."
        ),
    )
    sales_percentile: int = Field(
        description=(
            "동일 분기·동일 업종 내 매출의 Benchmark Percentile을 정수 반올림한 값(%). "
            "매출 내림차순 순위 / 비교 대상 수 × 100이며 낮을수록 상위권입니다."
        ),
    )
    volume_percentile: int = Field(
        description=(
            "동일 분기·동일 업종 내 거래건수의 Benchmark Percentile을 정수 반올림한 값(%). "
            "거래건수 내림차순 순위 / 비교 대상 수 × 100이며 낮을수록 상위권입니다."
        ),
    )


class SalesByDaySchema(BaseModel):
    day: str = Field(description="분석 대상 요일. 월, 화, 수, 목, 금, 토, 일 중 하나입니다.")
    percentage: int = Field(
        description="7개 요일 매출 합계 중 해당 요일의 매출 비중을 정수 반올림한 값(%). 합계가 0이면 0입니다.",
    )
    diff_from_average: int = Field(
        description=(
            "요일 평균 매출 대비 해당 요일의 증감률(%). "
            "(해당 요일 매출 - 7개 요일 평균 매출) / 평균 매출 × 100을 정수 반올림합니다. "
            "모든 요일의 매출이 0이면 현재 계산에서 합계를 1로 대체하므로 -100입니다."
        ),
    )
    is_peak: bool = Field(
        description="7개 요일 중 매출액이 최대인지 여부. 최대 매출액이 같은 요일은 모두 true입니다.",
    )


class SalesByTimeSchema(BaseModel):
    slot: str = Field(
        description="매출 시간대 구간. 00-06시, 06-11시, 11-14시, 14-17시, 17-21시, 21-24시 중 하나입니다.",
    )
    percentage: int = Field(
        description="6개 시간대 매출 합계 중 해당 시간대의 매출 비중을 정수 반올림한 값(%). 합계가 0이면 0입니다.",
    )
    sales_amount: int = Field(description="선택한 분기·상권·업종에서 해당 시간대에 발생한 추정 매출액(원).")
    is_peak: bool = Field(
        description="6개 시간대 중 매출액이 최대인지 여부. 최대 매출액이 같은 시간대는 모두 true입니다.",
    )


class SalesByAgeGenderSchema(BaseModel):
    age_group: str = Field(
        description="소비자 연령대. 10대, 20대, 30대, 40대, 50대, 60대+ 중 하나이며 성별과의 교차 집단은 아닙니다.",
    )
    percentage: int = Field(
        description="6개 연령대 매출 합계 중 해당 연령대의 매출 비중을 정수 반올림한 값(%). 고객 수 비중이 아니며 합계가 0이면 0입니다.",
    )
    is_primary: bool = Field(
        description="6개 연령대 중 매출액이 최대인 주요 연령층인지 여부. 최대 매출액이 같은 연령대는 모두 true입니다.",
    )


class SalesGenderSchema(BaseModel):
    female_ratio: int = Field(
        description="여성 매출 / 남녀 매출 합계 × 100을 정수 반올림한 여성 매출 비중(%). 성별 매출 합계가 0이면 0입니다.",
    )
    male_ratio: int = Field(
        description="100에서 female_ratio를 뺀 남성 매출 비중(%). 성별 매출 합계가 0이면 100입니다.",
    )
    dominant_gender: str = Field(
        description="정수 비중 기준 주요 소비 성별. female_ratio가 male_ratio 이상이면 female, 작으면 male이며 동률은 female입니다.",
    )
