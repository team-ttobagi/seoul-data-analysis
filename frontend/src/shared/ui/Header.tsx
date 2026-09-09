import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X, Layers, ArrowUpRight, Info } from "lucide-react";
import { useCompareStore } from "../lib/store";

export const Header: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  const { selectedCodes } = useCompareStore();

  const isExplore =
    location.pathname.startsWith("/explore") || location.pathname === "/";
  const isCompare = location.pathname.startsWith("/compare");

  return (
    <>
      <header className="sticky top-0 z-40 bg-[#f5f5f0] border-b-2 border-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Brand */}
          <Link
            to="/explore"
            className="flex items-center gap-2 text-xl font-extrabold tracking-tight font-display hover:opacity-85 transition-opacity"
          >
            <span className="bg-black text-white px-2 py-0.5 text-xs font-mono tracking-widest mr-1">
              SDP
            </span>
            <span className="tracking-tighter font-black text-lg sm:text-xl">
              SEOUL DATA PLAYGROUND
            </span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center space-x-8 font-mono text-sm font-bold">
            <Link
              to="/explore"
              className={`relative py-5 tracking-wider transition-colors hover:text-black ${
                isExplore ? "text-black font-extrabold" : "text-gray-500"
              }`}
            >
              EXPLORE
              {isExplore && (
                <span className="absolute bottom-0 left-0 w-full h-[3px] bg-[#d4ff00] border-t border-black" />
              )}
            </Link>

            <Link
              to="/compare"
              className={`relative py-5 tracking-wider flex items-center gap-1.5 transition-colors hover:text-black ${
                isCompare ? "text-black font-extrabold" : "text-gray-500"
              }`}
            >
              COMPARE
              {selectedCodes.length > 0 && (
                <span className="bg-black text-white text-[11px] font-mono px-1.5 py-0.2 rounded-none">
                  {selectedCodes.length}
                </span>
              )}
              {isCompare && (
                <span className="absolute bottom-0 left-0 w-full h-[3px] bg-[#d4ff00] border-t border-black" />
              )}
            </Link>

            <button
              onClick={() => setMethodologyOpen(true)}
              className="text-gray-600 hover:text-black flex items-center gap-1 font-mono text-xs border border-black/20 px-2 py-1 bg-white hover:bg-black hover:text-white transition-colors"
            >
              <Info className="w-3.5 h-3.5" />
              <span>산출 로직</span>
            </button>
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-3 md:hidden">
            <Link
              to="/compare"
              className="bg-black text-white text-xs font-mono px-2 py-1 flex items-center gap-1"
            >
              <Layers className="w-3.5 h-3.5" />
              {selectedCodes.length}
            </Link>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 border border-black bg-white"
            >
              {mobileMenuOpen ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-black bg-[#f5f5f0] px-4 py-4 space-y-3 font-mono">
            <Link
              to="/explore"
              onClick={() => setMobileMenuOpen(false)}
              className={`block py-2 text-base font-bold ${
                isExplore
                  ? "bg-[#d4ff00] px-2 text-black border border-black"
                  : "text-gray-700"
              }`}
            >
              EXPLORE (상권 탐색)
            </Link>
            <Link
              to="/compare"
              onClick={() => setMobileMenuOpen(false)}
              className={`block py-2 text-base font-bold ${
                isCompare
                  ? "bg-[#d4ff00] px-2 text-black border border-black"
                  : "text-gray-700"
              }`}
            >
              COMPARE (상권 비교 - {selectedCodes.length}개 선택됨)
            </Link>
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setMethodologyOpen(true);
              }}
              className="block w-full text-left py-2 text-sm text-gray-700 underline"
            >
              산출 로직 & 데이터 설명서
            </button>
          </div>
        )}
      </header>

      {/* Methodology Modal */}
      {methodologyOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="bg-[#f5f5f0] border-2 border-black w-full max-w-lg p-6 space-y-4 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]">
            <div className="flex items-center justify-between border-b border-black pb-3">
              <h3 className="font-extrabold text-lg flex items-center gap-2">
                <span className="bg-[#d4ff00] text-black px-2 py-0.5 font-mono text-xs border border-black">
                  METHODOLOGY
                </span>
                데이터 기반 탐색 점수 산출 로직
              </h3>
              <button
                onClick={() => setMethodologyOpen(false)}
                className="p-1 hover:bg-black hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-sm text-gray-800 leading-relaxed">
              본 서비스는{" "}
              <strong>서울시 상권분석서비스(Seoul Open Data)</strong>의
              추정매출, 점포 수, 유동 인구 통계를 기반으로 창업자가 우선적으로
              현장 조사할 가치가 높은 상권을 정량화합니다.
            </p>

            <div className="space-y-2 font-mono text-xs border border-black p-3 bg-white">
              <div className="flex justify-between py-1 border-b border-gray-200">
                <span>1. 매출 성장률 (Sales Growth)</span>
                <span className="font-bold">가중치 40%</span>
              </div>
              <div className="flex justify-between py-1 border-b border-gray-200">
                <span>2. 거래 활성도 (Transaction Volume)</span>
                <span className="font-bold">가중치 35%</span>
              </div>
              <div className="flex justify-between py-1 text-red-600 font-medium">
                <span>3. 경쟁 강도 (Competition Intensity - 역산)</span>
                <span className="font-bold">가중치 25%</span>
              </div>
            </div>

            <div className="bg-[#121212] text-white p-3 text-xs flex gap-2">
              <Info className="w-4 h-4 text-[#d4ff00] shrink-0 mt-0.5" />
              <span className="text-gray-300">
                <strong>주의</strong>: 이 점수는 창업 성공 확률이나 수익 보증이
                아니며, 추가 조사 및 현장 실사를 위한 탐색 지표입니다.
              </span>
            </div>

            <button
              onClick={() => setMethodologyOpen(false)}
              className="w-full py-2.5 bg-black text-white font-bold text-sm hover:bg-[#d4ff00] hover:text-black border border-black transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </>
  );
};

export const Footer: React.FC = () => {
  return (
    <footer className="border-t-2 border-black bg-[#121212] text-white py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
        <div className="flex items-center gap-2">
          <span className="font-extrabold text-sm sm:text-base tracking-tighter text-[#d4ff00]">
            SEOUL DATA PLAYGROUND
          </span>
        </div>
        <div className="text-gray-400 text-center md:text-right space-y-1">
          <p>© 2024–2026 SEOUL DATA PLAYGROUND. DATA-DRIVEN EDITORIAL.</p>
          <div className="flex justify-center md:justify-end gap-4 text-[11px] text-gray-500">
            <span className="hover:text-[#d4ff00] cursor-pointer">
              Methodology (가중치 40:35:25)
            </span>
            <span>•</span>
            <span className="hover:text-[#d4ff00] cursor-pointer">
              API Access (/api/v1)
            </span>
            <span>•</span>
            <span className="hover:text-[#d4ff00] cursor-pointer">
              Seoul Open Data Grounded
            </span>
          </div>
        </div>
      </div>
    </footer>
  );
};
