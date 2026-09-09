import React, { useState } from "react";
import {
  useParams,
  useSearchParams,
  Link,
  useNavigate,
} from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  CheckSquare,
  Square,
  Layers,
  ChevronDown,
} from "lucide-react";
import { api } from "../../shared/api/client";
import {
  RankBarChart,
  TimeBarChart,
  AgeGenderBarChart,
  DayBarChart,
} from "../../shared/ui/Charts";
import { useCompareStore } from "../../shared/lib/store";

/* ----------------------------- */
// Update by SoO 2026.09.07
//   store_count
//   store_count_change
/* ----------------------------- */

export const DistrictDetailPage: React.FC = () => {
  const { tradeAreaCode = "SEONGSU" } = useParams<{ tradeAreaCode: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const industryCode = searchParams.get("industry") || "CS100010";
  const quarter = searchParams.get("quarter") || "2026 Q2";

  const [rankTab, setRankTab] = useState<
    "sales" | "volume" | "growth" | "score"
  >("sales");

  const { isDistrictSelected, toggleDistrict } = useCompareStore();
  const isChecked = isDistrictSelected(tradeAreaCode);

  const { data: overview, isLoading: isOverviewLoading } = useQuery({
    queryKey: ["district-overview", tradeAreaCode, industryCode, quarter],
    queryFn: () =>
      api.getDistrictOverview(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
  });

  const { data: patterns, isLoading: isPatternsLoading } = useQuery({
    queryKey: ["district-patterns", tradeAreaCode, industryCode, quarter],
    queryFn: () =>
      api.getDistrictPatterns(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
  });

  const { data: competition, isLoading: isCompLoading } = useQuery({
    queryKey: ["district-competition", tradeAreaCode, industryCode, quarter],
    queryFn: () =>
      api.getDistrictCompetition(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
  });

  const { data: tradeAreas = [] } = useQuery({
    queryKey: ["trade-areas"],
    queryFn: api.getTradeAreas,
  });

  if (isOverviewLoading || !overview) {
    return (
      <div className="max-w-7xl mx-auto p-12 text-center font-mono">
        상권 데이터 로딩 중...
      </div>
    );
  }

  const getRankItems = () => {
    if (rankTab === "volume") return overview.rankings.by_volume;
    if (rankTab === "growth") return overview.rankings.by_growth;
    if (rankTab === "score") return overview.rankings.by_score;
    return overview.rankings.by_sales;
  };

  return (
    <div className="w-full bg-[#f5f5f0] min-h-[calc(100vh-4rem)] pb-12">
      {/* Top Breadcrumb & Switcher Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 flex flex-wrap items-center justify-between gap-4">
        <Link
          to="/explore"
          className="inline-flex items-center gap-1.5 font-mono text-xs font-bold text-gray-700 hover:text-black hover:underline"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>목록으로 돌아가기</span>
        </Link>

        {/* Quick district selector */}
        <div className="flex items-center gap-3">
          {/* <div className="flex items-center gap-2 font-mono text-xs">
            <span className="text-gray-500 font-bold">상권 변경:</span>
            <div className="relative inline-block">
              <select
                value={tradeAreaCode.toUpperCase()}
                onChange={(e) =>
                  navigate(
                    `/district/${e.target.value}?industry=${industryCode}&quarter=${encodeURIComponent(quarter)}`,
                  )
                }
                className="appearance-none bg-white border border-black px-3 py-1 pr-6 font-bold text-black cursor-pointer hover:bg-[#d4ff00]/20 focus:outline-none"
              >
                {tradeAreas.map((ta) => (
                  <option key={ta.code} value={ta.code}>
                    {ta.name} ({ta.district})
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          <button
            onClick={() => toggleDistrict(tradeAreaCode)}
            className="flex items-center gap-1.5 px-3 py-1 text-xs font-mono font-bold border border-black bg-white hover:bg-black hover:text-white transition-colors"
          >
            {isChecked ? (
              <CheckSquare className="w-3.5 h-3.5 text-black" />
            ) : (
              <Square className="w-3.5 h-3.5 text-gray-400" />
            )}
            <span>{isChecked ? "비교함 선택됨" : "비교함 담기"}</span>
          </button> */}
        </div>
      </div>

      {/* Hero Section matching Reference 2 */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-4 pb-6">
        <div className="space-y-3">
          <div>
            <span className="inline-block bg-[#d4ff00] text-black border border-black px-2.5 py-0.5 text-xs font-mono font-extrabold tracking-wider">
              EXPLORE BUSINESS DATA
            </span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-black leading-[1.15]">
            {overview.trade_area_name}에서 {overview.industry_name}는
            <br />
            어떻게 소비될까?
          </h1>

          <div className="flex items-center gap-2 text-xs sm:text-sm font-mono text-gray-700 pt-1">
            <span className="font-bold text-black">
              서울 &gt; {overview.trade_area_name} &gt; {overview.industry_name}
            </span>
            <span>|</span>
            <span>{overview.quarter}</span>
          </div>
        </div>
      </section>

      {/* KPI Row matching Reference 2 (4 equal columns with black borders) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 border-2 border-black divide-x-2 divide-y-2 md:divide-y-0 divide-black bg-[#f5f5f0]">
          {/* KPI 1 */}
          <div className="p-5 sm:p-6 bg-white">
            <span className="block font-mono text-xs text-gray-600 font-bold">
              추정 매출
            </span>
            <span className="block text-2xl sm:text-3xl font-black text-black mt-2 tracking-tight">
              {overview.kpis.estimated_sales_formatted}
            </span>
          </div>

          {/* KPI 2 */}
          <div className="p-5 sm:p-6 bg-white">
            <span className="block font-mono text-xs text-gray-600 font-bold">
              거래 건수
            </span>
            <span className="block text-2xl sm:text-3xl font-black text-black mt-2 tracking-tight">
              {overview.kpis.transaction_count_formatted}
            </span>
          </div>

          {/* KPI 3 */}
          <div className="p-5 sm:p-6 bg-white">
            <span className="block font-mono text-xs text-gray-600 font-bold">
              서울 상권 순위
            </span>
            <span className="block text-2xl sm:text-3xl font-black text-black mt-2 tracking-tight">
              {overview.kpis.seoul_rank}위
            </span>
          </div>

          {/* KPI 4 - Highlighted in Lime matching Reference 2 */}
          <div className="p-5 sm:p-6 bg-[#d4ff00]">
            <span className="block font-mono text-xs text-black font-bold">
              전분기 대비
            </span>
            <span className="block text-2xl sm:text-3xl font-black text-black mt-2 tracking-tight">
              +{overview.kpis.qoq_growth_rate}%
            </span>
          </div>
        </div>
      </section>

      {/* Main Grid Content matching Reference 2 (2x2 Grid) */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 border-2 border-black divide-y-2 lg:divide-y-0 lg:divide-x-2 divide-black bg-[#f5f5f0]">
          {/* Top Left: 어디가 강할까? / 상권 비교 순위 */}
          <div className="p-6 sm:p-8 flex flex-col justify-between space-y-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-black">
                어디가 강할까?
              </h2>
              <p className="text-xs font-mono text-gray-600 mt-1">
                {overview.industry_name} · 서울 전체 상권
              </p>

              {/* Filter Tabs */}
              <div className="mt-4 flex items-center gap-1.5 flex-wrap font-mono text-xs">
                <span className="text-gray-500 font-bold mr-1">RANK BY</span>
                <button
                  onClick={() => setRankTab("sales")}
                  className={`px-2 py-1 border border-black font-bold transition-colors ${
                    rankTab === "sales"
                      ? "bg-[#d4ff00] text-black"
                      : "bg-white text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  [매출]
                </button>
                <button
                  onClick={() => setRankTab("volume")}
                  className={`px-2 py-1 border border-black font-bold transition-colors ${
                    rankTab === "volume"
                      ? "bg-[#d4ff00] text-black"
                      : "bg-white text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  거래건수
                </button>
                <button
                  onClick={() => setRankTab("growth")}
                  className={`px-2 py-1 border border-black font-bold transition-colors ${
                    rankTab === "growth"
                      ? "bg-[#d4ff00] text-black"
                      : "bg-white text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  성장률
                </button>
                <button
                  onClick={() => setRankTab("score")}
                  className={`px-2 py-1 border border-black font-bold transition-colors ${
                    rankTab === "score"
                      ? "bg-[#d4ff00] text-black"
                      : "bg-white text-gray-700 hover:bg-gray-100"
                  }`}
                >
                  탐색점수
                </button>
              </div>
            </div>

            {/* Ranking Bar List */}
            <div className="my-2">
              <RankBarChart
                items={getRankItems()}
                currentCode={overview.trade_area_code}
                metricLabel={rankTab}
                onSelectDistrict={(code) =>
                  navigate(
                    `/district/${code}?industry=${industryCode}&quarter=${encodeURIComponent(quarter)}`,
                  )
                }
              />
            </div>

            {/* Footer summary */}
            <div className="border-t border-black pt-3 text-xs font-mono text-gray-700 flex justify-between">
              <span>
                {overview.trade_area_name} · 서울 전체{" "}
                {overview.kpis.seoul_rank}위
              </span>
              <span className="text-gray-500">
                상위 {overview.kpis.sales_percentile}%
              </span>
            </div>
          </div>

          {/* Top Right: 언제 가장 많이 팔릴까? (WHEN) */}
          <div className="p-6 sm:p-8 flex flex-col justify-between space-y-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-black">
                언제 가장 많이 팔릴까?
              </h2>
              <p className="text-xs font-mono text-gray-600 mt-1">
                시간대별 매출 비중 분포
              </p>
            </div>

            {/* Time Bar Chart */}
            {patterns && (
              <div className="my-2">
                <TimeBarChart
                  slots={patterns.when.slots}
                  peakSlot={patterns.when.peak_slot}
                />
              </div>
            )}

            {/* Insight quote */}
            <div className="border-l-4 border-[#d4ff00] pl-3 py-1 text-xs sm:text-sm font-medium text-black">
              {patterns?.when.insight ||
                "저녁 17–21시에 소비가 가장 집중됩니다."}
            </div>
          </div>
        </div>

        {/* Middle 2 Row: WHO & DAY */}
        <div className="grid grid-cols-1 lg:grid-cols-2 border-2 border-t-0 border-black divide-y-2 lg:divide-y-0 lg:divide-x-2 divide-black bg-[#f5f5f0]">
          {/* Middle Left: 누가 가장 많이 살까? (WHO) */}
          <div className="p-6 sm:p-8 flex flex-col justify-between space-y-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-black">
                누가 가장 많이 살까?
              </h2>

              {/* Big primary target label matching Reference 2 */}
              <div className="mt-4 flex items-center gap-3">
                <span className="text-3xl sm:text-4xl font-black text-black tracking-tight">
                  {patterns?.who.primary_target || "20대 여성"}
                </span>
                <span className="bg-[#d4ff00] text-black border border-black px-2 py-0.5 text-xs font-mono font-bold">
                  {patterns?.who.target_badge || "주요 고객층"}
                </span>
              </div>
            </div>

            {/* Demographics Bar Breakdown */}
            {patterns && (
              <div className="my-2">
                <AgeGenderBarChart
                  demographics={patterns.who.demographics}
                  primaryTarget={patterns.who.primary_target}
                />
              </div>
            )}

            {/* Insight quote */}
            <div className="border-l-4 border-[#d4ff00] pl-3 py-1 text-xs sm:text-sm font-medium text-black">
              {patterns?.who.insight || "20대 여성 소비 비중이 가장 높습니다."}
            </div>
          </div>

          {/* Middle Right: 어느 요일이 강할까? (DAY) */}
          <div className="p-6 sm:p-8 flex flex-col justify-between space-y-6">
            <div>
              <h2 className="text-xl sm:text-2xl font-black text-black">
                어느 요일이 강할까?
              </h2>
              <p className="text-xs font-mono text-gray-600 mt-1">
                요일별 매출 집중도 및 주중 대비 증감
              </p>
            </div>

            {/* Day Bar Chart */}
            {patterns && (
              <div className="my-2">
                <DayBarChart
                  days={patterns.day.days}
                  peakDay={patterns.day.peak_day}
                  peakDiffBadge={patterns.day.peak_diff_badge}
                />
              </div>
            )}

            {/* Insight quote */}
            <div className="border-l-4 border-[#d4ff00] pl-3 py-1 text-xs sm:text-sm font-medium text-black">
              {patterns?.day.insight ||
                "금요일 매출이 주중 평균보다 21% 높습니다."}
            </div>
          </div>
        </div>

        {/* Bottom Section: Competition & Overall Insight matching Reference 2 (Dark container) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 border-2 border-t-0 border-black bg-[#121212] text-white">
          {/* Left Dark Card: 경쟁은 어떨까? (주의할 점) (~38%) */}
          <div className="lg:col-span-5 p-6 sm:p-8 border-b-2 lg:border-b-0 lg:border-r-2 border-black flex flex-col justify-between space-y-6">
            <div>
              <h3 className="text-xl sm:text-2xl font-black text-[#d4ff00] tracking-tight">
                경쟁은 어떨까?
              </h3>
              {/* === Update by SoO 2026.09.07 ===========
                      2. [fix] 점포 관련 UI 및 데이터 참조 제거
                        2-1. District 상세 화면의 점포 수 표시 제거
              */}
              {/* <div className="mt-4">
                <span className="block font-mono text-xs text-gray-400 font-medium">동일 업종</span>
                <div className="flex items-baseline gap-3 mt-1">
                  <span className="text-3xl sm:text-4xl font-black text-white">
                    {competition?.store_count || 134}개
                  </span>
                  <span className="text-xs font-mono text-gray-400">
                    전분기 대비 <span className="text-[#d4ff00] font-bold">+{competition?.qoq_store_change || 12}개</span>
                  </span>
                </div>
              </div> */}
            </div>

            {/* Metric Level List matching Reference 2 */}
            <div className="divide-y divide-gray-800 border-t border-b border-gray-800 font-mono text-xs sm:text-sm">
              <div className="flex justify-between items-center py-2.5">
                <span className="text-gray-300">매출 수준</span>
                <span className="bg-white text-black px-2 py-0.5 font-bold text-xs">
                  {competition?.sales_level || "높음"}
                </span>
              </div>

              <div className="flex justify-between items-center py-2.5">
                <span className="text-gray-300">거래량</span>
                <span className="bg-white text-black px-2 py-0.5 font-bold text-xs">
                  {competition?.volume_level || "높음"}
                </span>
              </div>

              <div className="flex justify-between items-center py-2.5">
                <span className="text-gray-300">경쟁 강도</span>
                <span className="bg-[#ff3b30] text-white px-2 py-0.5 font-bold text-xs">
                  {competition?.competition_level || "매우 높음"}
                </span>
              </div>
            </div>

            {/* Warning Interpretation */}
            <p className="text-xs text-gray-400 leading-relaxed font-sans">
              {competition?.warning_text ||
                "수요도 크지만 동일 업종 공급 역시 빠르게 증가하고 있습니다."}
            </p>
          </div>

          {/* Right Dark Card: OVERALL INSIGHT & Score 82 (~62%) */}
          <div className="lg:col-span-7 p-6 sm:p-8 flex flex-col justify-between space-y-6">
            <div>
              <span className="text-xs font-mono font-bold tracking-widest text-gray-400 uppercase">
                OVERALL INSIGHT
              </span>

              {/* Giant Score */}
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-5xl sm:text-7xl font-black text-[#d4ff00] tracking-tighter">
                  SCORE {overview.takeaway.score}
                </span>
                <span className="text-xl sm:text-2xl font-mono text-gray-500 font-bold">
                  /100
                </span>
              </div>

              {/* Signal Badges matching Reference 2 */}
              <div className="flex flex-wrap items-center gap-2 mt-4 font-mono text-xs">
                <span className="bg-[#d4ff00] text-black px-2.5 py-1 font-bold">
                  {overview.takeaway.growth_tag}
                </span>
                <span className="bg-[#d4ff00] text-black px-2.5 py-1 font-bold">
                  {overview.takeaway.volume_tag}
                </span>
                <span className="border border-red-500 text-red-400 px-2.5 py-1 font-bold">
                  {overview.takeaway.competition_tag}
                </span>
              </div>
            </div>

            {/* Quote Conclusion matching Reference 2 */}
            <div className="border-l-4 border-[#d4ff00] pl-4 py-2">
              <p className="text-base sm:text-xl font-bold text-white leading-snug">
                "{overview.takeaway.summary}"
              </p>
            </div>

            {/* Disclaimer note */}
            <p className="text-[11px] font-mono text-gray-500">
              * {overview.takeaway.disclaimer}
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
