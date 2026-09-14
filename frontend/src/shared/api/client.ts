import axios from "axios";

import {
  TradeArea,
  TradeAreaResponse,
  TradeAreaSearchParams,
  District,
  Industry,
  RecommendationItem,
  DistrictOverview,
  DistrictPatterns,
  DistrictCompetition,
  CompareDistrictData,
} from "../types";

import {
  MOCK_DISTRICTS,
  MOCK_INDUSTRIES,
  MOCK_TRADE_AREA_RESPONSES,
  MOCK_TRADE_AREAS,
  getMockRecommendations,
  getMockDistrictOverview,
  getMockDistrictPatterns,
  getMockDistrictCompetition,
  getMockCompareData,
} from "./mockData";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(
  /\/$/,
  "",
);

/**
 * Mock 데이터는 개발 환경에서,
 * 그리고 VITE_USE_MOCK_API=true인 경우에만 사용한다.
 *
 * API 요청 실패를 이유로 Mock 데이터를 반환하지 않는다.
 */
const USE_MOCK =
  import.meta.env.DEV && import.meta.env.VITE_USE_MOCK_API === "true";

/**
 * 공통 Axios API Client
 */
const apiClient = axios.create({
  baseURL: API_BASE_URL,

  // 기존 1500ms보다 여유 있게 설정
  timeout: 5000,

  headers: {
    "Content-Type": "application/json",
  },

  /**
   * JSON 응답이 깨져 있을 경우
   * parsing 오류를 숨기지 않도록 설정
   */
  responseType: "json",

  transitional: {
    silentJSONParsing: false,
    forcedJSONParsing: true,
  },
});

/**
 * 성공 응답은 그대로 반환하고,
 * 실패 응답은 절대 성공 데이터로 변환하지 않는다.
 *
 * 404 / 422 / 500
 * Network Error
 * Timeout
 * JSON Parsing Error
 *
 * 모두 호출부까지 전달된다.
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(error),
);

export const api = {
  /**
   * 선택한 자치구의 상권 목록 및 검색
   */
  searchTradeAreas: async (
    params: TradeAreaSearchParams & { signgu_cd: string },
    signal?: AbortSignal,
  ): Promise<TradeArea[]> => {
    const keyword = params.keyword?.trim() || undefined;

    if (USE_MOCK) {
      return MOCK_TRADE_AREAS.filter(
        (area) => area.district_code === params.signgu_cd,
      )
        .filter(
          (area) =>
            !keyword || area.name.toLowerCase().includes(keyword.toLowerCase()),
        )
        .sort(
          (a, b) =>
            a.name.localeCompare(b.name, "ko") || a.code.localeCompare(b.code),
        );
    }

    const response = await apiClient.get<TradeArea[]>("/trade-areas/search", {
      params: {
        signgu_cd: params.signgu_cd,
        keyword,
      },
      signal,
    });

    return response.data;
  },
  /**
   * 자치구 목록 조회
   */
  getDistricts: async (): Promise<District[]> => {
    if (USE_MOCK) {
      return MOCK_DISTRICTS;
    }

    const response = await apiClient.get<District[]>("/districts");

    return response.data;
  },

  /**
   * 전체 상권 목록 조회
   */
  getTradeAreas: async (
    _params: TradeAreaSearchParams = {},
    signal?: AbortSignal,
  ): Promise<TradeAreaResponse[]> => {
    if (USE_MOCK) {
      return MOCK_TRADE_AREA_RESPONSES;
    }

    const response = await apiClient.get<TradeAreaResponse[]>("/trade-areas", {
      signal,
    });

    return response.data;
  },

  /**
   * 업종 목록
   */
  getIndustries: async (): Promise<Industry[]> => {
    if (USE_MOCK) {
      return MOCK_INDUSTRIES;
    }

    const response = await apiClient.get<Industry[]>("/industries");

    return response.data;
  },

  /**
   * 추천 상권
   */
  getRecommendations: async (params?: {
    industry_code?: string;
    quarter?: string;
    region?: string;
  }): Promise<RecommendationItem[]> => {
    if (USE_MOCK) {
      return getMockRecommendations(params?.industry_code, params?.quarter);
    }

    const response = await apiClient.get<RecommendationItem[]>(
      "/analytics/recommendations",
      {
        params: {
          industry_code: params?.industry_code,
          quarter: params?.quarter,
          region: params?.region,
        },
      },
    );

    return response.data;
  },

  /**
   * 상권 개요
   */
  getDistrictOverview: async (
    tradeAreaCode: string,
    params?: {
      industry_code?: string;
      quarter?: string;
    },
  ): Promise<DistrictOverview> => {
    if (USE_MOCK) {
      return getMockDistrictOverview(tradeAreaCode);
    }

    const response = await apiClient.get<DistrictOverview>(
      `/trade-areas/${tradeAreaCode}/overview`,
      {
        params: {
          industry_code: params?.industry_code,
          quarter: params?.quarter,
        },
      },
    );

    return response.data;
  },

  /**
   * 상권 패턴
   */
  getDistrictPatterns: async (
    tradeAreaCode: string,
    params?: {
      industry_code?: string;
      quarter?: string;
    },
  ): Promise<DistrictPatterns> => {
    if (USE_MOCK) {
      return getMockDistrictPatterns(tradeAreaCode);
    }

    const response = await apiClient.get<DistrictPatterns>(
      `/trade-areas/${tradeAreaCode}/patterns`,
      {
        params: {
          industry_code: params?.industry_code,
          quarter: params?.quarter,
        },
      },
    );

    return response.data;
  },

  /**
   * 상권 경쟁 현황
   */
  getDistrictCompetition: async (
    tradeAreaCode: string,
    params?: {
      industry_code?: string;
      quarter?: string;
    },
  ): Promise<DistrictCompetition> => {
    if (USE_MOCK) {
      return getMockDistrictCompetition(tradeAreaCode);
    }

    const response = await apiClient.get<DistrictCompetition>(
      `/trade-areas/${tradeAreaCode}/competition`,
      {
        params: {
          industry_code: params?.industry_code,
          quarter: params?.quarter,
        },
      },
    );

    return response.data;
  },

  /**
   * 상권 비교
   */
  getCompareData: async (params: {
    trade_area_codes: string[];
    industry_code?: string;
    quarter?: string;
  }): Promise<CompareDistrictData[]> => {
    if (USE_MOCK) {
      return getMockCompareData(params.trade_area_codes);
    }

    const response = await apiClient.get<CompareDistrictData[]>("/compare", {
      params: {
        trade_area_codes: params.trade_area_codes.join(","),
        industry_code: params.industry_code,
        quarter: params.quarter,
      },
    });

    return response.data;
  },
};

export { apiClient };
