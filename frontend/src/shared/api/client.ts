// Centralized typed API client for SEOUL DATA PLAYGROUND

import {
  TradeArea,
  Industry,
  RecommendationItem,
  DistrictOverview,
  DistrictPatterns,
  DistrictCompetition,
  CompareDistrictData,
} from "../types";
import {
  MOCK_INDUSTRIES,
  MOCK_TRADE_AREAS,
  getMockRecommendations,
  getMockDistrictOverview,
  getMockDistrictPatterns,
  getMockDistrictCompetition,
  getMockCompareData,
} from "./mockData";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "/api/v1").replace(/\/$/, "");

async function fetchWithFallback<T>(url: string, fallbackFn: () => T): Promise<T> {
  try {
    const res = await fetch(url, {
      headers: { "Content-Type": "application/json" },
      signal: AbortSignal.timeout(1500),
    });
    if (!res.ok) {
      return fallbackFn();
    }
    return (await res.json()) as T;
  } catch {
    // If backend is not running or network fails, use deterministic local data
    return fallbackFn();
  }
}

export const api = {
  getTradeAreas: async (): Promise<TradeArea[]> => {
    return fetchWithFallback(`${API_BASE_URL}/trade-areas`, () => MOCK_TRADE_AREAS);
  },

  getIndustries: async (): Promise<Industry[]> => {
    return fetchWithFallback(`${API_BASE_URL}/industries`, () => MOCK_INDUSTRIES);
  },

  getRecommendations: async (params?: {
    industry_code?: string;
    quarter?: string;
    region?: string;
  }): Promise<RecommendationItem[]> => {
    const query = new URLSearchParams();
    if (params?.industry_code) query.set("industry_code", params.industry_code);
    if (params?.quarter) query.set("quarter", params.quarter);
    if (params?.region) query.set("region", params.region);

    const url = `${API_BASE_URL}/analytics/recommendations?${query.toString()}`;
    return fetchWithFallback(url, () =>
      getMockRecommendations(params?.industry_code, params?.quarter)
    );
  },

  getDistrictOverview: async (
    tradeAreaCode: string,
    params?: { industry_code?: string; quarter?: string }
  ): Promise<DistrictOverview> => {
    const query = new URLSearchParams();
    if (params?.industry_code) query.set("industry_code", params.industry_code);
    if (params?.quarter) query.set("quarter", params.quarter);

    const url = `${API_BASE_URL}/trade-areas/${tradeAreaCode}/overview?${query.toString()}`;
    return fetchWithFallback(url, () => getMockDistrictOverview(tradeAreaCode));
  },

  getDistrictPatterns: async (
    tradeAreaCode: string,
    params?: { industry_code?: string; quarter?: string }
  ): Promise<DistrictPatterns> => {
    const query = new URLSearchParams();
    if (params?.industry_code) query.set("industry_code", params.industry_code);
    if (params?.quarter) query.set("quarter", params.quarter);

    const url = `${API_BASE_URL}/trade-areas/${tradeAreaCode}/patterns?${query.toString()}`;
    return fetchWithFallback(url, () => getMockDistrictPatterns(tradeAreaCode));
  },

  getDistrictCompetition: async (
    tradeAreaCode: string,
    params?: { industry_code?: string; quarter?: string }
  ): Promise<DistrictCompetition> => {
    const query = new URLSearchParams();
    if (params?.industry_code) query.set("industry_code", params.industry_code);
    if (params?.quarter) query.set("quarter", params.quarter);

    const url = `${API_BASE_URL}/trade-areas/${tradeAreaCode}/competition?${query.toString()}`;
    return fetchWithFallback(url, () => getMockDistrictCompetition(tradeAreaCode));
  },

  getCompareData: async (params: {
    trade_area_codes: string[];
    industry_code?: string;
    quarter?: string;
  }): Promise<CompareDistrictData[]> => {
    const query = new URLSearchParams();
    query.set("trade_area_codes", params.trade_area_codes.join(","));
    if (params?.industry_code) query.set("industry_code", params.industry_code);
    if (params?.quarter) query.set("quarter", params.quarter);

    const url = `${API_BASE_URL}/compare?${query.toString()}`;
    return fetchWithFallback(url, () => getMockCompareData(params.trade_area_codes));
  },
};
