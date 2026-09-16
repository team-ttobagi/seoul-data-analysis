// Core TypeScript Types and Entities for SEOUL DATA PLAYGROUND

export interface TradeArea {
  code: string;
  name: string;
  district_code: string;
  district_name: string | null;
}

// 전체 상권 목록 API: GET /trade-areas
export interface TradeAreaResponse {
  trdar_cd: string;
  trdar_se_cd: string;
  trdar_cd_nm: string;
  signgu_cd: string;
  signgu_cd_nm: string | null;
}

export interface District {
  signgu_cd: string;
  signgu_cd_nm: string;
}

export interface TradeAreaSearchParams {
  industry_code: string;
  signgu_cd: string;
  quarter: string;
  keyword?: string;
}

export interface QuarterOption {
  code: string;
  value: string;
}

export interface Industry {
  code: string;
  name: string;
  category?: string;
  description?: string;
}

export interface ScoreComponent {
  value: number;
  normalized_score: number;
  unit?: string;
  benchmark_percentile?: number; // e.g. 18 for 상위 18%
}

export interface RecommendationComponents {
  sales_growth: ScoreComponent;
  transaction_volume: ScoreComponent;
  competition: ScoreComponent;
}

export interface RecommendationItem {
  rank: number;
  trade_area_code: string;
  trade_area_name: string;
  district: string;
  score: number;
  signals: {
    growth: "high" | "medium" | "low";
    transaction: "high" | "medium" | "low";
    competition: "high" | "medium" | "low";
  };
  components: RecommendationComponents;
  insight: string;
  warning?: string;
}

// [연동] backend/app/domain/analytics/schemas.py DistrictKpis 기준.
// seoul_rank/qoq_growth_rate/competition_level/sales_level/volume_level 은
// 직전 분기 데이터 부족 시 null 을 반환하는 Optional 필드다.
export interface DistrictKpis {
  estimated_sales: number; // in KRW (e.g. 1280000000)
  estimated_sales_formatted: string; // "12.8억"
  transaction_count: number; // e.g. 450000
  transaction_count_formatted: string; // "45만"
  seoul_rank: number | null; // e.g. 7
  qoq_growth_rate: number | null; // e.g. +8.2
  sales_percentile: number; // e.g. 18 (상위 18%)
  volume_percentile: number; // e.g. 12 (상위 12%)
  competition_level: string | null; // 실제 값: "높음" | "보통" | "낮음"
  sales_level: string | null;
  volume_level: string | null;
}

export interface TimeSlotSales {
  slot: string; // "06-11시", "11-14시", "14-17시", "17-21시", "21-24시", "24-06시"
  percentage: number;
  is_peak: boolean;
  sales_amount: number;
}

// [연동] backend/app/domain/analytics/schemas.py DistrictPatternsResponse.who 기준.
// 연령과 성별은 별도로 집계되는 값이라 age_group 항목에는 성별 필드가 없다.
// WHO 섹션은 성별 구분 없이 연령대만 표시하기로 해 gender 자체를 프론트에서 사용하지 않는다.
export interface AgeShare {
  age_group: string; // "10대" ~ "60대+"
  percentage: number;
  is_primary: boolean;
}

export interface DaySales {
  day: "월" | "화" | "수" | "목" | "금" | "토" | "일";
  percentage: number;
  diff_from_average: number; // e.g. +21 for +21%
  is_peak: boolean;
}

export interface DistrictPatterns {
  when: {
    peak_slot: string; // e.g. "17–21시"
    insight: string;
    slots: TimeSlotSales[];
  };
  who: {
    // primary_age_group/primary_age_percentage 는 원천 데이터가 없으면 null(백엔드 기준).
    primary_age_group: string | null; // e.g. "20대"
    primary_age_percentage: number | null;
    insight: string;
    demographics: AgeShare[];
  };
  day: {
    peak_day: string; // e.g. "금요일"
    peak_diff_badge: string; // "+21%"
    insight: string;
    days: DaySales[];
  };
}

export interface DistrictRankingItem {
  rank: number;
  trade_area_code: string;
  trade_area_name: string;
  sales_formatted: string;
  sales_raw: number;
  is_current: boolean;
  score?: number;
  growth_rate?: number;
  transaction_count?: number;
}

export interface DistrictOverview {
  trade_area_code: string;
  trade_area_name: string;
  district: string;
  industry_code: string;
  industry_name: string;
  quarter: string;
  kpis: DistrictKpis;
  why_explore: {
    growth_rate: number;
    growth_percentile: number;
    volume_formatted: string;
    volume_percentile: number;
    competition_text: string;
  };
  rankings: {
    by_sales: DistrictRankingItem[];
    by_volume: DistrictRankingItem[];
    by_growth: DistrictRankingItem[];
    by_score: DistrictRankingItem[];
  };
  takeaway: {
    // score 는 구성 지표(성장률/거래량/경쟁) 부족 시 null → score_note 에 산출 불가 사유가 담긴다.
    score: number | null;
    score_note?: string | null; // score 가 null 일 때 산출 불가 사유. mock 데이터엔 없음
    growth_tag: string;
    volume_tag: string;
    competition_tag: string;
    // summary 는 /overview 응답에서는 항상 "AI 인사이트 생성 중입니다." 고정값이며,
    // 실제 값은 getDistrictOverviewInsight()(별도 /overview/insight 호출)로 받아와 교체한다.
    summary: string;
    disclaimer: string;
  };
}

// [연동] backend/app/domain/analytics/schemas.py DistrictCompetitionResponse 기준.
// trade_area_code 를 제외한 전 필드가 점포·경쟁 데이터 부족 시 null 을 반환하는 Optional 이다.
export interface DistrictCompetition {
  trade_area_code: string;
  competition_level: string | null; // 실제 값: "높음" | "보통" | "낮음"
  sales_level: string | null;
  volume_level: string | null;
  warning_text: string | null;
}

// [연동] backend GET /trade-areas/{code}/overview/insight → OverviewInsightResponse 기준.
// Gemini 인사이트는 생성까지 수 초가 걸려 overview 응답과 분리된 별도 endpoint로 받는다.
export interface DistrictOverviewInsight {
  summary: string;
  source: "gemini" | "fallback"; // gemini 성공이면 "AI INSIGHT" 라벨 표시
  status: "generated" | "fallback";
}

// [연동] backend/app/domain/analytics/schemas.py CompareDistrictData 기준.
// exploration_score / growth_rate / store_count / store_count_change / competition_level 은
// 백엔드에서 데이터 부족 시 null 을 반환할 수 있어 Optional 로 맞춘다.
export interface CompareDistrictData {
  trade_area_code: string;
  trade_area_name: string;
  district: string;
  exploration_score: number | null;
  estimated_sales_formatted: string;
  estimated_sales: number;
  transaction_count_formatted: string;
  transaction_count: number;
  growth_rate: number | null;
  store_count: number | null;
  store_count_change: number | null;
  strongest_age_group: string;
  strongest_time_period: string;
  strongest_day: string;
  competition_level: string | null;
  key_insight: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
  };
}
