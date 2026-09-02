import React from "react";
import { DistrictRankingItem, TimeSlotSales, AgeGenderSales, DaySales } from "../types";

// 1. Rank Bar Chart for "어디가 강할까?" (Matching Reference 2 Top Left)
interface RankBarChartProps {
  items: DistrictRankingItem[];
  currentCode: string;
  metricLabel?: string;
  onSelectDistrict?: (code: string) => void;
}

export const RankBarChart: React.FC<RankBarChartProps> = ({
  items,
  currentCode,
  metricLabel = "매출",
  onSelectDistrict,
}) => {
  const maxVal = Math.max(...items.map((i) => i.sales_raw || 1), 1);

  return (
    <div className="space-y-2.5 font-mono">
      {items.map((item, idx) => {
        const isCurrent =
          item.is_current || item.trade_area_code.toUpperCase() === currentCode.toUpperCase();
        const widthPercent = Math.max(15, Math.min(100, (item.sales_raw / maxVal) * 100));

        return (
          <div
            key={`${item.trade_area_code}-${idx}`}
            onClick={() => onSelectDistrict && onSelectDistrict(item.trade_area_code)}
            className={`flex items-center gap-3 text-sm group ${
              onSelectDistrict ? "cursor-pointer" : ""
            }`}
          >
            {/* Rank Number */}
            <span className="font-extrabold text-base w-7 shrink-0 text-black">
              {String(item.rank).padStart(2, "0")}
            </span>

            {/* Bar Container */}
            <div className="flex-1 relative h-9 border border-black bg-[#e5e5de] overflow-hidden flex items-center justify-between px-3">
              {/* Filled Portion */}
              <div
                className={`absolute left-0 top-0 bottom-0 transition-all duration-500 border-r border-black/40 ${
                  isCurrent ? "bg-[#d4ff00]" : "bg-[#dbdad2] group-hover:bg-[#d0cfc6]"
                }`}
                style={{ width: `${widthPercent}%` }}
              />

              {/* District Name + Current Badge */}
              <div className="relative z-10 flex items-center gap-2 font-bold text-black text-sm">
                <span>{item.trade_area_name}</span>
                {isCurrent && (
                  <span className="bg-black text-white text-[10px] font-mono px-1.5 py-0.5 tracking-tighter">
                    CURRENT
                  </span>
                )}
              </div>

              {/* Value formatted */}
              <div className="relative z-10 font-bold font-mono text-xs sm:text-sm text-black">
                {item.sales_formatted}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};

// 2. Time Bar Chart (Matching Reference 2 Top Right: "언제 가장 많이 팔릴까?")
interface TimeBarChartProps {
  slots: TimeSlotSales[];
  peakSlot: string;
}

export const TimeBarChart: React.FC<TimeBarChartProps> = ({ slots, peakSlot }) => {
  const maxPercent = Math.max(...slots.map((s) => s.percentage), 1);

  return (
    <div className="w-full">
      <div className="border border-black bg-white p-4 h-48 flex items-end justify-between gap-2 sm:gap-4 relative">
        {slots.map((slot) => {
          const isPeak = slot.is_peak || slot.slot.includes(peakSlot) || peakSlot.includes(slot.slot);
          const heightPercent = Math.max(18, (slot.percentage / maxPercent) * 90);

          return (
            <div key={slot.slot} className="flex-1 flex flex-col items-center h-full justify-end relative">
              {/* Peak Tooltip / Pill Badge */}
              {isPeak && (
                <div className="absolute -top-1 bg-white border border-black px-2 py-0.5 text-[11px] font-mono font-bold text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] z-10">
                  {peakSlot}
                </div>
              )}

              {/* Bar */}
              <div
                className={`w-full border border-black transition-all duration-500 ${
                  isPeak ? "bg-[#d4ff00]" : "bg-[#e5e5de] hover:bg-[#dbdad2]"
                }`}
                style={{ height: `${heightPercent}%` }}
              />
            </div>
          );
        })}
      </div>

      {/* Axis Labels */}
      <div className="flex justify-between font-mono text-[11px] text-gray-700 mt-2 px-1">
        {slots.map((s) => (
          <span key={s.slot} className="text-center flex-1">
            {s.slot.replace("시", "")}
          </span>
        ))}
      </div>
    </div>
  );
};

// 3. Age & Gender Breakdown Chart (Matching Reference 2 Middle Left: "누가 가장 많이 살까?")
interface AgeGenderBarChartProps {
  demographics: AgeGenderSales[];
  primaryTarget: string;
}

export const AgeGenderBarChart: React.FC<AgeGenderBarChartProps> = ({ demographics }) => {
  return (
    <div className="space-y-3 font-mono text-xs">
      {demographics.map((demo) => {
        const isPrimary = demo.is_primary || demo.percentage >= 40;

        return (
          <div key={demo.age_group} className="flex items-center gap-3">
            {/* Age Label */}
            <span className="w-12 shrink-0 font-bold text-sm text-black">
              {demo.age_group}
            </span>

            {/* Split Bar Container */}
            <div className="flex-1 h-8 border border-black bg-[#e5e5de] relative flex overflow-hidden">
              {/* Female Proportion */}
              <div
                className={`h-full border-r border-black flex items-center px-2 text-[11px] font-bold transition-all ${
                  isPrimary
                    ? "bg-[#d4ff00] text-black"
                    : "bg-[#d6d5cc] text-gray-800"
                }`}
                style={{ width: `${demo.female_ratio}%` }}
              >
                {isPrimary ? (
                  <span className="truncate">여성 우세</span>
                ) : (
                  <span className="truncate">{demo.female_ratio}%</span>
                )}
              </div>

              {/* Male Proportion */}
              <div
                className="h-full bg-[#eeede6] flex items-center justify-end px-2 text-[11px] text-gray-600"
                style={{ width: `${demo.male_ratio}%` }}
              >
                <span>{demo.male_ratio}%</span>
              </div>
            </div>

            {/* Overall Age Group Percentage */}
            <span className="w-10 text-right font-extrabold text-sm text-black">
              {demo.percentage}%
            </span>
          </div>
        );
      })}
    </div>
  );
};

// 4. Day of Week Bar Chart (Matching Reference 2 Middle Right: "어느 요일이 강할까?")
interface DayBarChartProps {
  days: DaySales[];
  peakDay: string;
  peakDiffBadge: string;
}

export const DayBarChart: React.FC<DayBarChartProps> = ({ days, peakDay, peakDiffBadge }) => {
  const maxPercent = Math.max(...days.map((d) => d.percentage), 1);

  return (
    <div className="w-full">
      <div className="border border-black bg-white p-4 h-48 flex items-end justify-between gap-1.5 sm:gap-3 relative">
        {days.map((day) => {
          const isPeak = day.is_peak || day.day === peakDay.replace("요일", "");
          const heightPercent = Math.max(20, (day.percentage / maxPercent) * 90);

          return (
            <div key={day.day} className="flex-1 flex flex-col items-center h-full justify-end relative">
              {/* Peak Tag */}
              {isPeak && (
                <div className="absolute -top-1 bg-white border border-black px-1.5 py-0.5 text-[11px] font-mono font-bold text-black shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] z-10">
                  {peakDiffBadge || "+21%"}
                </div>
              )}

              {/* Bar */}
              <div
                className={`w-full border border-black transition-all duration-500 ${
                  isPeak ? "bg-[#d4ff00]" : "bg-[#e5e5de] hover:bg-[#dbdad2]"
                }`}
                style={{ height: `${heightPercent}%` }}
              />
            </div>
          );
        })}
      </div>

      {/* Axis: Mon - Sun */}
      <div className="flex justify-between font-mono font-bold text-xs text-black mt-2 px-1">
        {days.map((d) => (
          <span
            key={d.day}
            className={`text-center flex-1 ${
              d.is_peak || d.day === peakDay.replace("요일", "")
                ? "text-black underline underline-offset-4 decoration-2"
                : "text-gray-700"
            }`}
          >
            {d.day}
          </span>
        ))}
      </div>
    </div>
  );
};
