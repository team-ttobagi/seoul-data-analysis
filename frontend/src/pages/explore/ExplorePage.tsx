import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Info,
  ArrowRight,
  CheckSquare,
  Square,
  ChevronDown,
} from "lucide-react";
import { api } from "../../shared/api/client";
import { Signals, ScorePill } from "../../shared/ui/Signals";
import { useCompareStore } from "../../shared/lib/store";
import type { Industry, RecommendationItem } from "../../shared/types";

interface ExploreFilterBarProps {
  industries: Industry[];
  selectedIndustry: string;
  setSelectedIndustry: (value: string) => void;
  selectedRegion: string;
  setSelectedRegion: (value: string) => void;
  selectedQuarter: string;
  setSelectedQuarter: (value: string) => void;
  recommendations: RecommendationItem[];
  selectedCodes: string[];
  toggleDistrict: (code: string) => void;
  clearDistricts: () => void;
  onOpenCompare: () => void;
}

const ExploreFilterBar: React.FC<ExploreFilterBarProps> = ({
  industries,
  selectedIndustry,
  setSelectedIndustry,
  selectedRegion,
  setSelectedRegion,
  selectedQuarter,
  setSelectedQuarter,
  recommendations,
  selectedCodes,
  toggleDistrict,
  clearDistricts,
  onOpenCompare,
}) => {
  const selectedDistricts = recommendations.filter((district) =>
    selectedCodes.includes(district.trade_area_code),
  );
  const candidateRecommendations = recommendations
    .filter((district) => !selectedCodes.includes(district.trade_area_code))
    .slice(0, 6);

  return (
    <div className="mt-6 md:mt-8 border border-black bg-white shadow-sm">
      <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-black border-b border-black bg-white">
        {[
          {
            label: "업종 카테고리",
            tag: "INDUSTRY",
            value:
              industries.find((industry) => industry.code === selectedIndustry)
                ?.name || "커피·음료",
            options: industries.map((industry) => ({
              value: industry.name,
              label: industry.name,
            })),
            onChange: (value: string) => {
              const industry = industries.find((item) => item.name === value);
              if (industry) setSelectedIndustry(industry.code);
            },
          },
          {
            label: "분석 지역",
            tag: "REGION",
            value: selectedRegion,
            options: [
              "서울 전체",
              "성동·광진구",
              "마포·용산구",
              "강남·서초구",
              "종로·중구",
              "관악구",
            ].map((value) => ({ value, label: value })),
            onChange: setSelectedRegion,
          },
          {
            label: "기준 분기",
            tag: "TIMELINE",
            value: selectedQuarter,
            options: ["2026 Q2", "2026 Q1", "2025 Q4"].map((value) => ({
              value,
              label: value === "2026 Q2" ? "2026 Q2 (최신 집계)" : value,
            })),
            onChange: setSelectedQuarter,
          },
        ].map((item) => (
          <div
            key={item.tag}
            className="p-3.5 flex flex-col justify-center gap-1 hover:bg-gray-50 transition-colors relative"
          >
            <div className="flex items-center justify-between">
              <span className="text-[10px] font-mono font-bold text-gray-500 uppercase tracking-wider">
                {item.label}
              </span>
              <span className="text-[9px] font-mono px-1.5 py-0.2 bg-gray-200 text-gray-800 rounded-none">
                {item.tag}
              </span>
            </div>
            <div className="relative flex items-center justify-between mt-0.5">
              <select
                value={item.value}
                onChange={(event) => item.onChange(event.target.value)}
                className="w-full appearance-none bg-transparent font-bold text-sm text-black cursor-pointer focus:outline-none pr-6"
              >
                {item.options.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
              <span className="pointer-events-none absolute right-0 text-xs text-gray-600 font-bold">
                ▼
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="p-4 bg-[#f2f2ee] flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="flex flex-col gap-2.5">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 mr-2">
              <span className="w-1.5 h-1.5 bg-black inline-block" />
              <span className="text-xs font-black text-black tracking-tight">
                비교 상권 트레이
              </span>
              <span className="font-mono text-[11px] font-bold bg-black text-[#d8fc03] px-1.5 py-0.5">
                {selectedDistricts.length} / 4
              </span>
            </div>
            {selectedDistricts.length === 0 ? (
              <span className="text-xs text-gray-500 italic py-1">
                상권 카드의 '비교' 버튼을 눌러 비교군을 담아보세요.
              </span>
            ) : (
              selectedDistricts.map((district) => (
                <div
                  key={district.trade_area_code}
                  className="inline-flex items-center gap-2 px-2.5 py-1 bg-white border border-black text-black text-xs font-bold shadow-sm"
                >
                  <span className="w-1.5 h-1.5 inline-block border border-black bg-black" />
                  <span>{district.trade_area_name}</span>
                  <button
                    onClick={() => toggleDistrict(district.trade_area_code)}
                    className="hover:text-red-600 text-xs font-bold leading-none text-gray-500 transition-colors cursor-pointer"
                    title="제거"
                    type="button"
                  >
                    ✕
                  </button>
                </div>
              ))
            )}
          </div>
          <div className="flex flex-wrap items-center gap-1.5 pt-0.5 text-xs">
            <span className="text-[11px] font-medium text-gray-500 mr-1">
              추천 추가:
            </span>
            {candidateRecommendations.map((district) => (
              <button
                key={district.trade_area_code}
                onClick={() => toggleDistrict(district.trade_area_code)}
                className="px-2 py-0.5 bg-white border border-gray-400 text-gray-700 text-xs font-medium hover:border-black hover:text-black transition-all cursor-pointer"
                type="button"
              >
                + {district.trade_area_name}
              </button>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3 shrink-0 self-end lg:self-center border-t lg:border-t-0 border-gray-300 pt-2 lg:pt-0 w-full lg:w-auto justify-end">
          {selectedDistricts.length > 0 && (
            <button
              onClick={clearDistricts}
              className="text-xs text-gray-600 hover:text-black underline underline-offset-2 font-medium px-2 py-1 transition-colors cursor-pointer"
              type="button"
            >
              선택 초기화
            </button>
          )}
          <button
            onClick={onOpenCompare}
            disabled={selectedDistricts.length === 0}
            className={`inline-flex items-center gap-2 px-4 py-2 text-xs font-bold border border-black transition-colors shadow-sm cursor-pointer ${selectedDistricts.length > 0 ? "bg-black text-white hover:bg-[#d8fc03] hover:text-black" : "bg-gray-300 text-gray-600 border-gray-400 cursor-not-allowed"}`}
            type="button"
          >
            <span>{selectedDistricts.length}개 상권 나란히 비교</span>
            <span className="text-xs">➔</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export const ExplorePage: React.FC = () => {
  const navigate = useNavigate();
  const [selectedIndustry, setSelectedIndustry] = useState<string>("CS100010");
  const [selectedRegion, setSelectedRegion] = useState<string>("서울 전체");
  const [selectedQuarter, setSelectedQuarter] = useState<string>("2026 Q2");
  const [activeItemCode, setActiveItemCode] = useState<string>("SEONGSU");

  const { isDistrictSelected, toggleDistrict, selectedCodes } =
    useCompareStore();

  const { data: industries = [] } = useQuery({
    queryKey: ["industries"],
    queryFn: api.getIndustries,
  });

  const { data: recommendations = [], isLoading } = useQuery({
    queryKey: [
      "recommendations",
      selectedIndustry,
      selectedQuarter,
      selectedRegion,
    ],
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
    navigate(
      `/district/${code}?industry=${selectedIndustry}&quarter=${encodeURIComponent(selectedQuarter)}`,
    );
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
        <ExploreFilterBar
          industries={industries}
          selectedIndustry={selectedIndustry}
          setSelectedIndustry={setSelectedIndustry}
          selectedRegion={selectedRegion}
          setSelectedRegion={setSelectedRegion}
          selectedQuarter={selectedQuarter}
          setSelectedQuarter={setSelectedQuarter}
          recommendations={recommendations}
          selectedCodes={selectedCodes}
          toggleDistrict={toggleDistrict}
          clearDistricts={useCompareStore.getState().clearDistricts}
          onOpenCompare={() => navigate("/compare")}
        />
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
                      onMouseEnter={() =>
                        setActiveItemCode(item.trade_area_code)
                      }
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
                          onClick={() =>
                            handleDistrictClick(item.trade_area_code)
                          }
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
                            <ScorePill
                              score={item.score}
                              isSelected={isTopActive}
                            />
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
                            onClick={() =>
                              handleDistrictClick(item.trade_area_code)
                            }
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
                <h3 className="text-lg sm:text-xl font-black text-black">
                  추천 기준
                </h3>
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
                  <span className="text-black font-medium">
                    Transaction Volume
                  </span>
                  <span className="font-extrabold text-black">35%</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-black font-medium">
                    Competition Intensity
                  </span>
                  <span className="font-extrabold text-black">25%</span>
                </div>
              </div>

              {/* Dashed line */}
              <div className="border-t border-dashed border-black/40 pt-2 text-xs text-gray-600 leading-relaxed">
                <p>
                  * 경쟁 강도는 역산(Inverse) 반영되어, 과밀 출점 상권은 감점
                  처리됩니다.
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
                본 점수는 성공 예측이 아닌 탐색을 위한 발견 지수(Discovery
                Index)입니다. 실제 창업 시에는 추가적인 현장 조사가 필요합니다.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
