import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
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
import { useCompareStore, useExploreStore } from "../../shared/lib/store";
import type {
  District,
  Industry,
  QuarterOption,
  RecommendationItem,
  TradeArea,
} from "../../shared/types";

interface ExploreFilterBarProps {
  industries: Industry[];
  quarters: QuarterOption[];
  industryStatus: string;
  quarterStatus: string;
  selectedIndustry: string;
  setSelectedIndustry: (value: string) => void;
  districts: District[];
  selectedDistrictCode: string;
  setDistrict: (code: string) => void;
  isDistrictsPending: boolean;
  isDistrictsError: boolean;
  keyword: string;
  setKeyword: (keyword: string) => void;
  searchKeyword: string;
  tradeAreas: TradeArea[];
  isTradeAreasFetching: boolean;
  isTradeAreasError: boolean;
  refetchTradeAreas: () => void;
  onSearch: () => void;
  onSubmitSearch: () => void;
  selectedQuarter: string;
  setSelectedQuarter: (value: string) => void;
  recommendations: RecommendationItem[];
  selectedCodes: string[];
  toggleDistrict: (code: string, name?: string) => void;
  clearDistricts: () => void;
  onOpenCompare: () => void;
}

const ExploreFilterBar: React.FC<ExploreFilterBarProps> = ({
  industries,
  quarters,
  industryStatus,
  quarterStatus,
  selectedIndustry,
  setSelectedIndustry,
  districts,
  selectedDistrictCode,
  setDistrict,
  isDistrictsPending,
  isDistrictsError,
  keyword,
  setKeyword,
  searchKeyword,
  tradeAreas,
  isTradeAreasFetching,
  isTradeAreasError,
  refetchTradeAreas,
  onSearch,
  onSubmitSearch,
  selectedQuarter,
  setSelectedQuarter,
  recommendations,
  selectedCodes,
  toggleDistrict,
  clearDistricts,
  onOpenCompare,
}) => {
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);
  const areaNamesByCode = useCompareStore((state) => state.areaNamesByCode);

  const selectedDistricts = selectedCodes.map((code) => {
    const recommendation = recommendations.find(
      (item) => item.trade_area_code === code,
    );

    return {
      trade_area_code: code,
      trade_area_name:
        areaNamesByCode[code] ?? recommendation?.trade_area_name ?? code,
    };
  });
  const candidateRecommendations = recommendations
    .filter((district) => !selectedCodes.includes(district.trade_area_code))
    .slice(0, 6);

  return (
    <div className="border border-black bg-white shadow-[0_10px_14px_-8px_rgba(0,0,0,0.5)]">
      <div className="grid grid-cols-1 md:grid-cols-[repeat(4,minmax(0,1fr))_88px] lg:grid-cols-[repeat(4,minmax(0,1fr))_104px] divide-y md:divide-y-0 md:divide-x divide-black border-b border-black bg-white">
        {[
          {
            label: "업종 카테고리",
            tag: "INDUSTRY",
            value: selectedIndustry,
            options: industries.length
              ? industries.map((industry) => ({
                  value: industry.code,
                  label: industry.name,
                }))
              : [{ value: "", label: industryStatus }],
            onChange: setSelectedIndustry,
            disabled: industries.length === 0,
          },
          {
            label: "분석 지역",
            tag: "REGION",
            value: selectedDistrictCode,
            options: [
              {
                value: "",
                label: isDistrictsPending
                  ? "자치구를 불러오는 중입니다"
                  : isDistrictsError
                    ? "지역 조회 실패"
                    : "서울 전체",
              },
              ...districts.map((district) => ({
                value: district.signgu_cd,
                label: district.signgu_cd_nm,
              })),
            ],
            onChange: setDistrict,
            disabled:
              isDistrictsPending || isDistrictsError || districts.length === 0,
          },
          {
            label: "기준 분기",
            tag: "TIMELINE",
            value: selectedQuarter,
            options: quarters.length
              ? quarters.map((quarter, index) => ({
                  value: quarter.code,
                  label:
                    index === 0
                      ? `${quarter.value} (최신 집계)`
                      : quarter.value,
                }))
              : [{ value: "", label: quarterStatus }],
            onChange: setSelectedQuarter,
            disabled: quarters.length === 0,
          },
        ].map((item) => (
          <React.Fragment key={item.tag}>
            <div className="p-3.5 flex flex-col justify-center gap-1 hover:bg-gray-50 transition-colors relative">
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
                  disabled={item.disabled}
                  className="w-full appearance-none bg-transparent font-bold text-sm text-black cursor-pointer focus:outline-none pr-6 disabled:cursor-not-allowed disabled:opacity-50"
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
            {item.tag === "TIMELINE" && (
              <div
                className="p-3.5 flex flex-col justify-center gap-1 hover:bg-gray-50 transition-colors relative"
                onBlur={(event) => {
                  if (!event.currentTarget.contains(event.relatedTarget))
                    setIsSearchOpen(false);
                }}
                onKeyDown={(event) => {
                  if (event.key === "Escape") setIsSearchOpen(false);
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono font-bold text-gray-500 uppercase tracking-wider">
                    상권 검색
                  </span>
                  <span className="text-[9px] font-mono px-1.5 py-0.2 bg-gray-200 text-gray-800 rounded-none">
                    SEARCH
                  </span>
                </div>

                <div className="relative mt-0.5">
                  <label htmlFor="trade-area-keyword" className="sr-only">
                    상권 검색
                  </label>
                  <input
                    ref={searchInputRef}
                    id="trade-area-keyword"
                    type="search"
                    value={keyword}
                    onChange={(event) => {
                      setKeyword(event.target.value);
                      setIsSearchOpen(true);
                      onSearch();
                    }}
                    onFocus={() => {
                      setIsSearchOpen(true);
                      onSearch();
                    }}
                    onKeyDown={(event) => {
                      if (event.key === "Enter") {
                        setIsSearchOpen(false);
                        onSubmitSearch();
                      }
                    }}
                    placeholder="상권 검색"
                    className="w-full rounded-none border-0 border-b border-black bg-transparent pb-1 pr-6 text-sm font-bold text-black placeholder:text-black focus:outline-none focus:border-b-2"
                  />
                  <button
                    type="button"
                    onClick={() => {
                      setIsSearchOpen((open) => !open);
                      onSearch();
                    }}
                    aria-label="상권 검색 목록"
                    aria-expanded={isSearchOpen}
                    className="absolute right-0 top-0 text-xs text-gray-600 font-bold cursor-pointer"
                  >
                    ▼
                  </button>
                </div>

                {isSearchOpen && (
                  <div
                    className="absolute left-0 right-0 top-full z-20 text-sm shadow-sm"
                    aria-live="polite"
                  >
                    {isTradeAreasFetching ? (
                      <p className="border border-black bg-white p-3">
                        상권을 불러오는 중입니다.
                      </p>
                    ) : isTradeAreasError ? (
                      <div className="border border-black bg-white p-3">
                        <p>상권 목록을 불러오지 못했습니다.</p>
                        <button
                          type="button"
                          onClick={() => refetchTradeAreas()}
                          className="mt-1 underline"
                        >
                          다시 시도
                        </button>
                      </div>
                    ) : (
                      <TradeAreaResults
                        key={JSON.stringify([
                          selectedDistrictCode,
                          searchKeyword,
                        ])}
                        areas={tradeAreas}
                        onSelect={(area) => {
                          setKeyword(area.name);
                          setIsSearchOpen(false);
                        }}
                      />
                    )}
                  </div>
                )}
              </div>
            )}
          </React.Fragment>
        ))}
        <button
          type="button"
          onClick={() => {
            setIsSearchOpen(false);
            onSubmitSearch();
          }}
          className="flex items-center justify-center self-stretch bg-black px-4 py-4 text-lg font-bold text-white hover:bg-black/85 focus-visible:outline-2 focus-visible:outline-offset-[-4px] focus-visible:outline-[#CCFF00] cursor-pointer"
        >
          검색
        </button>
      </div>

      <div className="p-4 bg-[#f2f2ee] flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 mr-2">
              <span className="w-1.5 h-1.5 bg-black inline-block" />
              <span className="text-xs font-black text-black tracking-tight">
                비교 상권 트레이
              </span>
              <span className="font-mono text-[11px] font-bold bg-black text-[#d8fc03] px-1.5 py-0.5">
                {selectedDistricts.length} / 7
              </span>
            </div>
            {selectedDistricts.length === 0 ? (
              <span className="text-xs text-gray-500 italic py-1">
                검색 결과의 '비교 담기' 또는 상권 카드의 '비교' 버튼을
                눌러주세요.
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
            <span>상권 나란히 비교</span>
            <span className="text-xs">➔</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export const ExplorePage: React.FC = () => {
  const navigate = useNavigate();
  const filterBarRef = useRef<HTMLDivElement>(null);
  const [filterBarHeight, setFilterBarHeight] = useState(0);
  const selectedDistrictCode = useExploreStore(
    (state) => state.selectedDistrictCode,
  );

  const setDistrict = useExploreStore((state) => state.setDistrict);

  const keyword = useExploreStore((state) => state.keyword);
  const setKeyword = useExploreStore((state) => state.setKeyword);

  const searchKeyword = keyword.trim();
  const [submittedKeyword, setSubmittedKeyword] = useState("");

  // 업종 카테고리/기준 분기는 Zustand store(useExploreStore)에 보관해서, 비교 화면으로 넘어갔다
  // 돌아와도 직전 조회 조건이 유지된다. 최초 진입 시에는 store 값이 빈 문자열이라 아래 fallback
  // 로직(CS100010/최신 분기)이 적용되고, 그 결과는 아래 useEffect로 다시 store에 기록된다.
  const industryChoice = useExploreStore((state) => state.industryCode);
  const setSelectedIndustry = useExploreStore((state) => state.setIndustry);
  const quarterChoice = useExploreStore((state) => state.quarterCode);
  const setSelectedQuarter = useExploreStore((state) => state.setQuarter);

  const {
    data: districts = [],
    isPending: isDistrictsPending,
    isError: isDistrictsError,
  } = useQuery({
    queryKey: ["districts"],
    queryFn: () => api.getDistricts(),
  });

  const {
    data: industries = [],
    isPending: industriesPending,
    isError: industriesError,
  } = useQuery({
    queryKey: ["industries"],
    queryFn: api.getIndustries,
  });
  const {
    data: quarterData = [],
    isPending: quartersPending,
    isError: quartersError,
  } = useQuery({
    queryKey: ["quarters"],
    queryFn: api.getQuarters,
  });
  const selectedIndustry = industries.some(
    (item) => item.code === industryChoice,
  )
    ? industryChoice
    : ((industries.find((item) => item.code === "CS100010") ?? industries[0])
        ?.code ?? "");
  const selectedQuarter = quarterData.some(
    (item) => item.code === quarterChoice,
  )
    ? quarterChoice
    : (quarterData[0]?.code ?? "");

  const selectedCodes = useCompareStore((state) => state.selectedCodes);
  const clearCompareDistricts = useCompareStore(
    (state) => state.clearDistricts,
  );
  const [pendingCompareReset, setPendingCompareReset] = useState<{
    filter: "industry" | "quarter";
    value: string;
  } | null>(null);

  const requestFilterChange = (
    filter: "industry" | "quarter",
    value: string,
    currentValue: string,
  ) => {
    if (value === currentValue) return;

    if (selectedCodes.length > 0) {
      setPendingCompareReset({ filter, value });
      return;
    }

    if (filter === "industry") {
      setSelectedIndustry(value);
    } else {
      setSelectedQuarter(value);
    }
  };

  const handleIndustryChange = (code: string) => {
    requestFilterChange("industry", code, selectedIndustry);
  };

  const handleQuarterChange = (code: string) => {
    requestFilterChange("quarter", code, selectedQuarter);
  };

  const confirmCompareReset = () => {
    if (!pendingCompareReset) return;

    clearCompareDistricts();
    if (pendingCompareReset.filter === "industry") {
      setSelectedIndustry(pendingCompareReset.value);
    } else {
      setSelectedQuarter(pendingCompareReset.value);
    }
    setPendingCompareReset(null);
  };

  const cancelCompareReset = () => {
    setPendingCompareReset(null);
  };

  // store(industryChoice/quarterChoice)가 비어있어 기본값(CS100010/최신 분기)으로 대체된
  // 경우에도, 실제로 조회에 쓰인 값을 store에 반영해둔다. ComparePage는 이 store 값을 그대로
  // 신뢰해서 조회하므로, 사용자가 필터를 한 번도 건드리지 않고 바로 비교로 넘어가도 방금 화면에
  // 보이던 것과 동일한 업종/분기로 비교된다.
  useEffect(() => {
    if (selectedIndustry && selectedIndustry !== industryChoice) {
      setSelectedIndustry(selectedIndustry);
    }
  }, [selectedIndustry, industryChoice, setSelectedIndustry]);

  useEffect(() => {
    if (selectedQuarter && selectedQuarter !== quarterChoice) {
      setSelectedQuarter(selectedQuarter);
    }
  }, [selectedQuarter, quarterChoice, setSelectedQuarter]);

  const selectedRegion =
    districts.find((item) => item.signgu_cd === selectedDistrictCode)
      ?.signgu_cd_nm ?? "서울 전체";
  const [activeItemCode, setActiveItemCode] = useState<string>("");

  const {
    data: allTradeAreas = [],
    isFetching: isTradeAreasFetching,
    isError: isTradeAreasError,
    refetch: refetchTradeAreas,
  } = useQuery({
    queryKey: [
      "trade-areas",
      selectedIndustry,
      selectedDistrictCode,
      selectedQuarter,
    ],
    queryFn: ({ signal }) =>
      selectedDistrictCode
        ? api.searchTradeAreas(
            {
              industry_code: selectedIndustry,
              signgu_cd: selectedDistrictCode,
              quarter: selectedQuarter,
            },
            signal,
          )
        : api.getTradeAreas(signal),
    enabled: Boolean(selectedIndustry && selectedQuarter),
    staleTime: Infinity,
    retry: false,
  });
  const tradeAreas = allTradeAreas.filter((area) =>
    area.name.toLowerCase().includes(searchKeyword.toLowerCase()),
  );
  const loadTradeAreas = () => {
    if (
      selectedIndustry &&
      selectedQuarter &&
      isTradeAreasError &&
      !isTradeAreasFetching
    ) {
      void refetchTradeAreas();
    }
  };

  const { isDistrictSelected, toggleDistrict } = useCompareStore();

  const {
    data: recommendations = [],
    isLoading,
    isError: recommendationsError,
    refetch: refetchRecommendations,
  } = useQuery({
    queryKey: [
      "recommendations",
      selectedIndustry,
      selectedQuarter,
      selectedRegion,
      submittedKeyword,
    ],
    enabled: Boolean(selectedIndustry && selectedQuarter),
    queryFn: () =>
      api.getRecommendations({
        industry_code: selectedIndustry,
        quarter: selectedQuarter,
        region: selectedRegion,
        keyword: submittedKeyword || undefined,
      }),
  });

  const currentIndustryName =
    industries.find((i) => i.code === selectedIndustry)?.name || "업종 선택";
  const selectedRecommendations = selectedCodes
    .map((code) =>
      recommendations.find((item) => item.trade_area_code === code),
    )
    .filter((item): item is RecommendationItem => item !== undefined);
  const orderedRecommendations = [
    ...selectedRecommendations,
    ...recommendations.filter(
      (item) => !selectedCodes.includes(item.trade_area_code),
    ),
  ];

  const handleDistrictClick = (code: string) => {
    navigate(
      `/district/${code}?industry=${selectedIndustry}&quarter=${encodeURIComponent(selectedQuarter)}`,
    );
  };

  useLayoutEffect(() => {
    const filterBar = filterBarRef.current;
    if (!filterBar) return;

    const updateFilterBarHeight = () => {
      setFilterBarHeight(Math.ceil(filterBar.getBoundingClientRect().height));
    };

    updateFilterBarHeight();
    const resizeObserver = new ResizeObserver(updateFilterBarHeight);
    resizeObserver.observe(filterBar);

    return () => resizeObserver.disconnect();
  }, []);

  return (
    <div className="w-full bg-[#f5f5f0] min-h-[calc(100vh-4rem)]">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12">
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
      </section>

      <div
        ref={filterBarRef}
        className="sticky top-16 z-30 mt-6 bg-[#f5f5f0] sm:mt-8"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <ExploreFilterBar
            industries={industries}
            quarters={quarterData}
            industryStatus={
              industriesPending
                ? "업종 불러오는 중"
                : industriesError
                  ? "업종 조회 실패"
                  : "등록된 업종 없음"
            }
            quarterStatus={
              quartersPending
                ? "분기 불러오는 중"
                : quartersError
                  ? "분기 조회 실패"
                  : "등록된 분기 없음"
            }
            selectedIndustry={selectedIndustry}
            setSelectedIndustry={handleIndustryChange}
            districts={districts}
            selectedDistrictCode={selectedDistrictCode}
            setDistrict={setDistrict}
            isDistrictsPending={isDistrictsPending}
            isDistrictsError={isDistrictsError}
            keyword={keyword}
            setKeyword={setKeyword}
            searchKeyword={searchKeyword}
            tradeAreas={tradeAreas}
            isTradeAreasFetching={isTradeAreasFetching}
            isTradeAreasError={isTradeAreasError}
            refetchTradeAreas={refetchTradeAreas}
            onSearch={loadTradeAreas}
            onSubmitSearch={() => {
              if (
                searchKeyword === submittedKeyword &&
                selectedIndustry &&
                selectedQuarter
              ) {
                void refetchRecommendations();
              } else {
                setSubmittedKeyword(searchKeyword);
              }
            }}
            selectedQuarter={selectedQuarter}
            setSelectedQuarter={handleQuarterChange}
            recommendations={recommendations}
            selectedCodes={selectedCodes}
            toggleDistrict={toggleDistrict}
            clearDistricts={useCompareStore.getState().clearDistricts}
            onOpenCompare={() => navigate("/compare")}
          />
        </div>
      </div>

      <div className="h-8" />

      {/* Main Swiss Grid Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[600px] border-y-2 border-black">
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
              ) : recommendationsError ? (
                <p className="p-12 text-center">
                  상권 조회에 실패했습니다. 잠시 후 다시 시도해 주세요.
                </p>
              ) : orderedRecommendations.length === 0 ? (
                <p className="p-12 text-center">
                  조회 조건에 맞는 상권이 없습니다.
                </p>
              ) : (
                orderedRecommendations.map((item) => {
                  const isTopActive = activeItemCode === item.trade_area_code;
                  const isChecked = isDistrictSelected(item.trade_area_code);

                  return (
                    <div
                      key={item.trade_area_code}
                      onMouseEnter={() =>
                        setActiveItemCode(item.trade_area_code)
                      }
                      className={`relative p-5 sm:p-6 transition-colors duration-150 group cursor-pointer ${
                        isChecked
                          ? "bg-[#CCFF00]"
                          : isTopActive
                            ? "bg-[#e5e5df]"
                            : "bg-[#f5f5f0] hover:bg-[#e5e5df]"
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
                              toggleDistrict(
                                item.trade_area_code,
                                item.trade_area_name,
                              );
                            }}
                            title="비교함에 추가/제외"
                            className="flex h-[38px] items-center gap-2 px-3 text-sm font-mono font-bold border border-black bg-white hover:bg-black hover:text-white transition-colors"
                          >
                            {isChecked ? (
                              <CheckSquare className="w-[18px] h-[18px] text-black" />
                            ) : (
                              <Square className="w-[18px] h-[18px] text-gray-500" />
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
          <div
            className="lg:col-span-4 lg:sticky lg:self-start bg-[#f5f5f0] flex flex-col justify-between p-6 sm:p-8 space-y-8"
            style={{ top: `calc(4rem + ${filterBarHeight}px)` }}
          >
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
                  <span className="text-black font-medium">
                    매출 성장 (Sales Growth)
                  </span>
                  <span className="font-extrabold text-black">40%</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-black font-medium">
                    거래량 (Transaction Volume)
                  </span>
                  <span className="font-extrabold text-black">35%</span>
                </div>
                <div className="flex justify-between py-3">
                  <span className="text-black font-medium">
                    경쟁 여건 (Competition Intensity)
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

      {pendingCompareReset && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
          role="dialog"
          aria-modal="true"
          aria-labelledby="compare-reset-title"
          aria-describedby="compare-reset-description"
        >
          <div className="w-full max-w-lg border-2 border-black bg-[#f5f5f0] p-6 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
            <div className="flex items-center gap-2 border-b border-black pb-3">
              <Info className="h-5 w-5 shrink-0" aria-hidden="true" />
              <h2 id="compare-reset-title" className="text-lg font-extrabold">
                비교 조건 변경 안내
              </h2>
            </div>

            <p
              id="compare-reset-description"
              className="py-5 text-sm font-medium leading-relaxed text-gray-800"
            >
              비교 상권 트레이의 상권은 동일 업종, 기준 분기만 담을 수 있습니다.
              업종 또는 분기가 변경되면 비교 상권 트레이는 초기화 됩니다. 초기화
              하시겠습니까?
            </p>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={cancelCompareReset}
                className="border border-black bg-white py-2.5 text-sm font-bold text-black transition-colors hover:bg-gray-200"
                autoFocus
              >
                아니오
              </button>
              <button
                type="button"
                onClick={confirmCompareReset}
                className="border border-black bg-black py-2.5 text-sm font-bold text-white transition-colors hover:bg-[#d4ff00] hover:text-black"
              >
                예
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

function TradeAreaResults({
  areas,
  onSelect,
}: {
  areas: TradeArea[];
  onSelect: (area: TradeArea) => void;
}) {
  const [visibleCount, setVisibleCount] = useState(20);
  const visibleAreas = areas.slice(0, visibleCount);
  const hasMore = visibleCount < areas.length;

  const showMore = () => {
    setVisibleCount((count) => Math.min(count + 20, areas.length));
  };

  return (
    <div className="border border-gray-300 bg-white">
      <p className="mb-0 border-b border-gray-300 bg-white py-3 pl-3.5 pr-3 text-left">
        전체 {areas.length}개 중 {visibleAreas.length}개 표시
      </p>

      <div
        className="max-h-80 overflow-y-auto bg-white"
        onScroll={(event) => {
          const element = event.currentTarget;
          const nearBottom =
            element.scrollTop + element.clientHeight >=
            element.scrollHeight - 40;

          if (nearBottom && hasMore) {
            showMore();
          }
        }}
      >
        {areas.length === 0 ? (
          <p className="p-3">일치하는 상권이 없습니다.</p>
        ) : (
          <ul aria-label="상권 검색 결과">
            {visibleAreas.map((area) => {
              return (
                <li
                  key={area.code}
                  className="border-b border-gray-300 last:border-b-0"
                >
                  <button
                    type="button"
                    onClick={() => onSelect(area)}
                    className="flex w-full items-center justify-between gap-3 bg-white p-3 text-left focus:outline-2 focus:outline-black hover:bg-[#F8F7F2]"
                  >
                    <span>
                      <span className="font-bold">{area.name}</span>
                      <span className="ml-2 text-gray-600">
                        {area.district_name ?? "자치구 정보 없음"}
                      </span>
                    </span>

                    <span className="shrink-0 text-xs font-bold">선택</span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}

        {hasMore && (
          <button
            type="button"
            onClick={showMore}
            className="w-full border-t border-gray-300 p-3 font-bold hover:bg-[#CCFF00]"
          >
            결과 더 보기
          </button>
        )}
      </div>
    </div>
  );
}
