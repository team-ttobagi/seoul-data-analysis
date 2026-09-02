import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Info, ArrowRight, CheckSquare, Square, ChevronDown } from "lucide-react";
import { api } from "../../shared/api/client";
import { Signals, ScorePill } from "../../shared/ui/Signals";
import { useCompareStore } from "../../shared/lib/store";

export const ExplorePage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedIndustry, setSelectedIndustry] = useState<string>("CS100010");
  const [selectedRegion, setSelectedRegion] = useState<string>("서울 전체");
  const [selectedQuarter, setSelectedQuarter] = useState<string>("2026 Q2");
  const [activeItemCode, setActiveItemCode] = useState<string>("SEONGSU");

  const { isDistrictSelected, toggleDistrict, selectedCodes } = useCompareStore();

  const { data: industries = [] } = useQuery({
    queryKey: ["industries"],
    queryFn: api.getIndustries,
  });

  const { data: recommendations = [], isLoading } = useQuery({
    queryKey: ["recommendations", selectedIndustry, selectedQuarter, selectedRegion],
    queryFn: () =>
      api.getRecommendations({
        industry_code: selectedIndustry,
        quarter: selectedQuarter,
        region: selectedRegion,
      }),
  });

  const currentIndustryName =
    industries.find((i) => i.code === selectedIndustry)?.name || "커피·음료";

  const handleDistrictClick = (code: string) => {
    navigate(`/district/${code}?industry=${selectedIndustry}&quarter=${encodeURIComponent(selectedQuarter)}`);
  };

  return (
    <div className="w-full bg-[#f5f5f0] min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12 pb-8 border-b-2 border-black">
        <div className="max-w-3xl space-y-4">
          {/* Badge */}
          <div>
            <span className="inline-block bg-[#d4ff00] text-black border border-black px-2.5 py-1 text-xs font-mono font-extrabold tracking-wider">
              EXPLORE BUSINESS DATA
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-3xl sm:text-5xl font-black tracking-tight text-black leading-[1.15]">
            {currentIndustryName} 창업,
            <br />
            서울 어디부터 볼까?
          </h1>

          {/* Subtitle */}
          <p className="text-base sm:text-lg text-gray-800 font-medium leading-relaxed pt-1">
            매출 성장 · 거래 활성도 · 경쟁 강도를 기준으로
            <br />
            먼저 살펴볼 상권을 찾았습니다.
          </p>
        </div>

        {/* Filters / Conditions Row */}
        <div className="mt-8 pt-6 border-t border-black flex flex-wrap items-center gap-y-3 gap-x-6 text-xs sm:text-sm font-mono text-gray-800">
          {/* Industry dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-gray-500 font-bold">업종</span>
            <div className="relative inline-block">
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="appearance-none bg-white border border-black px-3 py-1.5 pr-7 font-bold text-black cursor-pointer hover:bg-[#d4ff00]/20 focus:outline-none"
              >
                {industries.map((ind) => (
                  <option key={ind.code} value={ind.code}>
                    {ind.name}
                  </option>
                ))}
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          <span className="text-gray-300 hidden sm:inline">|</span>

          {/* Region dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-gray-500 font-bold">지역</span>
            <div className="relative inline-block">
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="appearance-none bg-white border border-black px-3 py-1.5 pr-7 font-bold text-black cursor-pointer hover:bg-[#d4ff00]/20 focus:outline-none"
              >
                <option value="서울 전체">서울 전체</option>
                <option value="성동구">성동구</option>
                <option value="마포구">마포구</option>
                <option value="관악구">관악구</option>
                <option value="광진구">광진구</option>
                <option value="강남구">강남구</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>

          <span className="text-gray-300 hidden sm:inline">|</span>

          {/* Quarter dropdown */}
          <div className="flex items-center gap-2">
            <span className="text-gray-500 font-bold">기준</span>
            <div className="relative inline-block">
              <select
                value={selectedQuarter}
                onChange={(e) => setSelectedQuarter(e.target.value)}
                className="appearance-none bg-white border border-black px-3 py-1.5 pr-7 font-bold text-black cursor-pointer hover:bg-[#d4ff00]/20 focus:outline-none"
              >
                <option value="2026 Q2">2026 Q2</option>
                <option value="2026 Q1">2026 Q1</option>
                <option value="2025 Q4">2025 Q4</option>
              </select>
              <ChevronDown className="w-3.5 h-3.5 absolute right-2 top-1/2 -translate-y-1/2 pointer-events-none" />
            </div>
          </div>
        </div>
      </section>

      {/* Main Swiss Grid Section */}
      <section className="max-w-7xl mx-auto border-b-2 border-black">
        <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[600px]">
          {/* Left Column: Ranked Candidates (~68%) */}
          <div className="lg:col-span-8 lg:border-r-2 border-black flex flex-col">
            {/* Section Header */}
            <div className="px-6 py-4 border-b-2 border-black flex items-center justify-between bg-[#f5f5f0]">
              <h2 className="text-xl sm:text-2xl font-black tracking-tight text-black">
                먼저 살펴볼 상권
              </h2>
              <span className="font-mono text-xs text-gray-600 font-bold tracking-widest uppercase">
                WHERE TO EXPLORE
              </span>
            </div>

            {/* Candidates List */}
            <div className="divide-y-2 divide-black flex-1">
              {isLoading ? (
                <div className="p-12 text-center font-mono text-gray-500">
                  데이터 집계 중...
                </div>
              ) : (
                recommendations.map((item, idx) => {
                  const isTopActive = activeItemCode === item.trade_area_code;
                  const isChecked = isDistrictSelected(item.trade_area_code);

                  return (
                    <div
                      key={item.trade_area_code}
                      onMouseEnter={() => setActiveItemCode(item.trade_area_code)}
                      className={`relative p-5 sm:p-6 transition-colors duration-150 group cursor-pointer ${
                        isTopActive
                          ? "bg-[#d4ff00]"
                          : "bg-[#f5f5f0] hover:bg-[#eeede6]"
                      }`}
                    >
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                        {/* Left Info: Rank + Name + Score + Signals */}
                        <div
                          className="flex-1"
                          onClick={() => handleDistrictClick(item.trade_area_code)}
                        >
                          <div className="flex items-center gap-3 sm:gap-4 flex-wrap">
                            {/* Rank */}
                            <span className="font-mono text-lg sm:text-xl font-black text-black">
                              {String(item.rank).padStart(2, "0")}
                            </span>

                            {/* District Name */}
                            <h3 className="text-xl sm:text-2xl font-black text-black tracking-tight group-hover:underline underline-offset-4">
                              {item.trade_area_name}
                            </h3>

                            {/* Score Pill */}
                            <ScorePill score={item.score} isSelected={isTopActive} />
                          </div>

                          {/* Signals */}
                          <div className="mt-3">
                            <Signals
                              growth={item.signals.growth}
                              transaction={item.signals.transaction}
                              competition={item.signals.competition}
                            />
                          </div>

                          {/* Short Explanation / Insight */}
                          {item.insight && (
                            <p className="mt-3 text-xs sm:text-sm font-medium text-black/90 leading-normal">
                              "{item.insight}"
                            </p>
                          )}
                        </div>

                        {/* Right Action: Compare Toggle + View Detail Arrow */}
                        <div className="flex items-center gap-2 sm:gap-3 self-end sm:self-center shrink-0">
                          {/* Compare Checkbox */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              toggleDistrict(item.trade_area_code);
                            }}
                            title="비교함에 추가/제외"
                            className="flex items-center gap-1.5 px-2.5 py-1.5 text-xs font-mono font-bold border border-black bg-white hover:bg-black hover:text-white transition-colors"
                          >
                            {isChecked ? (
                              <CheckSquare className="w-3.5 h-3.5 text-black" />
                            ) : (
                              <Square className="w-3.5 h-3.5 text-gray-500" />
                            )}
                            <span className="hidden sm:inline">비교</span>
                          </button>

                          {/* Detail Button */}
                          <button
                            onClick={() => handleDistrictClick(item.trade_area_code)}
                            className={`p-2 border border-black transition-all ${
                              isTopActive
                                ? "bg-black text-white hover:bg-white hover:text-black"
                                : "bg-white text-black hover:bg-[#d4ff00]"
                            }`}
                            aria-label={`${item.trade_area_name} 상세 분석 보기`}
                          >
                            <ArrowRight className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>

          {/* Right Column: Recommendation Factors & Disclaimer (~32%) */}
          <div className="lg:col-span-4 bg-[#f5f5f0] flex flex-col justify-between p-6 sm:p-8 space-y-8">
            {/* Top: Factors Weight Table */}
            <div className="space-y-6">
              <div>
                <h3 className="text-lg sm:text-xl font-black text-black">추천 기준</h3>
                <p className="text-xs font-mono text-gray-600 mt-0.5">
                  Exploration Score factors
                </p>
              </div>

              {/* Factors list with solid black bottom borders matching Reference 1 */}
              <div className="divide-y border-t border-b border-black font-mono text-xs sm:text-sm">
                <div className="flex justify-between py-3">
                  <span className="text-black font-medium">Sales Growth</span>
                  <span className="font-extrabold text-black">40%</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-black font-medium">Transaction Volume</span>
                  <span className="font-extrabold text-black">35%</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-black font-medium">Competition Intensity</span>
                  <span className="font-extrabold text-black">25%</span>
                </div>
              </div>

              {/* Dashed line */}
              <div className="border-t border-dashed border-black/40 pt-2 text-xs text-gray-600 leading-relaxed">
                <p>
                  * 경쟁 강도는 역산(Inverse) 반영되어, 과밀 출점 상권은 감점 처리됩니다.
                </p>
              </div>
            </div>

            {/* Bottom: Dark Disclaimer Box matching Reference 1 */}
            <div className="bg-[#121212] text-white p-5 border border-black space-y-2.5">
              <div className="flex items-center gap-2">
                <div className="w-5 h-5 rounded-full border border-[#d4ff00] text-[#d4ff00] flex items-center justify-center font-bold text-xs shrink-0">
                  i
                </div>
                <span className="text-xs font-bold font-mono text-[#d4ff00]">
                  DISCLAIMER
                </span>
              </div>
              <p className="text-xs text-gray-300 leading-relaxed font-sans">
                본 점수는 성공 예측이 아닌 탐색을 위한 발견 지수(Discovery Index)입니다. 실제 창업 시에는 추가적인 현장 조사가 필요합니다.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
