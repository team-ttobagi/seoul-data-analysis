import React, { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Menu,
  X,
  Layers,
  ArrowUpRight,
  Info,
  BadgeInfo,
} from "lucide-react";
import { useCompareStore, useHeaderBreadcrumbStore } from "../lib/store";
import { PageGuideModal } from "./PageGuideModal";
import { MethodologyModal } from "./MethodologyModal";

export const Header: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  const { selectedCodes } = useCompareStore();
  const { breadcrumb, visible: breadcrumbVisible } = useHeaderBreadcrumbStore();

  const isExplore =
    location.pathname.startsWith("/explore") || location.pathname === "/";
  const isCompare = location.pathname.startsWith("/compare");

  // 헤더 nav의 "?" 아이콘을 누르면 현재 보고 있는 화면(탐색/상세/비교)에 맞는 사용법
  // 안내 모달을 띄운다. 내용/드래그 위치 등 모달 자체 로직은 PageGuideModal에 있다.
  const [guideOpen, setGuideOpen] = useState(false);
  // 순수 CSS :hover 툴팁은, 클릭으로 모달이 열려 마우스 위치를 덮어버리면 마우스가
  // 실제로 움직이기 전까지 브라우저가 :hover를 재계산하지 않아 잔상처럼 남는다.
  // 그래서 hover 상태를 직접 관리하고, 클릭 시점에 명시적으로 꺼준다.
  const [guideIconHovered, setGuideIconHovered] = useState(false);

  return (
    <>
      <header className="sticky top-0 z-40 bg-[#f5f5f0] border-b-2 border-black">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6 min-w-0">
            {/* Brand */}
            <Link
              to="/explore"
              className="flex shrink-0 items-center gap-2 transition-opacity hover:opacity-85"
              aria-label="스팟 레이더 홈"
            >
              <img
                src="/brand/spot-radar-loupe-icon-light.svg"
                alt=""
                className="h-9 w-9 shrink-0 sm:h-10 sm:w-10"
                aria-hidden="true"
              />
              <span className="whitespace-nowrap font-display text-lg font-black tracking-tighter text-black sm:text-xl">
                SPOT RADAR
              </span>
            </Link>

            {/* 상권 상세 화면의 브레드크럼이 스크롤로 헤더 밑에 가리면 여기 같은 내용을 보여준다.
                DistrictDetailPage.tsx의 원본과 동일한 폰트/사이즈(text-xs sm:text-sm font-mono)를 쓴다. */}
            {breadcrumbVisible && breadcrumb && (
              <div className="hidden md:flex items-center gap-2 text-xs sm:text-sm font-mono text-gray-700 min-w-0">
                <span className="font-bold text-black truncate">
                  {breadcrumb.pathLabel}
                </span>
                <span>|</span>
                <span className="whitespace-nowrap">
                  {breadcrumb.quarterLabel}
                </span>
              </div>
            )}
          </div>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center space-x-8 font-mono text-sm font-bold">
            <Link
              to="/explore"
              className={`relative py-5 tracking-wider transition-colors hover:text-black ${
                isExplore ? "text-black font-extrabold" : "text-gray-500"
              }`}
            >
              탐색
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
              비교
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
            <button
              type="button"
              onClick={() => {
                setGuideIconHovered(false);
                setGuideOpen(true);
              }}
              onMouseEnter={() => setGuideIconHovered(true)}
              onMouseLeave={() => setGuideIconHovered(false)}
              className="relative inline-flex"
            >
              <BadgeInfo className="w-4 h-4 text-gray-500 hover:text-black cursor-pointer transition-colors" />
              {guideIconHovered && (
                <span className="pointer-events-none absolute left-1/2 top-full mt-2 -translate-x-1/2 whitespace-nowrap bg-black text-white text-[11px] font-mono px-2 py-1 z-10">
                  상권탐색을 도와드려요
                  <span className="absolute left-1/2 bottom-full -translate-x-1/2 w-0 h-0 border-x-4 border-x-transparent border-b-4 border-b-black" />
                </span>
              )}
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
              탐색
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
              비교 ({selectedCodes.length}개 선택됨)
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
            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setGuideOpen(true);
              }}
              className="block w-full text-left py-2 text-sm text-gray-700 underline"
            >
              화면 사용법 도움말
            </button>
          </div>
        )}
      </header>

      {/* METHODOLOGY(가중치 요약) + DETAIL(산출 로직 자세히 보기) 모달 — 두 모달 모두
          별도 파일(MethodologyModal)에서 관리하고, 여기서는 열림 여부만 소유한다. */}
      <MethodologyModal
        open={methodologyOpen}
        onClose={() => setMethodologyOpen(false)}
      />

      {/* 화면 사용법 안내 모달 — 헤더 nav의 "?" 아이콘을 누르면, 지금 보고 있는 화면
          (탐색/상세/비교)에 맞는 안내가 뜬다. 모달 자체는 별도 파일(PageGuideModal)에서
          관리하고, 여기서는 열림 여부만 소유한다. */}
      <PageGuideModal open={guideOpen} onClose={() => setGuideOpen(false)} />
    </>
  );
};

export const Footer: React.FC = () => {
  return (
    <footer className="border-t-2 border-black bg-[#121212] text-white py-10 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 font-mono text-xs">
        <div className="flex items-center gap-3">
          <img
            src="/brand/spot-radar-loupe-icon-dark.svg"
            alt=""
            className="h-11 w-11 shrink-0 sm:h-12 sm:w-12"
            aria-hidden="true"
          />
          <span className="whitespace-nowrap font-mono text-sm font-extrabold tracking-tighter text-[#d4ff00] sm:text-base">
            SPOT RADAR
          </span>
        </div>
        <div className="text-gray-400 text-center md:text-right space-y-1">
          <p>© 2024–2026 SPOT RADAR. DATA-DRIVEN EDITORIAL.</p>
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
