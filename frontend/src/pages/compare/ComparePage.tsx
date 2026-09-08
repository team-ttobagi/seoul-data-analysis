import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  ArrowLeft,
  Trash2,
  Plus,
  ArrowUpRight,
  ExternalLink,
} from "lucide-react";
import { api } from "../../shared/api/client";
import { useCompareStore } from "../../shared/lib/store";
import { ScorePill } from "../../shared/ui/Signals";

/* ---------------------------------------------- */
// Update by SoO 2026.09.07
//   store_count
//   store_count_change 동일 업종 점포수 / 경쟁 주석처리
/* ---------------------------------------------- */

export const ComparePage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedCodes, removeDistrict, addDistrict, clearDistricts } =
    useCompareStore();
  const [selectedIndustry] = useState("CS100010");
  const [selectedQuarter] = useState("2026 Q2");

  const { data: allTradeAreas = [] } = useQuery({
    queryKey: ["trade-areas"],
    queryFn: api.getTradeAreas,
  });

  const { data: compareList = [], isLoading } = useQuery({
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
    enabled: selectedCodes.length > 0,
  });

  const availableToAdd = allTradeAreas.filter(
    (ta) => !selectedCodes.includes(ta.code),
  );

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
              최대 3개 상권의 핵심 지표를 나란히 비교하여 후보지를 압축하세요.
            </p>
          </div>

          {selectedCodes.length > 0 && (
            <button
              onClick={clearDistricts}
              className="px-3 py-1.5 border border-black font-mono text-xs font-bold bg-white hover:bg-black hover:text-white transition-colors flex items-center gap-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>선택 초기화</span>
            </button>
          )}
        </div>

        {/* Quick Add Bar */}
        <div className="mt-6 flex flex-wrap items-center gap-2">
          <span className="font-mono text-xs font-bold text-gray-700">
            상권 추가 ({selectedCodes.length}/3):
          </span>
          {availableToAdd.map((ta) => (
            <button
              key={ta.code}
              disabled={selectedCodes.length >= 3}
              onClick={() => addDistrict(ta.code)}
              className="px-2.5 py-1 text-xs font-mono font-bold border border-black bg-white hover:bg-[#d4ff00] disabled:opacity-40 disabled:hover:bg-white flex items-center gap-1 transition-colors"
            >
              <Plus className="w-3 h-3" />
              {ta.name}
            </button>
          ))}
        </div>
      </section>

      {/* Comparison Table / Matrix */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-8">
        {selectedCodes.length === 0 ? (
          <div className="border-2 border-black p-12 text-center bg-white space-y-4">
            <p className="font-mono text-base font-bold text-gray-800">
              비교할 상권이 선택되지 않았습니다.
            </p>
            <Link
              to="/explore"
              className="inline-block px-4 py-2 bg-[#d4ff00] text-black border border-black font-bold font-mono text-sm hover:bg-black hover:text-white transition-colors"
            >
              탐색 목록에서 상권 담기
            </Link>
          </div>
        ) : (
          <div className="border-2 border-black bg-white overflow-x-auto">
            <table className="w-full text-left border-collapse font-mono text-xs sm:text-sm">
              <thead>
                <tr className="border-b-2 border-black bg-[#eeede6]">
                  <th className="p-4 sm:p-5 font-black text-black w-44 sm:w-56 border-r-2 border-black text-sm sm:text-base">
                    비교 지표
                  </th>
                  {compareList.map((item) => (
                    <th
                      key={item.trade_area_code}
                      className="p-4 sm:p-5 font-black text-black border-r-2 border-black last:border-r-0 min-w-[220px]"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-xs text-gray-500 block font-normal">
                            {item.district}
                          </span>
                          <span className="text-lg sm:text-xl font-black">
                            {item.trade_area_name}
                          </span>
                        </div>
                        <button
                          onClick={() => removeDistrict(item.trade_area_code)}
                          className="p-1 text-gray-400 hover:text-red-600 transition-colors"
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
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-extrabold text-base sm:text-lg text-black"
                    >
                      <div className="flex items-center gap-2">
                        <span className="bg-black text-white px-2.5 py-0.5 text-xs font-mono">
                          Score {item.exploration_score}
                        </span>
                        <span className="text-xs font-normal text-gray-500">
                          / 100
                        </span>
                      </div>
                    </td>
                  ))}
                </tr>

                {/* 2. Estimated Sales */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    추정 분기 매출
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-base text-black"
                    >
                      {item.estimated_sales_formatted}
                    </td>
                  ))}
                </tr>

                {/* 3. Transaction Volume */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    거래 건수
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {item.transaction_count_formatted}건
                    </td>
                  ))}
                </tr>

                {/* 4. QoQ Growth Rate */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    매출 성장률 (전분기비)
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      <span className="bg-[#d4ff00] px-2 py-0.5 border border-black text-xs font-bold">
                        +{item.growth_rate}%
                      </span>
                    </td>
                  ))}
                </tr>
                {/* === Update by SoO 2026.09.07 ===========
                      2. [fix] 점포 관련 UI 및 데이터 참조 제거
                        2-2. Compare 화면의 점포 수 / 점포 수 변화 표시 제거
                  */}
                {/* 5. Store Count & Competition */}
                {/* <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    동일 업종 점포수 / 경쟁
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 text-black"
                    >
                      <div className="font-bold">{item.store_count}개 (+{item.store_count_change}개)</div>
                      <span
                        className={`inline-block mt-1 px-1.5 py-0.2 text-[11px] font-bold ${
                          item.competition_level === "매우 높음"
                            ? "bg-red-500 text-white"
                            : "bg-gray-200 text-black"
                        }`}
                      >
                        경쟁 {item.competition_level}
                      </span>
                    </td>
                  ))}
                </tr> */}

                {/* 6. Primary Age & Gender */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    주요 소비 타겟 (WHO)
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {item.strongest_age_group}
                    </td>
                  ))}
                </tr>

                {/* 7. Peak Time */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    피크 소비 시간대 (WHEN)
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {item.strongest_time_period}
                    </td>
                  ))}
                </tr>

                {/* 8. Peak Day */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    최대 매출 요일 (DAY)
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 font-bold text-black"
                    >
                      {item.strongest_day}
                    </td>
                  ))}
                </tr>

                {/* 9. Key Insight */}
                <tr>
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    상권 탐색 요약
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0 text-xs font-sans text-gray-800 leading-relaxed"
                    >
                      {item.key_insight}
                    </td>
                  ))}
                </tr>

                {/* Action Row: Go to detail */}
                <tr className="bg-[#f5f5f0]">
                  <td className="p-4 font-bold text-black border-r-2 border-black bg-[#eeede6]">
                    상세 분석
                  </td>
                  {compareList.map((item) => (
                    <td
                      key={item.trade_area_code}
                      className="p-4 border-r-2 border-black last:border-r-0"
                    >
                      <button
                        onClick={() =>
                          navigate(
                            `/district/${item.trade_area_code}?industry=${selectedIndustry}&quarter=${encodeURIComponent(
                              selectedQuarter,
                            )}`,
                          )
                        }
                        className="w-full py-2 bg-black text-white font-bold text-xs hover:bg-[#d4ff00] hover:text-black border border-black flex items-center justify-center gap-1.5 transition-colors"
                      >
                        <span>{item.trade_area_name} 심층 보기</span>
                        <ArrowUpRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
};
