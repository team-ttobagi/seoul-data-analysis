from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ScoreComponent(BaseModel):
    value: Optional[float] = Field(
        default=None,
        description=(
            "구성 지표의 값. sales_growth는 QoQ 매출 성장률(%), transaction_volume은 거래건수(건), "
            "competition은 CompetitionScore(점)이다. 전분기 매출이 없거나 0 이하이면 성장률이, "
            "객단가·성장 균형·수요 다양성 중 필요한 값이 없으면 CompetitionScore가 null이다. "
            "현재 추천 API는 ExplorationScore 산출이 가능한 상권만 반환한다."
        ),
    )
    normalized_score: Optional[int] = Field(
        default=None,
        description=(
            "구성 지표의 0~100점 점수를 반올림한 값. sales_growth는 GrowthScore, "
            "transaction_volume은 TransactionScore, competition은 CompetitionScore이며 높을수록 긍정적이다. "
            "성장률·거래건수 또는 경쟁 점수 구성 지표가 부족해 해당 점수를 산출할 수 없으면 null이다."
        ),
    )
    unit: Optional[str] = Field(
        default=None,
        description="구성 지표의 단위. 현재 추천 API는 단위를 별도로 설정하지 않아 null을 반환하며, 실제 단위는 value 설명을 따른다.",
    )
    benchmark_percentile: Optional[int] = Field(
        default=None,
        description=(
            "동일 분기·업종의 서울 상권 중 해당 성장률·거래건수·CompetitionScore의 Benchmark Percentile. "
            "유효 지표의 내림차순 순위 / 유효 비교 대상 수 × 100을 반올림한 상위 N%이며 작을수록 상위권이다. "
            "동점은 같은 최소 순위를 사용하고, 해당 지표가 산출 불가이면 null이다."
        ),
    )


class RecommendationComponents(BaseModel):
    sales_growth: ScoreComponent = Field(
        description="QoQ 매출 성장률과 GrowthScore, 성장률의 Benchmark Percentile. GrowthScore는 성장률을 P5~P95로 제한한 뒤 0~100점으로 정규화한다.",
    )
    transaction_volume: ScoreComponent = Field(
        description="현재 분기 거래건수와 TransactionScore, 거래건수의 Benchmark Percentile. TransactionScore는 거래건수를 log1p 변환한 뒤 0~100점으로 정규화한다.",
    )
    competition: ScoreComponent = Field(
        description=(
            "CompetitionScore와 해당 Benchmark Percentile. TicketScore × 0.50 + GrowthBalanceScore × 0.30 "
            "+ DemandDiversityScore × 0.20으로 산출하는 경쟁 환경 Proxy이며 실제 경쟁 점포 수가 아니다. "
            "높을수록 경쟁 여건이 상대적으로 긍정적이다."
        ),
    )


class RecommendationItemResponse(BaseModel):
    rank: int = Field(description="선택 지역·검색어 조건의 추천 목록에서 ExplorationScore 내림차순으로 부여한 1부터 시작하는 표시 순번. 최대 100개이며 동점에도 연속 순번을 부여한다.")
    trade_area_code: str = Field(description="추천 상권 코드. 상권 상세 조회와 비교 API의 trade_area_code로 사용한다.")
    trade_area_name: str = Field(description="추천 카드에 표시할 상권명. 상권 메타데이터가 없으면 상권 코드를 표시한다.")
    district: str = Field(description="상권이 속한 서울 자치구명. 자치구 정보가 없으면 '-'를 반환한다.")
    score: int = Field(
        description=(
            "추천 카드의 ExplorationScore(0~100점)를 반올림한 값. GrowthScore × 0.40 + "
            "TransactionScore × 0.35 + CompetitionScore × 0.25로 산출하며 높을수록 탐색 우선순위가 높다. "
            "실제 창업 성공 확률을 의미하지 않는다."
        ),
    )
    signals: Dict[str, str] = Field(
        description=(
            "추천 카드의 세 가지 신호. growth는 GrowthScore, transaction은 TransactionScore, "
            "competition은 CompetitionScore의 등급이며 70 이상 high, 40 이상 70 미만 medium, 40 미만 low이다. "
            "competition의 high는 경쟁 여건이 상대적으로 긍정적이라는 뜻이다."
        ),
    )
    components: RecommendationComponents = Field(description="추천 점수의 근거인 성장성·거래 활성도·경쟁 여건별 원본 값, 정규화 점수, 서울 비교 집단 내 상위 비율.")
    insight: str = Field(description="GrowthScore·TransactionScore·CompetitionScore의 높음/보통/낮음 등급을 조합한 추천 카드의 규칙 기반 요약 문장.")
    warning: Optional[str] = Field(
        default=None,
        description="CompetitionScore가 40 미만(경쟁 여건 낮음)이면 표시하는 경쟁 압박 경고. 해당 조건에 해당하지 않으면 null이다.",
    )


class DistrictKpis(BaseModel):
    estimated_sales: int = Field(description="선택한 분기·상권·업종의 추정 매출액(원). 원천 데이터 thsmon_selng_amt에 해당한다.")
    estimated_sales_formatted: str = Field(description="상세 화면 KPI에 표시할 추정 매출액. 1억 원 이상은 '12.8억', 1만 원 이상은 '8500만'처럼 축약한다.")
    transaction_count: int = Field(description="선택한 분기·상권·업종의 거래건수(건). 원천 데이터 thsmon_selng_co에 해당한다.")
    transaction_count_formatted: str = Field(description="상세 화면 KPI에 표시할 거래건수. 1만 건 이상은 '45만'처럼 축약한다.")
    seoul_rank: Optional[int] = Field(
        default=None,
        description=(
            "동일 분기·업종의 서울 전체 상권을 대상으로 한 종합 순위. 매출·성장률·거래건수·CompetitionScore의 "
            "4개 Benchmark Percentile 평균이 낮은 순이며 1위가 최상위, 동점은 같은 최소 순위이다. "
            "전분기 자료 부족 등으로 4개 Percentile 중 하나라도 산출할 수 없으면 null이다."
        ),
    )
    qoq_growth_rate: Optional[float] = Field(
        default=None,
        description="QoQ 매출 성장률(%). (현재 분기 매출 - 직전 분기 매출) / 직전 분기 매출 × 100이며, 직전 분기 데이터가 없거나 매출이 0 이하이면 null이다.",
    )
    sales_percentile: int = Field(description="동일 분기·업종의 서울 상권 중 매출액 기준 상위 N%. 내림차순 최소 순위 / 비교 대상 수 × 100을 반올림하며 작을수록 매출 상위권이다.")
    growth_percentile: Optional[int] = Field(
        default=None,
        description=(
            "동일 분기·업종에서 QoQ 매출 성장률이 유효한 서울 상권 중 성장률 기준 상위 N%. "
            "내림차순 최소 순위 / 유효 비교 대상 수 × 100을 반올림하며 작을수록 상위권이다. "
            "직전 분기 데이터가 없거나 매출이 0 이하여서 성장률을 구할 수 없으면 null이다."
        ),
    )
    volume_percentile: int = Field(description="동일 분기·업종의 서울 상권 중 거래건수 기준 상위 N%. 내림차순 최소 순위 / 비교 대상 수 × 100을 반올림하며 작을수록 거래건수 상위권이다.")
    store_count: Optional[int] = Field(
        default=None,
        description="선택한 분기·상권·업종의 현재 분기 동일 업종 점포 수(개). 현재 분기 점포 데이터가 없으면 null이다.",
    )
    store_count_change: Optional[int] = Field(
        default=None,
        description="동일 업종 점포 수의 전분기 대비 증감 수(개). 현재 또는 직전 분기 점포 데이터가 없으면 null이다.",
    )
    competition_level: Optional[str] = Field(
        default=None,
        description=(
            "CompetitionScore 기준 경쟁 여건 등급. 70 이상 높음, 40 이상 70 미만 보통, 40 미만 낮음이며 "
            "높음은 상대적으로 긍정적인 경쟁 여건을 뜻한다. 실제 경쟁 점포 수가 아닌 Proxy이다. "
            "현재 거래건수 또는 전분기 매출·거래건수가 없거나 0 이하인 경우, 상권 업종별 매출 분포가 없는 경우 "
            "등으로 구성 점수를 구할 수 없으면 null이다."
        ),
    )
    sales_level: Optional[str] = Field(
        default=None,
        description="매출 수준 등급. 반올림 전 sales_percentile을 100에서 뺀 값이 70 이상이면 높음, 40 이상이면 보통, 그 미만이면 낮음이다. 매출 Percentile을 구할 수 없으면 null이다.",
    )
    volume_level: Optional[str] = Field(
        default=None,
        description="거래량 수준 등급. 반올림 전 volume_percentile을 100에서 뺀 값이 70 이상이면 높음, 40 이상이면 보통, 그 미만이면 낮음이다. 거래건수 Percentile을 구할 수 없으면 null이다.",
    )


class DistrictRankingItem(BaseModel):
    rank: int = Field(description="해당 지표의 상위 최대 5개 목록에서 1부터 시작하는 표시 순번. 지표 내림차순이며 동점에도 연속 순번을 부여한다.")
    trade_area_code: str = Field(description="순위에 포함된 상권의 코드.")
    trade_area_name: str = Field(description="순위표에 표시할 상권명. 상권 메타데이터가 없으면 상권 코드를 표시한다.")
    sales_formatted: str = Field(
        description="순위표의 지표 표시값. by_sales는 매출액('12.8억'), by_volume은 거래건수('45만'), by_growth는 QoQ 매출 성장률('+8.2%'), by_score는 ExplorationScore('82점')이다.",
    )
    sales_raw: float = Field(
        description="순위표의 지표 값. by_sales는 매출액(원), by_volume은 거래건수(건), by_growth는 QoQ 매출 성장률(%), by_score는 반올림한 ExplorationScore(점)를 담는다.",
    )
    is_current: bool = Field(description="현재 상세 조회 중인 상권과 일치하는지 여부. 화면에서 해당 순위 행을 강조하는 데 사용한다.")
    score: Optional[int] = Field(
        default=None,
        description="별도 ExplorationScore 필드. 현재 순위 응답에서는 값을 채우지 않아 null이며, by_score의 점수는 sales_raw와 sales_formatted에 담긴다.",
    )
    growth_rate: Optional[float] = Field(
        default=None,
        description="별도 QoQ 매출 성장률 필드. 현재 순위 응답에서는 값을 채우지 않아 null이며, by_growth의 성장률은 sales_raw와 sales_formatted에 담긴다.",
    )
    transaction_count: Optional[int] = Field(
        default=None,
        description="별도 거래건수 필드. 현재 순위 응답에서는 값을 채우지 않아 null이며, by_volume의 거래건수는 sales_raw와 sales_formatted에 담긴다.",
    )


class DistrictOverviewResponse(BaseModel):
    trade_area_code: str = Field(description="상세 분석 대상 상권 코드.")
    trade_area_name: str = Field(description="상세 화면 제목에 표시할 상권명. 상권 메타데이터가 없으면 상권 코드를 표시한다.")
    district: str = Field(description="상세 분석 대상 상권이 속한 서울 자치구명.")
    industry_code: str = Field(description="분석 대상 서비스 업종 코드. 서울 상권 비교 집단과 매출 조회 범위를 결정한다.")
    industry_name: str = Field(description="상세 화면에 표시할 서비스 업종명. 업종명을 조회할 수 없으면 업종 코드를 표시한다.")
    quarter: str = Field(description="분석 대상 분기. 요청한 quarter 값을 그대로 반환하며, 기본 표기는 '2025 Q4'이다.")
    kpis: DistrictKpis = Field(description="상세 화면 상단 KPI와 Benchmark 표시용 매출액, 거래건수, 서울 종합 순위, QoQ 매출 성장률 및 수준 등급.")
    why_explore: Dict[str, Any] = Field(
        description=(
            "상세 화면의 탐색 이유. growth_rate는 QoQ 매출 성장률(%), growth_percentile은 성장률 상위 N%, "
            "volume_formatted는 축약한 거래건수, volume_percentile은 거래건수 상위 N%이며 kpis와 같은 값이다. "
            "store_count는 동일 업종 점포 수(개), competition_text는 경쟁 여건 등급 표시 문구이다. "
            "직전 분기 데이터가 없거나 매출이 0 이하이면 growth_rate와 growth_percentile은 null이다."
        ),
    )
    rankings: Dict[str, List[DistrictRankingItem]] = Field(
        description=(
            "상세 화면 '어디가 강할까?'의 서울 전체 상권 순위표. 동일 분기·업종에서 by_sales는 매출액, "
            "by_volume은 거래건수, by_growth는 QoQ 매출 성장률, by_score는 ExplorationScore 내림차순으로 "
            "각각 최대 5개를 반환한다. 성장률·점수를 산출할 수 없는 상권은 해당 순위에서 제외하며 "
            "유효 후보가 없으면 빈 목록이다. 현재 상권이 상위 5개 밖이면 별도 추가하지 않는다."
        ),
    )
    takeaway: Dict[str, Any] = Field(
        description=(
            "상세 화면 종합 인사이트. score는 반올림한 ExplorationScore "
            "(GrowthScore × 0.40 + TransactionScore × 0.35 + CompetitionScore × 0.25)이며 "
            "전분기 자료·현재 거래건수·수요 다양성 등 구성 지표가 부족하면 null이다. "
            "score_note는 점수 산출 불가 안내이며 점수를 구할 수 있으면 null이다. "
            "growth_tag는 매출 성장률 또는 산출 불가 문구, volume_tag는 거래건수, competition_tag는 경쟁 여건, "
            "summary는 점수 등급을 조합한 요약, disclaimer는 탐색 지표가 실제 창업 성공 가능성을 뜻하지 않는다는 안내이다."
        ),
    )


class TimeSlotSales(BaseModel):
    slot: str = Field(description="매출 집계 시간대. '00-06시', '06-11시', '11-14시', '14-17시', '17-21시', '21-24시' 중 하나이다.")
    percentage: int = Field(description="TimeShare: 전체 6개 시간대 매출 합계 중 해당 시간대 매출의 비중(%)을 반올림한 값. 합계가 0이면 0이다.")
    is_peak: bool = Field(description="해당 시간대 매출이 최대인지 여부. 최대 매출이 같으면 모두 true이며, 전체 시간대 매출이 0인 경우도 모두 true이다.")
    sales_amount: int = Field(description="선택 분기·상권·업종의 해당 시간대 매출액(원).")


class AgeGenderSales(BaseModel):
    age_group: str = Field(description="매출 집계 연령대. '10대', '20대', '30대', '40대', '50대', '60대+' 중 하나이며 연령과 성별을 결합한 집단은 아니다.")
    percentage: int = Field(description="AgeShare: 전체 연령대 매출 합계 중 해당 연령대 매출의 비중(%)을 반올림한 값. 합계가 0이면 0이다.")
    is_primary: bool = Field(description="해당 연령대 매출이 최대인지 여부. 최대 매출이 같으면 모두 true이며, 전체 연령대 매출이 0인 경우도 모두 true이다.")


class GenderSales(BaseModel):
    female_ratio: int = Field(description="FemaleShare: 여성 매출 / (남성 매출 + 여성 매출) × 100을 반올림한 비중(%). 성별 매출 합계가 0이면 0이다.")
    male_ratio: int = Field(description="남성 매출 비중(%). 현재 구현은 100 - female_ratio로 계산하므로 두 비중의 합은 100이며, 성별 매출 합계가 0인 경우에도 100이다.")
    dominant_gender: str = Field(description="반올림된 성별 매출 비중이 더 높은 성별. 여성 비중이 남성 이상이면 'female', 그 외에는 'male'이며 동률은 'female'이다.")


class DaySales(BaseModel):
    day: str = Field(description="매출 집계 요일. '월', '화', '수', '목', '금', '토', '일' 중 하나이다.")
    percentage: int = Field(description="DayShare: 월~일 전체 매출 합계 중 해당 요일 매출의 비중(%)을 반올림한 값. 합계가 0이면 0이다.")
    diff_from_average: int = Field(
        description="DayDiff: (해당 요일 매출 - 월~일 평균 매출) / 월~일 평균 매출 × 100을 반올림한 값(%). 현재 구현은 전체 요일 매출이 0이면 합계를 1로 보정하여 -100을 반환한다.",
    )
    is_peak: bool = Field(description="해당 요일 매출이 최대인지 여부. 최대 매출이 같으면 모두 true이며, 전체 요일 매출이 0인 경우도 모두 true이다.")


class DistrictPatternsResponse(BaseModel):
    when: Dict[str, Any] = Field(
        description=(
            "상세 화면 시간대별 매출 차트. peak_slot은 최대 매출 시간대(PeakTime), insight는 설명 문장, "
            "slots는 slot(시간대)·percentage(TimeShare, %)·sales_amount(원)·is_peak(최대 여부) 목록이다. "
            "동률인 항목은 모두 is_peak=true이며 peak_slot은 시간대 순서상 첫 항목이다. "
            "해당 분기·상권·업종의 원천 데이터를 조회할 수 없으면 slots는 [], peak_slot은 null이고 안내 문장을 반환한다. "
            "원천 행이 있으나 시간대 매출 합계가 0이면 비중은 모두 0이다."
        ),
    )
    who: Dict[str, Any] = Field(
        description=(
            "상세 화면 주요 소비 연령층과 성별 차트. primary_age_group은 최대 매출 연령대(PrimaryAge), "
            "primary_age_percentage는 해당 AgeShare(%), demographics는 age_group·percentage(%)·is_primary 목록, "
            "gender는 female_ratio(여성 매출 %)·male_ratio(100 - female_ratio)·dominant_gender(female 또는 male), "
            "insight는 연령대 요약이다. 연령과 성별은 별도로 집계하며 교차 비율이 아니다. "
            "연령대 최대 매출이 같으면 모두 is_primary=true이고 대표 연령대는 첫 항목이다. "
            "원천 데이터를 조회할 수 없으면 demographics는 [], primary_age_group·primary_age_percentage·gender는 null이다. "
            "원천 행의 연령대 매출 합계가 0이면 비중은 모두 0이며, 성별 합계가 0이면 여성 0%·남성 100%이다. "
            "성별 비중이 같으면 dominant_gender는 female이다."
        ),
    )
    day: Dict[str, Any] = Field(
        description=(
            "상세 화면 요일별 매출 차트. peak_day는 최대 매출 요일(PeakDay), peak_diff_badge는 월~일 평균 대비 "
            "증감률(DayDiff)을 '+21%'처럼 표시한 값, insight는 설명 문장, "
            "days는 day(요일)·percentage(DayShare, %)·diff_from_average(DayDiff, %)·is_peak 목록이다. "
            "동률인 항목은 모두 is_peak=true이고 대표 요일은 월~일 순서상 첫 항목이다. "
            "원천 데이터를 조회할 수 없으면 days는 [], peak_day와 peak_diff_badge는 null이다. "
            "원천 행이 있으나 요일 매출 합계가 0이면 비중은 0, diff_from_average는 현재 계산에 따라 -100이다."
        ),
    )


class DistrictCompetitionResponse(BaseModel):
    trade_area_code: str = Field(description="경쟁 여건 분석 대상 상권 코드. 분석 데이터가 없어도 요청 코드를 대문자로 반환한다.")
    store_count: Optional[int] = Field(
        default=None,
        description="선택한 분기·상권·업종의 현재 분기 동일 업종 점포 수(개). 현재 분기 점포 데이터가 없으면 null이다.",
    )
    qoq_store_change: Optional[int] = Field(
        default=None,
        description="동일 업종 점포 수의 전분기 대비 증감 수(개). 현재 또는 직전 분기 점포 데이터가 없으면 null이다.",
    )
    competition_level: Optional[str] = Field(
        default=None,
        description=(
            "CompetitionScore 기준 경쟁 여건. 70 이상 높음, 40 이상 70 미만 보통, 40 미만 낮음이며 높을수록 긍정적이다. "
            "실제 경쟁 점포 수가 아닌 매출·거래 기반 Proxy이다. 해당 분기·상권·업종의 분석 데이터가 없거나, "
            "현재 거래건수·직전 분기 매출·거래건수가 없거나 0 이하인 경우 또는 수요 다양성 자료 부족 등으로 "
            "CompetitionScore를 산출할 수 없으면 null이다."
        ),
    )
    sales_level: Optional[str] = Field(
        default=None,
        description="매출 수준. 100 - 매출 Benchmark Percentile이 70 이상이면 높음, 40 이상이면 보통, 그 미만이면 낮음이다. 해당 분기·상권·업종 데이터가 없거나 Percentile을 구할 수 없으면 null이다.",
    )
    volume_level: Optional[str] = Field(
        default=None,
        description="거래량 수준. 100 - 거래건수 Benchmark Percentile이 70 이상이면 높음, 40 이상이면 보통, 그 미만이면 낮음이다. 해당 분기·상권·업종 데이터가 없거나 Percentile을 구할 수 없으면 null이다.",
    )
    warning_text: Optional[str] = Field(
        default=None,
        description="CompetitionScore가 40 미만(경쟁 여건 낮음)이면 표시하는 경쟁 압박 경고. 경쟁 여건이 보통/높음이거나 분석 데이터 또는 구성 지표가 없어 등급을 구할 수 없으면 null이다.",
    )


class CompareDistrictData(BaseModel):
    trade_area_code: str = Field(description="비교표의 분석 대상 상권 코드.")
    trade_area_name: str = Field(description="비교표에 표시할 상권명. 상권 메타데이터가 없으면 상권 코드를 표시한다.")
    district: str = Field(description="상권이 속한 서울 자치구명. 자치구 정보가 없으면 '-'를 반환한다.")
    exploration_score: Optional[int] = Field(
        default=None,
        description=(
            "비교표의 ExplorationScore(0~100점)를 반올림한 값. GrowthScore × 0.40 + TransactionScore × 0.35 "
            "+ CompetitionScore × 0.25이며 높을수록 탐색 우선순위가 높다. 직전 분기 매출·거래건수가 없거나 "
            "0 이하인 경우, 현재 거래건수가 0 이하인 경우, 수요 다양성 자료 부족 등으로 구성 점수를 구할 수 없으면 null이다."
        ),
    )
    estimated_sales_formatted: str = Field(description="비교표에 표시할 분기 추정 매출액. '12.8억', '8500만'처럼 축약한 문자열이다.")
    estimated_sales: int = Field(description="선택 분기·상권·업종의 추정 매출액(원). 원천 데이터 thsmon_selng_amt에 해당한다.")
    transaction_count_formatted: str = Field(description="비교표에 표시할 분기 거래건수. 1만 건 이상은 '45만'처럼 축약한다.")
    transaction_count: int = Field(description="선택 분기·상권·업종의 거래건수(건). 원천 데이터 thsmon_selng_co에 해당한다.")
    growth_rate: Optional[float] = Field(
        default=None,
        description="QoQ 매출 성장률(%). overview의 kpis.qoq_growth_rate와 같은 계산값이며, 직전 분기 데이터가 없거나 매출이 0 이하이면 null이다.",
    )
    store_count: Optional[int] = Field(
        default=None,
        description="비교 대상 상권의 현재 분기·업종별 동일 업종 점포 수(개). 현재 분기 점포 데이터가 없으면 null이다.",
    )
    store_count_change: Optional[int] = Field(
        default=None,
        description="비교 대상 상권의 동일 업종 점포 수 전분기 대비 증감 수(개). 현재 또는 직전 분기 점포 데이터가 없으면 null이다.",
    )
    strongest_age_group: str = Field(description="최대 매출 연령대와 AgeShare를 '20대 (45%)'처럼 표시한 값. 동률이면 연령대 순서상 첫 항목이며, 연령대 데이터를 조회할 수 없으면 '-'이다.")
    strongest_time_period: str = Field(description="최대 매출 시간대(PeakTime)와 TimeShare를 '17-21시 (36%)'처럼 표시한 값. 동률이면 시간대 순서상 첫 항목이며, 시간대 데이터를 조회할 수 없으면 '-'이다.")
    strongest_day: str = Field(description="최대 매출 요일(PeakDay)과 월~일 평균 대비 증감률(DayDiff)을 '금 (+21%)'처럼 표시한 값. 동률이면 월~일 순서상 첫 항목이며, 요일 데이터를 조회할 수 없으면 '-'이다.")
    competition_level: Optional[str] = Field(
        default=None,
        description=(
            "CompetitionScore 기준 경쟁 여건 등급. 70 이상 높음, 40 이상 70 미만 보통, 40 미만 낮음이며 "
            "높음은 상대적으로 긍정적인 여건을 뜻하는 Proxy이고 실제 경쟁 점포 수가 아니다. "
            "현재 거래건수·직전 분기 매출·거래건수가 없거나 0 이하인 경우, 수요 다양성 자료 부족 등으로 "
            "CompetitionScore를 산출할 수 없으면 null이다."
        ),
    )
    key_insight: str = Field(description="비교표의 상권별 핵심 요약. GrowthScore·TransactionScore·CompetitionScore 중 산출 가능한 지표의 높음/보통/낮음 등급을 조합한 문장이다.")
