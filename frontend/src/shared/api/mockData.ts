// Seeded dataset adhering to Seoul Commercial District Open Data schemas and values
/* ----------------------------- */
// Update by SoO 2026.09.07
//   store_count
//   store_count_change
//   qoq_store_change 제외
/* ----------------------------- */
import {
  TradeArea,
  TradeAreaResponse,
  District,
  Industry,
  RecommendationItem,
  DistrictOverview,
  DistrictPatterns,
  DistrictCompetition,
  CompareDistrictData,
} from "../types";

export const MOCK_DISTRICTS: District[] = [
  { signgu_cd: "11110", signgu_cd_nm: "종로구" },
  { signgu_cd: "11140", signgu_cd_nm: "중구" },
  { signgu_cd: "11170", signgu_cd_nm: "용산구" },
  { signgu_cd: "11200", signgu_cd_nm: "성동구" },
  { signgu_cd: "11215", signgu_cd_nm: "광진구" },
  { signgu_cd: "11230", signgu_cd_nm: "동대문구" },
  { signgu_cd: "11260", signgu_cd_nm: "중랑구" },
  { signgu_cd: "11290", signgu_cd_nm: "성북구" },
  { signgu_cd: "11305", signgu_cd_nm: "강북구" },
  { signgu_cd: "11320", signgu_cd_nm: "도봉구" },
  { signgu_cd: "11350", signgu_cd_nm: "노원구" },
  { signgu_cd: "11380", signgu_cd_nm: "은평구" },
  { signgu_cd: "11410", signgu_cd_nm: "서대문구" },
  { signgu_cd: "11440", signgu_cd_nm: "마포구" },
  { signgu_cd: "11470", signgu_cd_nm: "양천구" },
  { signgu_cd: "11500", signgu_cd_nm: "강서구" },
  { signgu_cd: "11530", signgu_cd_nm: "구로구" },
  { signgu_cd: "11545", signgu_cd_nm: "금천구" },
  { signgu_cd: "11560", signgu_cd_nm: "영등포구" },
  { signgu_cd: "11590", signgu_cd_nm: "동작구" },
  { signgu_cd: "11620", signgu_cd_nm: "관악구" },
  { signgu_cd: "11650", signgu_cd_nm: "서초구" },
  { signgu_cd: "11680", signgu_cd_nm: "강남구" },
  { signgu_cd: "11710", signgu_cd_nm: "송파구" },
  { signgu_cd: "11740", signgu_cd_nm: "강동구" },
];

export const MOCK_INDUSTRIES: Industry[] = [
  {
    code: "CS100010",
    name: "커피·음료",
    category: "외식업",
    description: "카페, 디저트 및 음료 전문점",
  },
  {
    code: "CS100001",
    name: "한식",
    category: "외식업",
    description: "한식 일반 음식점 및 식당",
  },
  {
    code: "CS100007",
    name: "치킨",
    category: "외식업",
    description: "치킨 및 닭강정 전문점",
  },
  {
    code: "CS200001",
    name: "편의점",
    category: "서비스업",
    description: "종합 편의점 및 소매 유통",
  },
  {
    code: "CS300001",
    name: "의류",
    category: "도소매업",
    description: "패션, 캐주얼 및 부티크 의류",
  },
  {
    code: "CS300002",
    name: "미용",
    category: "서비스업",
    description: "헤어샵, 네일 및 뷰티 케어",
  },
];

export const MOCK_TRADE_AREAS: TradeArea[] = [
  {
    code: "SEONGSU",
    name: "성수동",
    district_code: "11200",
    district_name: "성동구",
  },
  {
    code: "HONGDAE",
    name: "홍대입구",
    district_code: "11440",
    district_name: "마포구",
  },
  {
    code: "SHAROSU",
    name: "샤로수길",
    district_code: "11620",
    district_name: "관악구",
  },
  {
    code: "KONKUK",
    name: "건대입구",
    district_code: "11215",
    district_name: "광진구",
  },
  {
    code: "GANGNAM",
    name: "강남역",
    district_code: "11680",
    district_name: "강남구",
  },
  {
    code: "GAROSU",
    name: "가로수길",
    district_code: "11680",
    district_name: "강남구",
  },
  {
    code: "IKSEON",
    name: "익선동",
    district_code: "11110",
    district_name: "종로구",
  },
  {
    code: "EULJIRO",
    name: "을지로3가",
    district_code: "11140",
    district_name: "중구",
  },
];

// 전체 상권 API 응답 형태의 개발용 Mock 데이터
export const MOCK_TRADE_AREA_RESPONSES: TradeAreaResponse[] =
  MOCK_TRADE_AREAS.map((area) => ({
    trdar_cd: area.code,
    // 개발용 고정값이며 실제 상권 유형을 의미하지 않습니다.
    trdar_se_cd: "A",
    trdar_cd_nm: area.name,
    signgu_cd: area.district_code,
    signgu_cd_nm: area.district_name,
  }));

// Calculation of deterministic exploration scores:
// sales_growth_weight = 0.40, transaction_volume_weight = 0.35, competition_weight = 0.25 (inverse)
export function getMockRecommendations(
  _industryCode: string = "CS100010",
  _quarter: string = "2026 Q2",
): RecommendationItem[] {
  return [
    {
      rank: 1,
      trade_area_code: "SEONGSU",
      trade_area_name: "성수동",
      district: "성동구",
      score: 82,
      signals: {
        growth: "high",
        transaction: "high",
        competition: "high",
      },
      components: {
        sales_growth: {
          value: 12.4,
          normalized_score: 91,
          benchmark_percentile: 18,
        },
        transaction_volume: {
          value: 450000,
          normalized_score: 85,
          benchmark_percentile: 12,
        },
        competition: {
          value: 134,
          normalized_score: 62,
          benchmark_percentile: 88,
        },
      },
      insight: "성장성과 거래 활성도가 높지만 경쟁도 강합니다.",
      warning: "동일 업종 134개로 공급 집중 심화",
    },
    {
      rank: 2,
      trade_area_code: "HONGDAE",
      trade_area_name: "홍대입구",
      district: "마포구",
      score: 78,
      signals: {
        growth: "medium",
        transaction: "high",
        competition: "high",
      },
      components: {
        sales_growth: {
          value: 6.8,
          normalized_score: 76,
          benchmark_percentile: 25,
        },
        transaction_volume: {
          value: 580000,
          normalized_score: 94,
          benchmark_percentile: 5,
        },
        competition: {
          value: 182,
          normalized_score: 52,
          benchmark_percentile: 95,
        },
      },
      insight:
        "서울 최대 거래량을 자랑하지만 동일 업종 진입 밀도가 최상위권입니다.",
      warning: "임대료 및 과밀 경쟁 유의",
    },
    {
      rank: 3,
      trade_area_code: "SHAROSU",
      trade_area_name: "샤로수길",
      district: "관악구",
      score: 74,
      signals: {
        growth: "high",
        transaction: "medium",
        competition: "low",
      },
      components: {
        sales_growth: {
          value: 14.1,
          normalized_score: 95,
          benchmark_percentile: 9,
        },
        transaction_volume: {
          value: 280000,
          normalized_score: 68,
          benchmark_percentile: 38,
        },
        competition: {
          value: 58,
          normalized_score: 82,
          benchmark_percentile: 45,
        },
      },
      insight:
        "1인 청년 가구의 소비 증가세가 뚜렷하며 상대적 경쟁 부담이 낮습니다.",
    },
    {
      rank: 4,
      trade_area_code: "KONKUK",
      trade_area_name: "건대입구",
      district: "광진구",
      score: 71,
      signals: {
        growth: "medium",
        transaction: "medium",
        competition: "medium",
      },
      components: {
        sales_growth: {
          value: 5.2,
          normalized_score: 70,
          benchmark_percentile: 34,
        },
        transaction_volume: {
          value: 320000,
          normalized_score: 74,
          benchmark_percentile: 30,
        },
        competition: {
          value: 96,
          normalized_score: 69,
          benchmark_percentile: 65,
        },
      },
      insight:
        "안정적인 대학생 배후 수요를 기반으로 꾸준한 소비 흐름을 보입니다.",
    },
    {
      rank: 5,
      trade_area_code: "GANGNAM",
      trade_area_name: "강남역",
      district: "강남구",
      score: 69,
      signals: {
        growth: "low",
        transaction: "high",
        competition: "high",
      },
      components: {
        sales_growth: {
          value: 2.1,
          normalized_score: 55,
          benchmark_percentile: 62,
        },
        transaction_volume: {
          value: 620000,
          normalized_score: 98,
          benchmark_percentile: 2,
        },
        competition: {
          value: 240,
          normalized_score: 42,
          benchmark_percentile: 99,
        },
      },
      insight:
        "거래 규모는 서울 최고이나 성장 정체와 초대형 프랜차이즈 과밀 상태입니다.",
      warning: "초기 고정비 및 포화 경쟁 경계",
    },
  ];
}

export function getMockDistrictOverview(
  tradeAreaCode: string,
): DistrictOverview {
  const code = tradeAreaCode.toUpperCase();

  if (code === "HONGDAE") {
    return {
      trade_area_code: "HONGDAE",
      trade_area_name: "홍대입구",
      district: "마포구",
      industry_code: "CS100010",
      industry_name: "커피·음료",
      quarter: "2026 Q2",
      kpis: {
        estimated_sales: 1620000000,
        estimated_sales_formatted: "16.2억",
        transaction_count: 580000,
        transaction_count_formatted: "58만",
        seoul_rank: 2,
        qoq_growth_rate: 6.8,
        sales_percentile: 5,
        volume_percentile: 5,
        // store_count: 182,
        // store_count_change: 8,
        competition_level: "매우 높음",
        sales_level: "매우 높음",
        volume_level: "매우 높음",
      },
      why_explore: {
        growth_rate: 6.8,
        growth_percentile: 25,
        volume_formatted: "58만",
        volume_percentile: 5,
        // store_count: 182,
        competition_text: "경쟁 매우 높음",
      },
      rankings: {
        by_sales: [
          {
            rank: 1,
            trade_area_code: "GANGNAM",
            trade_area_name: "강남역",
            sales_formatted: "18.5억",
            sales_raw: 1850000000,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "16.2억",
            sales_raw: 1620000000,
            is_current: true,
          },
          {
            rank: 3,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "12.8억",
            sales_raw: 1280000000,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "GAROSU",
            trade_area_name: "가로수길",
            sales_formatted: "11.7억",
            sales_raw: 1170000000,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "8.9억",
            sales_raw: 890000000,
            is_current: false,
          },
        ],
        by_volume: [
          {
            rank: 1,
            trade_area_code: "GANGNAM",
            trade_area_name: "강남역",
            sales_formatted: "62만",
            sales_raw: 620000,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "58만",
            sales_raw: 580000,
            is_current: true,
          },
          {
            rank: 3,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "45만",
            sales_raw: 450000,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "32만",
            sales_raw: 320000,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "28만",
            sales_raw: 280000,
            is_current: false,
          },
        ],
        by_growth: [
          {
            rank: 1,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "+14.1%",
            sales_raw: 14.1,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "+12.4%",
            sales_raw: 12.4,
            is_current: false,
          },
          {
            rank: 3,
            trade_area_code: "EULJIRO",
            trade_area_name: "을지로3가",
            sales_formatted: "+9.2%",
            sales_raw: 9.2,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "+6.8%",
            sales_raw: 6.8,
            is_current: true,
          },
          {
            rank: 5,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "+5.2%",
            sales_raw: 5.2,
            is_current: false,
          },
        ],
        by_score: [
          {
            rank: 1,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "82점",
            sales_raw: 82,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "78점",
            sales_raw: 78,
            is_current: true,
          },
          {
            rank: 3,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "74점",
            sales_raw: 74,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "71점",
            sales_raw: 71,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "GANGNAM",
            trade_area_name: "강남역",
            sales_formatted: "69점",
            sales_raw: 69,
            is_current: false,
          },
        ],
      },
      takeaway: {
        score: 78,
        growth_tag: "매출 증가율 ++",
        volume_tag: "거래건수 ++++",
        competition_tag: "경쟁 강도 --",
        summary:
          "홍대입구는 압도적인 거래 활성도를 지니나 출점 경쟁이 심화된 상권입니다.",
        disclaimer:
          "실제 창업 성공 가능성을 의미하지 않는 데이터 기반 탐색 지표입니다.",
      },
    };
  }

  if (code === "SHAROSU") {
    return {
      trade_area_code: "SHAROSU",
      trade_area_name: "샤로수길",
      district: "관악구",
      industry_code: "CS100010",
      industry_name: "커피·음료",
      quarter: "2026 Q2",
      kpis: {
        estimated_sales: 740000000,
        estimated_sales_formatted: "7.4억",
        transaction_count: 280000,
        transaction_count_formatted: "28만",
        seoul_rank: 18,
        qoq_growth_rate: 14.1,
        sales_percentile: 28,
        volume_percentile: 38,
        // store_count: 58,
        // store_count_change: 3,
        competition_level: "보통",
        sales_level: "보통",
        volume_level: "보통",
      },
      why_explore: {
        growth_rate: 14.1,
        growth_percentile: 9,
        volume_formatted: "28만",
        volume_percentile: 38,
        // store_count: 58,
        competition_text: "경쟁 보통 / 성장 우수",
      },
      rankings: {
        by_sales: [
          {
            rank: 1,
            trade_area_code: "GANGNAM",
            trade_area_name: "강남역",
            sales_formatted: "18.5억",
            sales_raw: 1850000000,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "16.2억",
            sales_raw: 1620000000,
            is_current: false,
          },
          {
            rank: 3,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "12.8억",
            sales_raw: 1280000000,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "GAROSU",
            trade_area_name: "가로수길",
            sales_formatted: "11.7억",
            sales_raw: 1170000000,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "7.4억",
            sales_raw: 740000000,
            is_current: true,
          },
        ],
        by_volume: [
          {
            rank: 1,
            trade_area_code: "GANGNAM",
            trade_area_name: "강남역",
            sales_formatted: "62만",
            sales_raw: 620000,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "58만",
            sales_raw: 580000,
            is_current: false,
          },
          {
            rank: 3,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "45만",
            sales_raw: 450000,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "32만",
            sales_raw: 320000,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "28만",
            sales_raw: 280000,
            is_current: true,
          },
        ],
        by_growth: [
          {
            rank: 1,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "+14.1%",
            sales_raw: 14.1,
            is_current: true,
          },
          {
            rank: 2,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "+12.4%",
            sales_raw: 12.4,
            is_current: false,
          },
          {
            rank: 3,
            trade_area_code: "EULJIRO",
            trade_area_name: "을지로3가",
            sales_formatted: "+9.2%",
            sales_raw: 9.2,
            is_current: false,
          },
          {
            rank: 4,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "+6.8%",
            sales_raw: 6.8,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "+5.2%",
            sales_raw: 5.2,
            is_current: false,
          },
        ],
        by_score: [
          {
            rank: 1,
            trade_area_code: "SEONGSU",
            trade_area_name: "성수동",
            sales_formatted: "82점",
            sales_raw: 82,
            is_current: false,
          },
          {
            rank: 2,
            trade_area_code: "HONGDAE",
            trade_area_name: "홍대입구",
            sales_formatted: "78점",
            sales_raw: 78,
            is_current: false,
          },
          {
            rank: 3,
            trade_area_code: "SHAROSU",
            trade_area_name: "샤로수길",
            sales_formatted: "74점",
            sales_raw: 74,
            is_current: true,
          },
          {
            rank: 4,
            trade_area_code: "KONKUK",
            trade_area_name: "건대입구",
            sales_formatted: "71점",
            sales_raw: 71,
            is_current: false,
          },
          {
            rank: 5,
            trade_area_code: "GANGNAM",
            trade_area_name: "강남역",
            sales_formatted: "69점",
            sales_raw: 69,
            is_current: false,
          },
        ],
      },
      takeaway: {
        score: 74,
        growth_tag: "매출 증가율 ++++",
        volume_tag: "거래건수 ++",
        competition_tag: "경쟁 강도 양호",
        summary:
          "샤로수길은 청년 1인 가구 기반 높은 성장성과 비교적 적정 경쟁도를 보이는 상권입니다.",
        disclaimer:
          "실제 창업 성공 가능성을 의미하지 않는 데이터 기반 탐색 지표입니다.",
      },
    };
  }

  // Default: SEONGSU (Exactly matching Reference Image 2!)
  return {
    trade_area_code: "SEONGSU",
    trade_area_name: "성수동",
    district: "성동구",
    industry_code: "CS100010",
    industry_name: "커피·음료",
    quarter: "2026 Q2",
    kpis: {
      estimated_sales: 1280000000,
      estimated_sales_formatted: "12.8억",
      transaction_count: 450000,
      transaction_count_formatted: "45만",
      seoul_rank: 7,
      qoq_growth_rate: 8.2,
      sales_percentile: 18,
      volume_percentile: 12,
      // store_count: 134,
      // store_count_change: 12,
      competition_level: "매우 높음",
      sales_level: "높음",
      volume_level: "높음",
    },
    why_explore: {
      growth_rate: 12.4,
      growth_percentile: 18,
      volume_formatted: "45만",
      volume_percentile: 12,
      // store_count: 134,
      competition_text: "경쟁 매우 높음",
    },
    rankings: {
      by_sales: [
        {
          rank: 1,
          trade_area_code: "GANGNAM",
          trade_area_name: "강남역",
          sales_formatted: "18.5억",
          sales_raw: 1850000000,
          is_current: false,
        },
        {
          rank: 2,
          trade_area_code: "HONGDAE",
          trade_area_name: "홍대입구",
          sales_formatted: "16.2억",
          sales_raw: 1620000000,
          is_current: false,
        },
        {
          rank: 3,
          trade_area_code: "SEONGSU",
          trade_area_name: "성수동",
          sales_formatted: "12.8억",
          sales_raw: 1280000000,
          is_current: true,
        },
        {
          rank: 4,
          trade_area_code: "GAROSU",
          trade_area_name: "가로수길",
          sales_formatted: "11.7억",
          sales_raw: 1170000000,
          is_current: false,
        },
        {
          rank: 5,
          trade_area_code: "KONKUK",
          trade_area_name: "건대입구",
          sales_formatted: "8.9억",
          sales_raw: 890000000,
          is_current: false,
        },
        {
          rank: 7,
          trade_area_code: "SEONGSU",
          trade_area_name: "성수동",
          sales_formatted: "12.8억",
          sales_raw: 1280000000,
          is_current: true,
        },
      ],
      by_volume: [
        {
          rank: 1,
          trade_area_code: "GANGNAM",
          trade_area_name: "강남역",
          sales_formatted: "62만",
          sales_raw: 620000,
          is_current: false,
        },
        {
          rank: 2,
          trade_area_code: "HONGDAE",
          trade_area_name: "홍대입구",
          sales_formatted: "58만",
          sales_raw: 580000,
          is_current: false,
        },
        {
          rank: 3,
          trade_area_code: "SEONGSU",
          trade_area_name: "성수동",
          sales_formatted: "45만",
          sales_raw: 450000,
          is_current: true,
        },
        {
          rank: 4,
          trade_area_code: "GAROSU",
          trade_area_name: "가로수길",
          sales_formatted: "36만",
          sales_raw: 360000,
          is_current: false,
        },
        {
          rank: 5,
          trade_area_code: "KONKUK",
          trade_area_name: "건대입구",
          sales_formatted: "32만",
          sales_raw: 320000,
          is_current: false,
        },
      ],
      by_growth: [
        {
          rank: 1,
          trade_area_code: "SHAROSU",
          trade_area_name: "샤로수길",
          sales_formatted: "+14.1%",
          sales_raw: 14.1,
          is_current: false,
        },
        {
          rank: 2,
          trade_area_code: "SEONGSU",
          trade_area_name: "성수동",
          sales_formatted: "+12.4%",
          sales_raw: 12.4,
          is_current: true,
        },
        {
          rank: 3,
          trade_area_code: "EULJIRO",
          trade_area_name: "을지로3가",
          sales_formatted: "+9.2%",
          sales_raw: 9.2,
          is_current: false,
        },
        {
          rank: 4,
          trade_area_code: "HONGDAE",
          trade_area_name: "홍대입구",
          sales_formatted: "+6.8%",
          sales_raw: 6.8,
          is_current: false,
        },
        {
          rank: 5,
          trade_area_code: "KONKUK",
          trade_area_name: "건대입구",
          sales_formatted: "+5.2%",
          sales_raw: 5.2,
          is_current: false,
        },
      ],
      by_score: [
        {
          rank: 1,
          trade_area_code: "SEONGSU",
          trade_area_name: "성수동",
          sales_formatted: "82점",
          sales_raw: 82,
          is_current: true,
        },
        {
          rank: 2,
          trade_area_code: "HONGDAE",
          trade_area_name: "홍대입구",
          sales_formatted: "78점",
          sales_raw: 78,
          is_current: false,
        },
        {
          rank: 3,
          trade_area_code: "SHAROSU",
          trade_area_name: "샤로수길",
          sales_formatted: "74점",
          sales_raw: 74,
          is_current: false,
        },
        {
          rank: 4,
          trade_area_code: "KONKUK",
          trade_area_name: "건대입구",
          sales_formatted: "71점",
          sales_raw: 71,
          is_current: false,
        },
        {
          rank: 5,
          trade_area_code: "GANGNAM",
          trade_area_name: "강남역",
          sales_formatted: "69점",
          sales_raw: 69,
          is_current: false,
        },
      ],
    },
    takeaway: {
      score: 82,
      growth_tag: "매출 증가율 +++",
      volume_tag: "거래건수 +++",
      competition_tag: "경쟁 강도 -",
      summary:
        "성수동은 거래량과 매출 성장성은 높은 편이지만 동일 업종 경쟁도 강합니다.",
      disclaimer:
        "실제 창업 성공 가능성을 의미하지 않는 데이터 기반 탐색 지표입니다.",
    },
  };
}

export function getMockDistrictPatterns(
  tradeAreaCode: string,
): DistrictPatterns {
  const code = tradeAreaCode.toUpperCase();

  if (code === "HONGDAE") {
    return {
      when: {
        peak_slot: "18–22시",
        insight: "심야 및 저녁 18-22시에 유동인구와 소비가 집중됩니다.",
        slots: [
          {
            slot: "06-11시",
            percentage: 8,
            is_peak: false,
            sales_amount: 129600000,
          },
          {
            slot: "11-14시",
            percentage: 16,
            is_peak: false,
            sales_amount: 259200000,
          },
          {
            slot: "14-17시",
            percentage: 22,
            is_peak: false,
            sales_amount: 356400000,
          },
          {
            slot: "17-21시",
            percentage: 38,
            is_peak: true,
            sales_amount: 615600000,
          },
          {
            slot: "21-24시",
            percentage: 16,
            is_peak: false,
            sales_amount: 259200000,
          },
        ],
      },
      who: {
        primary_target: "20대 남녀",
        target_badge: "주요 고객층",
        insight: "20대 청년층이 전체 매출의 60% 이상을 차지합니다.",
        demographics: [
          {
            age_group: "10대",
            percentage: 12,
            female_ratio: 55,
            male_ratio: 45,
            dominant_gender: "female",
            is_primary: false,
          },
          {
            age_group: "20대",
            percentage: 52,
            female_ratio: 58,
            male_ratio: 42,
            dominant_gender: "female",
            is_primary: true,
          },
          {
            age_group: "30대",
            percentage: 24,
            female_ratio: 48,
            male_ratio: 52,
            dominant_gender: "male",
            is_primary: false,
          },
          {
            age_group: "40대+",
            percentage: 12,
            female_ratio: 45,
            male_ratio: 55,
            dominant_gender: "male",
            is_primary: false,
          },
        ],
      },
      day: {
        peak_day: "토요일",
        peak_diff_badge: "+34%",
        insight: "토요일 매출이 주중 평균보다 34% 높습니다.",
        days: [
          { day: "월", percentage: 11, diff_from_average: -15, is_peak: false },
          { day: "화", percentage: 12, diff_from_average: -10, is_peak: false },
          { day: "수", percentage: 13, diff_from_average: -5, is_peak: false },
          { day: "목", percentage: 14, diff_from_average: 2, is_peak: false },
          { day: "금", percentage: 18, diff_from_average: 22, is_peak: false },
          { day: "토", percentage: 20, diff_from_average: 34, is_peak: true },
          { day: "일", percentage: 12, diff_from_average: -8, is_peak: false },
        ],
      },
    };
  }

  // Default: SEONGSU (Reference Image 2!)
  return {
    when: {
      peak_slot: "17–21시",
      insight: "저녁 17–21시에 소비가 가장 집중됩니다.",
      slots: [
        {
          slot: "06-11시",
          percentage: 10,
          is_peak: false,
          sales_amount: 128000000,
        },
        {
          slot: "11-14시",
          percentage: 18,
          is_peak: false,
          sales_amount: 230400000,
        },
        {
          slot: "14-17시",
          percentage: 24,
          is_peak: false,
          sales_amount: 307200000,
        },
        {
          slot: "17-21시",
          percentage: 36,
          is_peak: true,
          sales_amount: 460800000,
        },
        {
          slot: "21-24시",
          percentage: 12,
          is_peak: false,
          sales_amount: 153600000,
        },
      ],
    },
    who: {
      primary_target: "20대 여성",
      target_badge: "주요 고객층",
      insight: "20대 여성 소비 비중이 가장 높습니다.",
      demographics: [
        {
          age_group: "10대",
          percentage: 15,
          female_ratio: 52,
          male_ratio: 48,
          dominant_gender: "female",
          is_primary: false,
        },
        {
          age_group: "20대",
          percentage: 45,
          female_ratio: 65,
          male_ratio: 35,
          dominant_gender: "female",
          is_primary: true,
        },
        {
          age_group: "30대",
          percentage: 25,
          female_ratio: 52,
          male_ratio: 48,
          dominant_gender: "female",
          is_primary: false,
        },
        {
          age_group: "40대+",
          percentage: 15,
          female_ratio: 40,
          male_ratio: 60,
          dominant_gender: "male",
          is_primary: false,
        },
      ],
    },
    day: {
      peak_day: "금요일",
      peak_diff_badge: "+21%",
      insight: "금요일 매출이 주중 평균보다 21% 높습니다.",
      days: [
        { day: "월", percentage: 12, diff_from_average: -10, is_peak: false },
        { day: "화", percentage: 13, diff_from_average: -5, is_peak: false },
        { day: "수", percentage: 14, diff_from_average: 0, is_peak: false },
        { day: "목", percentage: 15, diff_from_average: 6, is_peak: false },
        { day: "금", percentage: 21, diff_from_average: 21, is_peak: true },
        { day: "토", percentage: 14, diff_from_average: 2, is_peak: false },
        { day: "일", percentage: 11, diff_from_average: -14, is_peak: false },
      ],
    },
  };
}

export function getMockDistrictCompetition(
  tradeAreaCode: string,
): DistrictCompetition {
  const code = tradeAreaCode.toUpperCase();
  if (code === "SHAROSU") {
    return {
      trade_area_code: "SHAROSU",
      // store_count: 58,
      // qoq_store_change: 3,
      competition_level: "보통",
      sales_level: "보통",
      volume_level: "보통",
      warning_text:
        "비교적 안정적이나 최근 신규 카페 입점이 점진적으로 늘어나는 추세입니다.",
    };
  }
  if (code === "HONGDAE") {
    return {
      trade_area_code: "HONGDAE",
      // store_count: 182,
      // qoq_store_change: 8,
      competition_level: "매우 높음",
      sales_level: "매우 높음",
      volume_level: "매우 높음",
      warning_text:
        "상권 활성도가 높은 만큼 점포 간 간격이 좁고 폐업률 변동성이 큽니다.",
    };
  }

  // Default: SEONGSU
  return {
    trade_area_code: "SEONGSU",
    // store_count: 134,
    // qoq_store_change: 12,
    competition_level: "매우 높음",
    sales_level: "높음",
    volume_level: "높음",
    warning_text: "수요도 크지만 동일 업종 공급 역시 빠르게 증가하고 있습니다.",
  };
}

export function getMockCompareData(
  tradeAreaCodes: string[],
): CompareDistrictData[] {
  const allDistricts: Record<string, CompareDistrictData> = {
    GAROSU: {
      trade_area_code: "GAROSU",
      trade_area_name: "가로수길",
      district: "강남구",
      exploration_score: 50,
      estimated_sales_formatted: "1억",
      estimated_sales: 100000000,
      transaction_count_formatted: "1만",
      transaction_count: 10000,
      growth_rate: 5,
      strongest_age_group: "테스트 데이터",
      strongest_time_period: "테스트 데이터",
      strongest_day: "테스트 데이터",
      competition_level: "보통",
      key_insight: "화면 검증용 가상 데이터입니다. 실제 상권 통계가 아닙니다.",
    },
    IKSEON: {
      trade_area_code: "IKSEON",
      trade_area_name: "익선동",
      district: "종로구",
      exploration_score: 50,
      estimated_sales_formatted: "1억",
      estimated_sales: 100000000,
      transaction_count_formatted: "1만",
      transaction_count: 10000,
      growth_rate: 5,
      strongest_age_group: "테스트 데이터",
      strongest_time_period: "테스트 데이터",
      strongest_day: "테스트 데이터",
      competition_level: "보통",
      key_insight: "화면 검증용 가상 데이터입니다. 실제 상권 통계가 아닙니다.",
    },
    EULJIRO: {
      trade_area_code: "EULJIRO",
      trade_area_name: "을지로3가",
      district: "중구",
      exploration_score: 50,
      estimated_sales_formatted: "1억",
      estimated_sales: 100000000,
      transaction_count_formatted: "1만",
      transaction_count: 10000,
      growth_rate: 5,
      strongest_age_group: "테스트 데이터",
      strongest_time_period: "테스트 데이터",
      strongest_day: "테스트 데이터",
      competition_level: "보통",
      key_insight: "화면 검증용 가상 데이터입니다. 실제 상권 통계가 아닙니다.",
    },
    SEONGSU: {
      trade_area_code: "SEONGSU",
      trade_area_name: "성수동",
      district: "성동구",
      exploration_score: 82,
      estimated_sales_formatted: "12.8억",
      estimated_sales: 1280000000,
      transaction_count_formatted: "45만",
      transaction_count: 450000,
      growth_rate: 12.4,
      // store_count: 134,
      // store_count_change: 12,
      strongest_age_group: "20대 여성 (45%)",
      strongest_time_period: "17–21시 (36%)",
      strongest_day: "금요일 (+21%)",
      competition_level: "매우 높음",
      key_insight: "트렌드 리딩 및 높은 매출 성장, 출점 과밀 주의",
    },
    HONGDAE: {
      trade_area_code: "HONGDAE",
      trade_area_name: "홍대입구",
      district: "마포구",
      exploration_score: 78,
      estimated_sales_formatted: "16.2억",
      estimated_sales: 1620000000,
      transaction_count_formatted: "58만",
      transaction_count: 580000,
      growth_rate: 6.8,
      // store_count: 182,
      // store_count_change: 8,
      strongest_age_group: "20대 남녀 (52%)",
      strongest_time_period: "18–22시 (38%)",
      strongest_day: "토요일 (+34%)",
      competition_level: "매우 높음",
      key_insight: "압도적 유동 거래량, 심야 및 주말 집중",
    },
    SHAROSU: {
      trade_area_code: "SHAROSU",
      trade_area_name: "샤로수길",
      district: "관악구",
      exploration_score: 74,
      estimated_sales_formatted: "7.4억",
      estimated_sales: 740000000,
      transaction_count_formatted: "28만",
      transaction_count: 280000,
      growth_rate: 14.1,
      // store_count: 58,
      // store_count_change: 3,
      strongest_age_group: "20대 1인가구 (48%)",
      strongest_time_period: "18–21시 (32%)",
      strongest_day: "금요일 (+18%)",
      competition_level: "보통",
      key_insight: "가장 높은 성장률(+14.1%), 상대적 경쟁 부담 완만",
    },
    KONKUK: {
      trade_area_code: "KONKUK",
      trade_area_name: "건대입구",
      district: "광진구",
      exploration_score: 71,
      estimated_sales_formatted: "8.9억",
      estimated_sales: 890000000,
      transaction_count_formatted: "32만",
      transaction_count: 320000,
      growth_rate: 5.2,
      // store_count: 96,
      // store_count_change: 5,
      strongest_age_group: "20대 학생 (50%)",
      strongest_time_period: "17–21시 (34%)",
      strongest_day: "금/토 (+16%)",
      competition_level: "높음",
      key_insight: "대학생 배후 수요 안정적, 저녁 시간대 집중",
    },
    GANGNAM: {
      trade_area_code: "GANGNAM",
      trade_area_name: "강남역",
      district: "강남구",
      exploration_score: 69,
      estimated_sales_formatted: "18.5억",
      estimated_sales: 1850000000,
      transaction_count_formatted: "62만",
      transaction_count: 620000,
      growth_rate: 2.1,
      // store_count: 240,
      // store_count_change: 15,
      strongest_age_group: "30대 직장인 (46%)",
      strongest_time_period: "11–14시 (38%)",
      strongest_day: "목/금 (+14%)",
      competition_level: "매우 높음",
      key_insight: "서울 최대 거래 규모이나 대형 프랜차이즈 과밀",
    },
  };

  return tradeAreaCodes.map((code) => {
    const result = allDistricts[code.toUpperCase()];

    if (!result) {
      throw new Error(`비교용 Mock 데이터가 없습니다: ${code}`);
    }

    return result;
  });
}
