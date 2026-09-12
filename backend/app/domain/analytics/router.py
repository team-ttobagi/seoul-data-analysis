from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_db
from backend.app.domain.trade_area.repository import TradeAreaRepository
from backend.app.domain.sales.repository import SalesRepository
from backend.app.domain.industry.repository import IndustryRepository
from backend.app.domain.store.repository import StoreRepository
from backend.app.domain.store.service import StoreService
from backend.app.domain.analytics.service import AnalyticsService
from backend.app.domain.analytics.schemas import (
    RecommendationItemResponse,
    DistrictOverviewResponse,
    DistrictPatternsResponse,
    DistrictCompetitionResponse,
    CompareDistrictData,
)

router = APIRouter(tags=["Analytics"])


def get_analytics_service(db: AsyncSession = Depends(get_db)) -> AnalyticsService:
    trade_area_repo = TradeAreaRepository(session=db)
    sales_repo = SalesRepository(session=db)
    industry_repo = IndustryRepository(session=db)
    store_service = StoreService(repository=StoreRepository(session=db))
    return AnalyticsService(
        trade_area_repo=trade_area_repo,
        sales_repo=sales_repo,
        industry_repo=industry_repo,
        store_service=store_service,
    )


@router.get("/analytics/recommendations", response_model=List[RecommendationItemResponse])
async def get_recommendations(
    industry_code: str = Query(
        "CS100010", description="분석할 서비스 업종 코드. 업종 목록 API에서 선택하며 기본값은 커피·음료입니다.",
        examples=["CS100010"],
    ),
    quarter: str = Query(
        "2025 Q4", description="분석 기준 분기. YYYY Qn 형식으로 전달하며 해당 분기와 직전 분기 매출·거래 데이터를 사용합니다.",
        examples=["2025 Q4"],
    ),
    region: Optional[str] = Query(
        "서울 전체", description="추천 후보를 제한할 자치구명. 자치구명과 완전히 일치해야 하며 서울 전체 또는 빈 문자열이면 지역을 제한하지 않습니다. 점수 산출 기준은 서울 전체입니다.",
        examples=["서울 전체", "성동구"],
    ),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """선택한 업종·분기·지역에서 ExplorationScore가 높은 상권을 최대 5개 반환합니다.

    메인 탐색 화면의 '먼저 살펴볼 상권' 카드에 순위, 점수, 지표별 신호,
    근거 지표와 인사이트를 제공합니다. 동일 분기·동일 업종의 서울 전체 상권으로
    점수와 Benchmark Percentile을 산출한 후 자치구명으로 후보를 제한합니다.
    지역을 바꾸어도 해당 지역만으로 점수를 다시 정규화하지 않습니다.

    ExplorationScore는 `GrowthScore × 0.40 + TransactionScore × 0.35 + CompetitionScore × 0.25`이며,
    높을수록 탐색 우선순위가 높습니다.
    GrowthScore는 QoQ 매출 성장률을 P5~P95로 제한한 뒤 정규화한 점수,
    TransactionScore는 현재 거래건수에 로그 변환과 정규화를 적용한 점수입니다.
    CompetitionScore는 매출·거래 기반의 경쟁 환경 Proxy로, 높을수록 긍정적입니다.

    ExplorationScore를 산출할 수 없는 상권은 후보에서 제외하고, 산출 가능한
    점수의 내림차순으로 순위를 부여합니다. 조회된 데이터나 조건에 맞는 후보가
    없으면 404 대신 빈 목록을 반환합니다. warning은 경쟁 여건이 '낮음'일 때만
    제공하며 그 외에는 null입니다. 점수는 실제 창업 성공 가능성을 의미하지 않습니다.
    """
    return await service.get_recommendations(industry_code, quarter, region)


@router.get("/trade-areas/{trade_area_code}/overview", response_model=DistrictOverviewResponse)
async def get_district_overview(
    trade_area_code: str,
    industry_code: str = Query(
        "CS100010", description="상세 분석할 서비스 업종 코드. 동일 업종의 서울 전체 상권을 비교 기준으로 사용합니다.",
        examples=["CS100010"],
    ),
    quarter: str = Query(
        "2025 Q4", description="상세 분석 기준 분기. YYYY Qn 형식이며 GrowthRate는 해당 분기와 직전 분기 매출을 비교합니다.",
        examples=["2025 Q4"],
    ),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """상권 상세 화면의 KPI, 탐색 근거, 지표별 순위와 종합 인사이트를 반환합니다.

    상권 코드와 선택한 업종·분기로 매출을 조회합니다. 해당 조합의 매출 데이터가
    조회되지 않으면 404(SALES_DATA_NOT_FOUND)를 반환합니다. 상권명·업종명은
    메타데이터를 사용하며 조회되지 않는 이름은 해당 코드로 대신 표시합니다.
    현재 분기 점포 데이터가 없으면 store_count를 null로, 직전 분기 점포 데이터가 없으면
    store_count_change를 null로 반환합니다.

    GrowthRate는 직전 분기 대비 매출 증감률(%)입니다. 전분기 매출이 없거나
    0 이하이면 qoq_growth_rate와 growth_percentile은 null입니다. seoul_rank는
    서울 전체의 동일 분기·동일 업종에서 매출·성장·거래·CompetitionScore의
    Benchmark Percentile 평균이 낮은 순으로 산정하며, 구성 지표가 부족하면
    null입니다. Percentile은 '상위 N%'를 뜻하므로 낮을수록 상위권입니다.

    rankings는 Sales, Transaction, GrowthRate, ExplorationScore별 내림차순
    상위 5개를 제공합니다. 성장률·탐색 점수 산출 불가 상권은 해당 순위에서 제외합니다.
    각 순위 항목의 sales_raw와 sales_formatted는 선택한 지표의 원본값과 표시값입니다.

    takeaway.score는 `GrowthScore × 0.40 + TransactionScore × 0.35 + CompetitionScore × 0.25`인
    ExplorationScore를 반올림한 값입니다.
    구성 점수가 부족하면 null이며 score_note로 산출 불가 사유를 안내합니다.
    CompetitionScore는 실제 점포 수 대신 경쟁 환경을 간접 추정한 Proxy입니다.
    """
    return await service.get_overview(trade_area_code, industry_code, quarter)


@router.get("/trade-areas/{trade_area_code}/patterns", response_model=DistrictPatternsResponse)
async def get_district_patterns(
    trade_area_code: str,
    industry_code: str = Query(
        "CS100010", description="소비 패턴을 조회할 서비스 업종 코드. 선택한 상권의 해당 업종 매출만 사용합니다.",
        examples=["CS100010"],
    ),
    quarter: str = Query(
        "2025 Q4", description="소비 패턴 조회 분기. YYYY Qn 형식이며 해당 분기의 시간대·연령대·성별·요일별 매출을 사용합니다.",
        examples=["2025 Q4"],
    ),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """상권·업종·분기별 시간대, 연령대, 성별, 요일 소비 패턴을 반환합니다.

    상권 상세 화면의 '언제가 가장 많이 팔릴까?', '누가 가장 많이 살까?',
    '어느 요일이 강할까?' 차트와 피크 배지에 사용하는 데이터입니다.
    TimeShare, AgeShare, DayShare는 각 분류별 매출 합계 대비 비중(%)이며
    실제 방문자 수나 연령×성별 교차 집단의 비율이 아닙니다. 성별 비중은 별도로 제공합니다.
    DayDiff는 월~일 7개 요일의 평균 매출 대비 증감률(%)입니다.

    PeakTime, PrimaryAge, PeakDay는 분류별 최대 매출 항목입니다.
    동률이면 개별 항목의 is_peak 또는 is_primary가 모두 true이며,
    요약에는 시간대·연령대·요일의 응답 순서상 첫 번째 최대값을 사용합니다.

    해당 조건의 매출 행이 조회되지 않아도 404를 반환하지 않습니다.
    when.slots, who.demographics, day.days는 빈 목록이고, when.peak_slot,
    who.primary_age_group, who.primary_age_percentage, who.gender,
    day.peak_day, day.peak_diff_badge는 null입니다.
    매출 행은 존재하지만 매출액이 모두 0인 경우에는 항목 목록을 유지합니다.
    """
    return await service.get_patterns(trade_area_code, industry_code, quarter)


@router.get("/trade-areas/{trade_area_code}/competition", response_model=DistrictCompetitionResponse)
async def get_district_competition(
    trade_area_code: str,
    industry_code: str = Query(
        "CS100010", description="경쟁 여건을 분석할 서비스 업종 코드. 동일 업종의 서울 전체 상권을 비교 기준으로 사용합니다.",
        examples=["CS100010"],
    ),
    quarter: str = Query(
        "2025 Q4", description="경쟁 여건 분석 분기. YYYY Qn 형식이며 성장 균형 계산에는 직전 분기의 매출·거래 데이터도 필요합니다.",
        examples=["2025 Q4"],
    ),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """상권 상세 화면의 경쟁 여건, 매출 수준, 거래량 수준과 주의 문구를 반환합니다.

    선택한 상권·업종·분기의 CompetitionScore를 같은 분기·같은 업종의 서울
    전체 상권과 비교해 산출합니다. CompetitionScore는
    `TicketScore × 0.50 + GrowthBalanceScore × 0.30 + DemandDiversityScore × 0.20`으로 계산하는
    경쟁 환경 Proxy입니다. DemandDiversityScore에는 해당 분기의 상권별 전체
    업종 매출 분포를 사용합니다. 실제 경쟁 점포 수를 의미하지 않으며,
    '높음'일수록 경쟁 여건이 상대적으로 긍정적입니다.

    competition_level은 CompetitionScore가 70 이상이면 '높음',
    40 이상 70 미만이면 '보통', 40 미만이면 '낮음'입니다.
    sales_level과 volume_level은 각각 100 - Sales Percentile,
    100 - Transaction Volume Percentile에 같은 구간 기준을 적용합니다.
    warning_text는 competition_level이 '낮음'일 때만 제공하고 그 외에는 null입니다.

    매출 데이터가 조회되지 않으면 404 대신 상권 코드와 나머지 필드가 null인
    객체를 반환합니다. 매출은 있어도 전분기 데이터 부재, 거래건수 0 또는
    구성 지표 부족으로 CompetitionScore를 산출할 수 없으면 competition_level은 null입니다.
    현재 분기 점포 데이터가 없으면 store_count를 null로, 직전 분기 점포 데이터가 없으면
    qoq_store_change를 null로 반환합니다.
    """
    return await service.get_competition(trade_area_code, industry_code, quarter)


@router.get("/compare", response_model=List[CompareDistrictData])
async def get_compare_districts(
    trade_area_codes: str = Query(
        ..., description="비교할 상권 코드를 쉼표로 구분한 필수 문자열. 공백과 빈 항목은 제거하며 입력 순서와 중복 코드는 유지합니다. 현재 API에는 개수 제한이 없습니다.",
        examples=["SEONGSU,HONGDAE"],
    ),
    industry_code: str = Query(
        "CS100010", description="모든 비교 상권에 공통으로 적용할 하나의 서비스 업종 코드. 상권마다 서로 다른 업종을 지정하는 방식은 지원하지 않습니다.",
        examples=["CS100010"],
    ),
    quarter: str = Query(
        "2025 Q4", description="모든 비교 상권에 공통으로 적용할 분기. YYYY Qn 형식이며 점수와 순위는 동일 분기·동일 업종의 서울 전체 상권을 기준으로 산출합니다.",
        examples=["2025 Q4"],
    ),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """선택한 상권들의 매출·거래·탐색 점수와 주요 소비 패턴을 비교 목록으로 반환합니다.

    비교 화면의 표에 사용할 데이터로, 요청한 모든 상권에 하나의 업종과 분기를
    공통 적용합니다. 점수는 선택 목록 내부가 아니라 동일 분기·동일 업종의
    서울 전체 상권을 기준으로 계산합니다. exploration_score는
    GrowthScore × 0.40 + TransactionScore × 0.35 + CompetitionScore × 0.25인
    ExplorationScore의 반올림 값이며, CompetitionScore는 경쟁 환경 Proxy입니다.

    상권 코드는 쉼표로 분리한 뒤 앞뒤 공백과 빈 항목을 제거하고 대문자로 조회합니다.
    입력 순서를 유지하며 중복 코드는 중복 결과로 반환합니다. 해당 업종·분기의
    매출 데이터가 없는 코드는 404 대신 목록에서 제외하고, 조회 가능한 코드가
    없으면 빈 목록을 반환합니다. 현재 서버는 비교 상권 수를 제한하지 않습니다.

    전분기 매출이 없거나 0 이하이면 growth_rate는 null이며, 구성 지표가
    부족하면 exploration_score와 competition_level은 null일 수 있습니다.
    주요 연령대·시간대·요일을 찾을 수 없는 경우 해당 표시 문자열은 '-'입니다.
    매출 데이터가 있는 비교 대상 중 현재 분기 점포 데이터가 없으면 store_count를 null로,
    직전 분기 점포 데이터가 없으면 store_count_change를 null로 반환합니다.
    이 API는 비교함의 선택 상태를 저장하지 않으므로 선택 변경 시 다시 조회해야 합니다.
    """
    codes = [c.strip() for c in trade_area_codes.split(",") if c.strip()]
    return await service.get_compare(codes, industry_code, quarter)
