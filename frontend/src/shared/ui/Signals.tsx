import React from "react";

interface SignalsProps {
  growth: "high" | "medium" | "low";
  transaction: "high" | "medium" | "low";
  competition: "high" | "medium" | "low";
}

export const Signals: React.FC<SignalsProps> = ({ growth, transaction, competition }) => {
  const getArrow = (level: "high" | "medium" | "low") => {
    if (level === "high") return "⇡⇡";
    if (level === "medium") return "⇡";
    return "⇣";
  };

  return (
    <div className="flex items-center gap-3 font-mono text-xs font-bold">
      <span className="flex items-center gap-1 text-black">
        <span>성장</span>
        <span className="font-extrabold">{getArrow(growth)}</span>
      </span>

      <span className="flex items-center gap-1 text-black">
        <span>거래</span>
        <span className="font-extrabold">{getArrow(transaction)}</span>
      </span>

      <span
        className={`flex items-center gap-1 ${
          competition === "high" ? "text-[#e02424] font-extrabold" : "text-black"
        }`}
      >
        <span>경쟁</span>
        <span className="font-extrabold">{getArrow(competition)}</span>
      </span>
    </div>
  );
};

export const ScorePill: React.FC<{ score: number; isSelected?: boolean }> = ({
  score,
  isSelected = false,
}) => {
  return (
    <div
      className={`inline-flex items-center gap-1 px-2.5 py-0.5 font-mono text-xs font-bold border border-black ${
        isSelected
          ? "bg-black text-white"
          : "bg-white text-black"
      }`}
    >
      <span className="text-[10px] text-gray-400">Score</span>
      <span className="text-sm font-extrabold">{score}</span>
    </div>
  );
};
