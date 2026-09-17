import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, Trash2, ArrowUpRight, ExternalLink } from "lucide-react";
import { api } from "../../shared/api/client";
import { useCompareStore, useExploreStore } from "../../shared/lib/store";
import { ScorePill } from "../../shared/ui/Signals";
import { getApiErrorMessage } from "../../shared/lib/apiError";
import { StatusBlock, StatusInline } from "../../shared/ui/QueryState";
import { useIsFreshDirectEntry } from "../../shared/lib/navigationOrigin";

export const ComparePage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedCodes, areaNamesByCode } = useCompareStore();

  // [연동] 주소창 직접 입력/새로고침/북마크로 /compare 에 곧바로 들어온 경우(이 세션에서 앱 내부
  // 이동이 한 번도 없었던 POP)엔, 빈 비교표를 보여주는 대신 상권을 고를 수 있는 Explore로 즉시
  // 돌려보낸다. Explore/Compare 등 앱 내부에서 이동해온 경우(PUSH/REPLACE)나, 그런 이동 이후의
  // 브라우저 뒤로가기(POP)는 리다이렉트하지 않는다.
  const shouldRedirectToExplore = useIsFreshDirectEntry();

  useEffect(() => {
    if (shouldRedirectToExplore) {
      navigate("/explore", { replace: true });
    }
  }, [shouldRedirectToExplore, navigate]);

  // [연동] Explore에서 선택한 업종/분기(useExploreStore)를 그대로 이어받는다 — 이전엔
  // CS100010/20254로 고정돼 있어, Explore에서 다른 업종으로 조회한 상권을 비교표로 넘기면
  // 실제로는 전혀 다른 업종·분기 기준으로 재조회되어 Score 등 지표가 달라 보이는 문제가 있었다.
  // Explore를 거치지 않고 곧바로 /compare 로 들어와 store가 비어있는 경우, 임의의 기본값으로
  // 대체하지 않고 "비교할 상권이 선택되지 않았습니다" 빈 상태로 보여준다.
  const selectedIndustry = useExploreStore((state) => state.industryCode);
  const selectedQuarter = useExploreStore((state) => state.quarterCode);

  // 선택은 최대 7개까지 가능하지만, 비교표에는 선택한 순서대로 최대 3개만 표시한다.
  // 이미 표시 중이던 항목은 selectedCodes 가 바뀌어도(추가/Explore에서 넘어옴 등) 그대로 유지하고,
  // 표시할 게 하나도 없을 때만 선택 순서대로 앞의 3개를 채운다.
  const [displayedCodes, setDisplayedCodes] = useState<string[]>([]);

  useEffect(() => {
    setDisplayedCodes((current) => {
      const stillSelected = current.filter((code) =>
        selectedCodes.includes(code),
      );
      return stillSelected.length > 0
        ? stillSelected.slice(0, 3)
        : selectedCodes.slice(0, 3);
    });
  }, [selectedCodes]);

  const {
    data: compareList = [],
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery({
    queryKey: [
      "compare-data",
      selectedCodes,
      selectedIndustry,
      selectedQuarter,
    ],
    queryFn: () =>
      api.getCompareData({
        trade_area_codes: selectedCodes,
        industry_code: selectedIndustry,
        quarter: selectedQuarter,
      }),
    enabled: selectedCodes.length > 0 && Boolean(selectedIndustry && selectedQuarter),
  });

  // 비교표 컬럼은 데이터 로딩 여부와 무관하게 displayedCodes(최대 3개) 순서로 즉시 그린다.
  // compareList 가 아직 안 왔으면 data 가 undefined 인 채로 컬럼만 먼저 표시하고(Explore→Compare
  // 이동 직후 "비교 지표" 한 칸만 화면을 채우는 현상 방지), 각 셀은 도착하면 실제 값으로 채운다.
  const displayedItems = displayedCodes.map((code) => ({
    code,
    name: areaNamesByCode[code] ?? code,
    data: compareList.find((item) => item.trade_area_code === code),
  }));

  // "상권 추가"에는 선택은 했지만 현재 비교표에는 표시되지 않은 상권만 보여준다
  // (비교표에 보이는 상권은 여기서 제외).
  const hiddenSelectedDistricts = selectedCodes
    .filter((code) => !displayedCodes.includes(code))
    .map((code) => ({
      trade_area_code: code,
      trade_area_name: areaNamesByCode[code] ?? code,
    }));

  const showInComparison = (code: string) => {
    if (displayedCodes.length >= 3) {
      window.alert("비교 지표는 3개까지 비교됩니다.");
      return;
    }
    setDisplayedCodes((current) => [...current, code]);
  };

  // 비교표의 쓰레기통은 선택 자체를 취소하지 않고 표시에서만 숨긴다 — 숨긴 상권은
  // "상권 추가"에 다시 나타나며, 완전히 선택을 취소하려면 "선택 초기화"를 사용한다.
  const hideFromComparison = (code: string) => {
    setDisplayedCodes((current) => current.filter((c) => c !== code));
  };

  // "선택 초기화"는 비교표(표시) 만 초기화하고, "상권 추가"의 선택 정보(selectedCodes)는 유지한다.
  const handleClearDisplayed = () => {
    setDisplayedCodes([]);
  };

  // compareList 가 아직 로딩 중인 컬럼(data undefined)에 표시할 자리표시자.
  const Placeholder = () => <span className="text-gray-300">…</span>;

  // [연동] GET /compare 는 요청한 trade_area_code 중 데이터가 없는 항목을 에러 없이 결과 배열에서
  // 조용히 제외한다. 로딩 중("…")과 "조회는 성공했지만 이 상권 데이터가 없음"을 구분해서 보여준다.
  const NoDataCell = () => (
    <span className="text-gray-400 text-xs">데이터 없음</span>
  );
  const cellFallback = isLoading ? <Placeholder /> : <NoDataCell />;

  // Explore로 리다이렉트되는 동안 빈 비교표 화면이 잠깐 보이지 않도록 아무것도 그리지 않는다.
  if (shouldRedirectToExplore) {
    return null;
  }

  return (
    <div className="w-full bg-[#f5f5f0] min-h-[calc(100vh-4rem)] pb-16">
      {/* Header Bar */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 pb-6 border-b-2 border-black">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <Link
              to="/explore"
              className="inline-flex items-center gap-1.5 font-mono text-xs font-bold text-gray-700 hover:text-black hover:underline mb-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>상권 탐색으로 돌아가기</span>
            </Link>
            <h1 className="text-3xl sm:text-4xl font-black tracking-tight text-black">
              상권 다각 비교 분석
            </h1>
            <p className="text-sm font-mono text-gray-600 mt-1">
              최대 7개 상권의 핵심 지표를 나란히 비교하여 후보지를 압축하세요.
            </p>
          </div>

          {selectedCodes.length > 0 && (
            <button
              onClick={handleClearDisplayed}
              className="px-3 py-1.5 border border-black font-mono text-xs font-bold bg-white hover:bg-black hover:text-white transition-colors flex items-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>선택 초기화</span>
            </button>
          )}
        </div>

        {/* [연동] 비교표에 보이는 상권은 제외하고, 선택은 했지만 표시되지 않은 상권만 보여준다.
            클릭하면 비교표에 표시되고(최대 3개), 3개가 이미 차 있으면 alert 로 안내한다. */}
        <div className="mt-6 flex flex-wrap items-center gap-2">
          <span className="font-mono text-xs font-bold text-gray-700">
            상권 추가 ({selectedCodes.length}/7):
          </span>
          {selectedCodes.length === 0 ? (
            <span className="text-xs text-gray-500 italic py-1">
              Explore에서 비교할 상권을 선택하세요.
            </span>
          ) : hiddenSelectedDistricts.length === 0 ? (
            <span className="text-xs text-gray-500 italic py-1">
              선택한 상권이 모두 비교표에 표시 중입니다.
            </span>
          ) : (
            hiddenSelectedDistricts.map((district) => (
              <button
                key={district.trade_area_code}
                type="button"
                disabled={displayedCodes.length >= 3}
                onClick={() => showInComparison(district.trade_area_code)}
                className="inline-flex items-center gap-2 px-2.5 py-1 bg-white border border-black text-black text-xs font-bold shadow-sm hover:bg-[#d4ff00] transition-colors cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-white"
                title={
                  displayedCodes.length >= 3
                    ? "비교 지표는 3개까지 비교됩니다."
                    : `${district.trade_area_name} 비교표에 표시`
                }
              >
                <span className="w-1.5 h-1.5 inline-block border border-black bg-black" />
                <span>{district.trade_area_name}</span>
                <span className="text-gray-500">보기</span>
              </button>
            ))
          )}
        </div>
      </section>

      {/* Comparison Table / Matrix */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        {/* 비교표에 표시 중인 상권이 0개면(전체 미선택 포함) 빈 상태 화면을 보여준다.
            선택은 남아있지만 전부 숨겨진 경우에도 동일하게 이 화면을 보여주고,
            "상권 추가"의 "보기" 버튼으로 다시 표시할 수 있다. Explore를 거치지 않고 곧바로
            /compare 로 들어와 업종/분기(selectedIndustry/selectedQuarter)가 비어있는 경우도
            같은 빈 상태로 처리한다. */}
        {displayedCodes.length === 0 || !selectedIndustry || !selectedQuarter ? (
          <StatusBlock
            kind="empty"
            title="비교할 상권이 선택되지 않았습니다."
            action={
              <Link
                to="/explore"
                className="inline-block px-4 py-2 bg-[#d4ff00] text-black border border-black font-bold font-mono text-sm hover:bg-black hover:text-white transition-colors"
              >
                탐색 목록에서 상권 담기
              </Link>
            }
          />
        ) : isError ? (
          // [연동] compareList 조회 자체가 실패한 경우(네트워크/타임아웃/5xx 등) 표를 그리지 않고
          // 에러 화면으로 명확히 대체한다 — 정상 데이터 화면(검은 테두리 표)과 절대 혼동되지 않도록
          // 빨간 테두리로 구분한다.
          <StatusBlock
            kind="error"
            title="비교 데이터를 불러오지 못했습니다."
            description={getApiErrorMessage(error)}
            action={
              <button
                onClick={() => refetch()}
                className="px-4 py-2 bg-black text-white font-bold font-mono text-sm hover:bg-red-600 transition-colors"
              >
                다시 시도
              </button>
            }
          />
        ) : (
          <>
            {/* [연동] compareList 조회(useQuery)의 isLoading 동안 표 위에 로딩 안내를 띄운다.
                표 자체(컬럼/자리표시자)는 이미 즉시 그려지므로 이 배너는 보조 안내다. */}
            {isLoading && (
              <div className="mb-3">
                <StatusInline
                  kind="loading"
                  message="비교할 상권데이터를 가져오는 중입니다."
                />
              </div>
            )}
            <div className="border-2 border-black bg-white overflow-x-auto">
              <table className="w-full text-left border-collapse font-mono text-xs sm:text-sm">
                <thead>
                  <tr className="border-b-2 border-black bg-[#eeede6]">
                  <th className="p-4 sm:p-5 font-black text-black w-44 sm:w-56 border-r-2 border-black text-sm sm:text-base">
                    비교 지표
                  </th>
                  {displayedItems.map(({ code, name, data }) => (
                    <th
                      key={code}
                      className="p-4 sm:p-5 font-black text-black border-r-2 border-black last:border-r-0 min-w-[220px]"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-xs text-gray-500 block font-normal">
                            {data?.district ?? cellFallback}
                          </span>
                          <span className="text-lg sm:text-xl font-black">
                            {data?.trade_area_name ?? name}
                          </span>
                        </div>
                        <button
                          onClick={() => hideFromComparison(code)}
                          className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                          title="제외하기"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-black">
                {/* 1. Exploration Score */}
                <tr className="bg-[#d4ff00]/20">
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]/70">
                    데이터 탐색 점수
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-extrabold text-base sm:text-lg text-black"
                    >
                      {data ? (
                        <div className="flex items-center gap-2">
                          <span className="bg-black text-white px-2.5 py-0.5 text-xs font-mono">
                            Score {data.exploration_score ?? "-"}
                          </span>
                          <span className="text-xs font-normal text-gray-500">
                            / 100
                          </span>
                        </div>
                      ) : (
                        cellFallback
                      )}
                    </td>
                  ))}
                </tr>

                {/* 2. Estimated Sales */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    추정 분기 매출
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-base text-black"
                    >
                      {data ? data.estimated_sales_formatted : cellFallback}
                    </td>
                  ))}
                </tr>

                {/* 3. Transaction Volume */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    거래 건수
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {data ? `${data.transaction_count_formatted}건` : cellFallback}
                    </td>
                  ))}
                </tr>

                {/* 4. QoQ Growth Rate */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    매출 성장률 (전분기비)
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {/* [연동] growth_rate 는 음수 가능(Optional[float]) → 부호 직접 계산, null 이면 "-" 표기 */}
                      {data ? (
                        <span className="bg-[#d4ff00] px-2 py-0.5 border border-black text-xs font-bold">
                          {data.growth_rate === null
                            ? "-"
                            : `${data.growth_rate > 0 ? "+" : ""}${data.growth_rate.toFixed(1)}%`}
                        </span>
                      ) : (
                        cellFallback
                      )}
                    </td>
                  ))}
                </tr>
                {/* 5. Store Count & Competition
                    [연동] GET /api/v1/compare 응답의 store_count / store_count_change / competition_level 을 사용한다
                    (backend/app/domain/analytics/schemas.py CompareDistrictData 기준).
                    competition_level 실제 값은 "높음" / "보통" / "낮음" 3단계(백엔드 CompetitionScore 기준)이며
                    "높음"을 경쟁 경고(빨강) 기준으로 맞춘다. */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    동일 업종 점포수 / 경쟁
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 text-black"
                    >
                      {data ? (
                        <>
                          <div className="font-bold">
                            {data.store_count ?? "-"}개 (
                            {data.store_count_change === null
                              ? "-"
                              : `${data.store_count_change > 0 ? "+" : ""}${data.store_count_change}개`}
                            )
                          </div>
                          <span
                            className={`inline-block mt-1 px-1.5 py-0.5 text-[11px] font-bold ${
                              data.competition_level === "높음"
                                ? "bg-red-500 text-white"
                                : "bg-gray-200 text-black"
                            }`}
                          >
                            경쟁 {data.competition_level ?? "-"}
                          </span>
                        </>
                      ) : (
                        cellFallback
                      )}
                    </td>
                  ))}
                </tr>

                {/* 6. Primary Age & Gender */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    주요 소비 타겟 (WHO)
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {data ? data.strongest_age_group : cellFallback}
                    </td>
                  ))}
                </tr>

                {/* 7. Peak Time */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    피크 소비 시간대 (WHEN)
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {data ? data.strongest_time_period : cellFallback}
                    </td>
                  ))}
                </tr>

                {/* 8. Peak Day */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    최대 매출 요일 (DAY)
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {data ? data.strongest_day : cellFallback}
                    </td>
                  ))}
                </tr>

                {/* 9. Key Insight */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    상권 탐색 요약
                  </td>
                  {displayedItems.map(({ code, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0 text-xs font-sans text-gray-800 leading-relaxed"
                    >
                      {data ? data.key_insight : cellFallback}
                    </td>
                  ))}
                </tr>

                {/* Action Row: Go to detail */}
                <tr className="bg-[#f5f5f0]">
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    상세 분석
                  </td>
                  {displayedItems.map(({ code, name, data }) => (
                    <td
                      key={code}
                      className="p-4 border-r-2 border-black last:border-r-0"
                    >
                      <button
                        onClick={() =>
                          navigate(
                            `/district/${code}?industry=${selectedIndustry}&quarter=${encodeURIComponent(
                              selectedQuarter,
                            )}`,
                          )
                        }
                        className="w-full py-2 bg-black text-white font-bold text-xs hover:bg-[#d4ff00] hover:text-black border border-black flex items-center justify-center gap-1.5 transition-colors"
                      >
                        <span>{data?.trade_area_name ?? name} 심층 보기</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
            </div>
          </>
        )}
      </section>
    </div>
  );
};
