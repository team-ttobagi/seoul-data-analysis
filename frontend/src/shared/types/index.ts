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
  signgu_cd?: string;
  keyword?: string;
}

export interface Industry {
  code: string;
  name: string;
  category: string;
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

export interface DistrictKpis {
  estimated_sales: number; // in KRW (e.g. 1280000000)
  estimated_sales_formatted: string; // "12.8억"
  transaction_count: number; // e.g. 450000
  transaction_count_formatted: string; // "45만"
  seoul_rank: number; // e.g. 7
  qoq_growth_rate: number; // e.g. +8.2
  sales_percentile: number; // e.g. 18 (상위 18%)
  volume_percentile: number; // e.g. 12 (상위 12%)
  competition_level: "매우 높음" | "높음" | "보통" | "낮음";
  sales_level: "매우 높음" | "높음" | "보통" | "낮음";
  volume_level: "매우 높음" | "높음" | "보통" | "낮음";
}

export interface TimeSlotSales {
  slot: string; // "06-11시", "11-14시", "14-17시", "17-21시", "21-24시", "24-06시"
  percentage: number;
  is_peak: boolean;
  sales_amount: number;
}

export interface AgeGenderSales {
  age_group: "10대" | "20대" | "30대" | "40대+";
  percentage: number;
  female_ratio: number; // 0 to 100
  male_ratio: number; // 0 to 100
  dominant_gender: "female" | "male" | "equal";
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
    primary_target: string; // e.g. "20대 여성"
    target_badge: string; // "주요 고객층"
    insight: string;
    demographics: AgeGenderSales[];
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
    score: number;
    growth_tag: string;
    volume_tag: string;
    competition_tag: string;
    summary: string;
    disclaimer: string;
  };
}

export interface DistrictCompetition {
  trade_area_code: string;
  competition_level: string;
  sales_level: string;
  volume_level: string;
  warning_text: string;
}

export interface CompareDistrictData {
  trade_area_code: string;
  trade_area_name: string;
  district: string;
  exploration_score: number;
  estimated_sales_formatted: string;
  estimated_sales: number;
  transaction_count_formatted: string;
  transaction_count: number;
  growth_rate: number;
  strongest_age_group: string;
  strongest_time_period: string;
  strongest_day: string;
  competition_level: string;
  key_insight: string;
}

export interface ApiErrorResponse {
  error: {
    code: string;
    message: string;
  };
}
