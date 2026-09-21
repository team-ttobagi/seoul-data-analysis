import React, { useEffect, useRef, useState } from "react";
import {
  useParams,
  useSearchParams,
  Link,
  useNavigate,
} from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  AlertTriangle,
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
  AgeBarChart,
  DayBarChart,
} from "../../shared/ui/Charts";
import {
  useCompareStore,
  useHeaderBreadcrumbStore,
} from "../../shared/lib/store";
import {
  formatNullable,
  formatQuarterLabel,
  formatSignedPercent,
} from "../../shared/lib/format";
import { getApiErrorMessage } from "../../shared/lib/apiError";
import { StatusBlock, StatusInline } from "../../shared/ui/QueryState";
import { useIsFreshDirectEntry } from "../../shared/lib/navigationOrigin";

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
  const quarter = searchParams.get("quarter") || "20254";

  const [rankTab, setRankTab] = useState<
    "sales" | "volume" | "growth" | "score"
  >("sales");

  const { isDistrictSelected, toggleDistrict } = useCompareStore();
  const isChecked = isDistrictSelected(tradeAreaCode);

  // [연동] 주소창에 완성된 URL(예: /district/3120088?industry=...&quarter=...)을 직접 입력하거나
  // 새로고침/북마크로 곧바로 들어온 경우(이 세션에서 앱 내부 이동이 한 번도 없었던 POP)엔, 상세
  // 데이터를 조회하지 않고 Explore로 즉시 돌려보낸다. Explore/Compare 등 앱 내부에서 이동해온
  // 경우(PUSH/REPLACE)나 그런 이동 이후의 브라우저 뒤로가기(POP)는 리다이렉트하지 않는다.
  const shouldRedirectToExplore = useIsFreshDirectEntry();

  useEffect(() => {
    if (shouldRedirectToExplore) {
      navigate("/explore", { replace: true });
    }
  }, [shouldRedirectToExplore, navigate]);

  const {
    data: overview,
    isLoading: isOverviewLoading,
    isError: isOverviewError,
    error: overviewError,
    refetch: refetchOverview,
  } = useQuery({
    queryKey: ["district-overview", tradeAreaCode, industryCode, quarter],
    queryFn: () =>
      api.getDistrictOverview(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
    enabled: !shouldRedirectToExplore,
  });

  // [연동] Gemini 인사이트는 별도 /overview/insight 호출로 받아온다(최대 수 초 소요, 나머지 화면을 막지 않음).
  // 응답 전까지는 overview.takeaway.summary 의 고정 문구("AI 인사이트 생성 중입니다.")를 그대로 보여준다.
  const { data: overviewInsight } = useQuery({
    queryKey: [
      "district-overview-insight",
      tradeAreaCode,
      industryCode,
      quarter,
    ],
    queryFn: () =>
      api.getDistrictOverviewInsight(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
    enabled: !shouldRedirectToExplore,
  });

  const {
    data: patterns,
    isLoading: isPatternsLoading,
    isError: isPatternsError,
    error: patternsError,
  } = useQuery({
    queryKey: ["district-patterns", tradeAreaCode, industryCode, quarter],
    queryFn: () =>
      api.getDistrictPatterns(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
    enabled: !shouldRedirectToExplore,
  });

  const {
    data: competition,
    isLoading: isCompLoading,
    isError: isCompError,
    error: competitionError,
  } = useQuery({
    queryKey: ["district-competition", tradeAreaCode, industryCode, quarter],
    queryFn: () =>
      api.getDistrictCompetition(tradeAreaCode, {
        industry_code: industryCode,
        quarter,
      }),
    enabled: !shouldRedirectToExplore,
  });

  const { data: tradeAreas = [] } = useQuery({
    queryKey: ["trade-areas"],
    queryFn: ({ signal }) => api.getTradeAreas(signal),
  });

  // 브레드크럼("서울 > OO > 업종 | 분기")이 스크롤로 헤더 밑에 가리면 헤더에 같은 내용을
  // 노출하고, 다시 보이면 숨긴다. IntersectionObserver로 브레드크럼 자체의 노출 여부를
  // 감지해 Header가 구독하는 전역 상태(useHeaderBreadcrumbStore)에 반영한다.
  const breadcrumbRef = useRef<HTMLDivElement>(null);
  const setHeaderBreadcrumb = useHeaderBreadcrumbStore((s) => s.setBreadcrumb);
  const setHeaderBreadcrumbVisible = useHeaderBreadcrumbStore(
    (s) => s.setVisible,
  );

  useEffect(() => {
    if (!overview) return;

    setHeaderBreadcrumb({
      pathLabel: `서울 > ${overview.trade_area_name} > ${overview.industry_name}`,
      quarterLabel: formatQuarterLabel(overview.quarter),
    });

    const el = breadcrumbRef.current;
    if (!el) return;

    // 헤더(h-16 = 64px) 밑으로 가리는 순간을 감지하도록 그만큼 rootMargin을 당겨준다.
    const observer = new IntersectionObserver(
      ([entry]) => setHeaderBreadcrumbVisible(!entry.isIntersecting),
      { rootMargin: "-64px 0px 0px 0px" },
    );
    observer.observe(el);

    return () => {
      observer.disconnect();
      setHeaderBreadcrumb(null);
      setHeaderBreadcrumbVisible(false);
    };
  }, [overview, setHeaderBreadcrumb, setHeaderBreadcrumbVisible]);

  // Explore로 리다이렉트되는 동안 로딩/상세 화면이 잠깐 보이지 않도록 아무것도 그리지 않는다.
  if (shouldRedirectToExplore) {
    return null;
  }

  // [연동] overview 는 데이터가 없으면 404 SALES_DATA_NOT_FOUND 를 내려주는 실제 에러 상태다
  // (patterns/competition 처럼 200 + 빈 배열/null 로 내려오지 않음). loading/error/empty 를
  // 명확히 구분해서, 에러가 정상 데이터 화면으로 오인되지 않게 한다.
  if (isOverviewLoading) {
    return (
      <div className="max-w-7xl mx-auto p-12">
        <StatusBlock
          kind="loading"
          title="상권 데이터를 불러오는 중입니다..."
        />
      </div>
    );
  }

  if (isOverviewError) {
    return (
      <div className="max-w-7xl mx-auto p-12">
        <StatusBlock
          kind="error"
          title="상권 데이터를 불러오지 못했습니다."
          description={getApiErrorMessage(overviewError)}
          action={
            <button
              onClick={() => refetchOverview()}
              className="px-4 py-2 bg-black text-white font-bold font-mono text-sm hover:bg-red-600 transition-colors"
            >
              다시 시도
            </button>
          }
        />
      </div>
    );
  }

  if (!overview) {
    return (
      <div className="max-w-7xl mx-auto p-12">
        <StatusBlock kind="empty" title="표시할 상권 데이터가 없습니다." />
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
    <div
      className="w-full bg-[#f5f5f0] min-h-[calc(100vh-4rem)] pb-12"
      onClickCapture={(e) => {
        if ((e.target as HTMLElement).closest("button")) {
          console.log("sales_percentile:", overview.kpis.sales_percentile);
        }
      }}
    >
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
                    {ta.name} ({ta.district_name ?? "자치구 정보 없음"})
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

          <div
            ref={breadcrumbRef}
            className="flex items-center gap-2 text-xs sm:text-sm font-mono text-gray-700 pt-1"
          >
            <span className="font-bold text-black">
              서울 &gt; {overview.trade_area_name} &gt; {overview.industry_name}
            </span>
            <span>|</span>
            <span>{formatQuarterLabel(overview.quarter)}</span>
          </div>
        </div>
      </section>

      {/* AI Insight Section — 추정 매출 KPI 라인 위로 이동, 경쟁은 어떨까? 를 오른쪽에 함께 배치 */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 border-2 border-black bg-[#121212] text-white">
          {/* Left Dark Card: OVERALL INSIGHT & Score (~62%) */}
          <div className="lg:col-span-7 p-6 sm:p-8 border-b-2 lg:border-b-0 lg:border-r-2 border-black flex flex-col justify-between space-y-6">
            <div>
              <span className="text-xs font-mono font-bold tracking-widest text-gray-400 uppercase">
                OVERALL INSIGHT
              </span>

              {/* Giant Score */}
              {/* [연동] score 는 성장률/거래량/경쟁 구성 지표 부족 시 null → "-" 폴백, score_note 로 사유 안내 */}
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-5xl sm:text-7xl font-black text-gray-500 tracking-tighter">
                  SCORE{" "}
                  <span className="text-white">
                    {formatNullable(overview.takeaway.score)}
                  </span>
                </span>
                <span className="text-xl sm:text-2xl font-mono text-gray-500 font-bold">
                  /100
                </span>
              </div>
              {overview.takeaway.score == null &&
                overview.takeaway.score_note && (
                  <p className="text-xs font-mono text-gray-500 mt-1">
                    {overview.takeaway.score_note}
                  </p>
                )}

              {/* Signal Badges matching Reference 2 */}
              <div className="flex flex-wrap items-center gap-2 mt-4 font-mono text-xs">
                <span className="bg-[#d4ff00] text-black px-2.5 py-1 font-bold">
                  {overview.takeaway.growth_tag}
                </span>
                <span className="bg-[#d4ff00] text-black px-2.5 py-1 font-bold">
                  {overview.takeaway.volume_tag}
                </span>
                <span
                  className={`border px-2.5 py-1 font-bold ${
                    overview.takeaway.competition_tag === "경쟁 여건 좋음"
                      ? "border-[#4ade80] text-[#4ade80]"
                      : overview.takeaway.competition_tag === "경쟁 여건 보통"
                        ? "border-white text-white"
                        : "border-red-500 text-red-400"
                  }`}
                >
                  {overview.takeaway.competition_tag}
                </span>
              </div>
            </div>

            {/* Quote Conclusion matching Reference 2 */}
            {/* [연동] overviewInsight(/overview/insight) 가 도착하면 실제 AI 인사이트 문장으로 교체하고,
                source가 gemini일 때만 "AI INSIGHT" 라벨을 단다. 도착 전에는 overview.takeaway.summary
                의 고정 문구("AI 인사이트 생성 중입니다.")를 그대로 보여준다. */}
            <div className="border-l-4 border-[#d4ff00] pl-4 py-2">
              {overviewInsight?.source === "gemini" && (
                <span className="block text-[10px] font-mono font-bold tracking-widest text-[#d4ff00] uppercase mb-1">
                  AI INSIGHT
                </span>
              )}
              <p className="text-base sm:text-xl font-bold text-white leading-snug">
                "{overviewInsight?.summary ?? overview.takeaway.summary}"
              </p>
            </div>

            {/* Disclaimer note */}
            <p className="text-[11px] font-mono text-gray-500">
              * {overview.takeaway.disclaimer}
            </p>
          </div>

          {/* Right Dark Card: 경쟁은 어떨까? (주의할 점) (~38%) */}
          <div className="lg:col-span-5 p-6 sm:p-8 flex flex-col justify-between space-y-6">
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
            {/* [연동] sales_level/volume_level/competition_level 은 경쟁·폐업률 데이터 부족 시
                백엔드가 null 을 내려주는 Optional 필드다. loading("…") / error("오류", 빨간 배지) /
                empty(null → "-") 를 구분해서, API 에러가 정상 "-" 화면으로 오인되지 않게 한다. */}
            <div className="divide-y divide-gray-800 border-t border-b border-gray-800 font-mono text-xs sm:text-sm">
              <div className="flex justify-between items-center py-2.5">
                <span className="text-gray-300">매출 수준</span>
                <span
                  className={`px-2 py-0.5 font-bold text-xs ${
                    isCompError
                      ? "bg-red-600 text-white"
                      : "bg-white text-black"
                  }`}
                >
                  {isCompLoading
                    ? "…"
                    : isCompError
                      ? "오류"
                      : formatNullable(competition?.sales_level)}
                </span>
              </div>

              <div className="flex justify-between items-center py-2.5">
                <span className="text-gray-300">거래량</span>
                <span
                  className={`px-2 py-0.5 font-bold text-xs ${
                    isCompError
                      ? "bg-red-600 text-white"
                      : "bg-white text-black"
                  }`}
                >
                  {isCompLoading
                    ? "…"
                    : isCompError
                      ? "오류"
                      : formatNullable(competition?.volume_level)}
                </span>
              </div>

              <div className="flex justify-between items-center py-2.5">
                <span className="text-gray-300">경쟁 여건</span>
                <span
                  className={`px-2 py-0.5 font-bold text-xs ${
                    !isCompLoading &&
                    !isCompError &&
                    competition?.competition_level === "좋음"
                      ? "bg-[#4ade80] text-black"
                      : !isCompLoading &&
                          !isCompError &&
                          competition?.competition_level === "보통"
                        ? "bg-white text-black"
                        : "bg-[#ff3b30] text-white"
                  }`}
                >
                  {isCompLoading
                    ? "…"
                    : isCompError
                      ? "오류"
                      : formatNullable(competition?.competition_level)}
                </span>
              </div>
            </div>

            {/* Error note — 경쟁 데이터 자체를 못 불러왔을 때, 아래 warning_text(정상 안내 문구)와
                혼동되지 않도록 별도의 경고 아이콘/문구로 표시한다. */}
            {isCompError && (
              <div className="flex items-center gap-1.5 text-xs text-red-400 font-sans">
                <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
                <span>
                  {getApiErrorMessage(
                    competitionError,
                    "경쟁 데이터를 불러오지 못했습니다.",
                  )}
                </span>
              </div>
            )}

            {/* Warning Interpretation
                [연동] warning_text 는 경쟁 여건이 낮음일 때만 채워지는 Optional 필드라, 로딩/에러 중이거나
                null이면(경고할 내용이 없으면) 가짜 문구를 보여주지 않고 문단 자체를 숨긴다. */}
            {!isCompLoading && !isCompError && competition?.warning_text && (
              <p className="text-xs text-gray-400 leading-relaxed font-sans">
                {competition.warning_text}
              </p>
            )}
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
            {/* [연동] seoul_rank 는 Optional(구성 Percentile 부족 시 null) → "-" 폴백 */}
            <span className="block text-2xl sm:text-3xl font-black text-black mt-2 tracking-tight">
              {formatNullable(overview.kpis.seoul_rank, "위")}
            </span>
          </div>

          {/* KPI 4 - Highlighted in Lime matching Reference 2 */}
          <div className="p-5 sm:p-6 bg-[#d4ff00]">
            <span className="block font-mono text-xs text-black font-bold">
              전분기 대비
            </span>
            {/* [연동] qoq_growth_rate 는 음수 가능(Optional[float]) → formatSignedPercent 가
                null/0/음수를 모두 정확히 구분해 표시한다 */}
            <span className="block text-2xl sm:text-3xl font-black text-black mt-2 tracking-tight">
              {formatSignedPercent(overview.kpis.qoq_growth_rate)}
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
                {formatNullable(overview.kpis.seoul_rank, "위")}
              </span>
              <span className="text-gray-500">
                {rankTab === "sales" &&
                  `상위 ${overview.kpis.sales_percentile}%`}
                {rankTab === "volume" &&
                  `상위 ${overview.kpis.volume_percentile}%`}
                {/* {rankTab === "growth" &&
                  `상위 ${overview.kpis.growth_percentile}%`}
                {rankTab === "score" &&
                  `상위 ${overview.kpis.exploration_percentile}%`} */}
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

            {/* [연동] patterns 는 소스 데이터가 없어도 404 없이 200 + 빈 배열로 내려온다.
                loading / error / empty(slots=[])를 구분해서, 로딩/에러 중에 예시 문구가 정상
                인사이트처럼 보이지 않게 한다. */}
            {isPatternsLoading ? (
              <StatusInline
                kind="loading"
                message="시간대별 데이터를 불러오는 중입니다."
              />
            ) : isPatternsError ? (
              <StatusInline
                kind="error"
                message={getApiErrorMessage(
                  patternsError,
                  "시간대별 데이터를 불러오지 못했습니다.",
                )}
              />
            ) : patterns && patterns.when.slots.length > 0 ? (
              <>
                <div className="my-2">
                  <TimeBarChart
                    slots={patterns.when.slots}
                    peakSlot={patterns.when.peak_slot}
                  />
                </div>
                <div className="border-l-4 border-[#d4ff00] pl-3 py-1 text-xs sm:text-sm font-medium text-black">
                  {patterns.when.insight}
                </div>
              </>
            ) : (
              <StatusInline
                kind="empty"
                message="시간대별 데이터가 없습니다."
              />
            )}
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
            </div>

            {/* [연동] 성별 구분 없이 연령대(primary_age_group)만 표시.
                backend who.gender(female_ratio/male_ratio)는 화면에서 사용하지 않는다.
                patterns 는 소스 데이터가 없어도 404 없이 200 + 빈 배열로 내려오므로
                loading / error / empty(demographics=[])를 구분해서 표시한다. */}
            {isPatternsLoading ? (
              <StatusInline
                kind="loading"
                message="연령대별 데이터를 불러오는 중입니다."
              />
            ) : isPatternsError ? (
              <StatusInline
                kind="error"
                message={getApiErrorMessage(
                  patternsError,
                  "연령대별 데이터를 불러오지 못했습니다.",
                )}
              />
            ) : patterns && patterns.who.demographics.length > 0 ? (
              <>
                <div className="flex items-center gap-3">
                  <span className="text-3xl sm:text-4xl font-black text-black tracking-tight">
                    {patterns.who.primary_age_group}
                  </span>
                  <span className="bg-[#d4ff00] text-black border border-black px-2 py-0.5 text-xs font-mono font-bold">
                    주요 소비 연령대
                    {patterns.who.primary_age_percentage != null
                      ? ` (${patterns.who.primary_age_percentage}%)`
                      : ""}
                  </span>
                </div>

                <div className="my-2">
                  <AgeBarChart demographics={patterns.who.demographics} />
                </div>

                <div className="border-l-4 border-[#d4ff00] pl-3 py-1 text-xs sm:text-sm font-medium text-black">
                  {patterns.who.insight}
                </div>
              </>
            ) : (
              <StatusInline
                kind="empty"
                message="연령대별 데이터가 없습니다."
              />
            )}
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

            {/* [연동] patterns 는 소스 데이터가 없어도 404 없이 200 + 빈 배열로 내려온다.
                loading / error / empty(days=[])를 구분해서 표시한다. */}
            {isPatternsLoading ? (
              <StatusInline
                kind="loading"
                message="요일별 데이터를 불러오는 중입니다."
              />
            ) : isPatternsError ? (
              <StatusInline
                kind="error"
                message={getApiErrorMessage(
                  patternsError,
                  "요일별 데이터를 불러오지 못했습니다.",
                )}
              />
            ) : patterns && patterns.day.days.length > 0 ? (
              <>
                <div className="my-2">
                  <DayBarChart
                    days={patterns.day.days}
                    peakDay={patterns.day.peak_day}
                    peakDiffBadge={patterns.day.peak_diff_badge}
                  />
                </div>
                <div className="border-l-4 border-[#d4ff00] pl-3 py-1 text-xs sm:text-sm font-medium text-black">
                  {patterns.day.insight}
                </div>
              </>
            ) : (
              <StatusInline kind="empty" message="요일별 데이터가 없습니다." />
            )}
          </div>
        </div>
      </section>
    </div>
  );
};
