import React, { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Menu,
  X,
  Layers,
  ArrowUpRight,
  Info,
  FileQuestionMark,
} from "lucide-react";
import { useCompareStore, useHeaderBreadcrumbStore } from "../lib/store";

type DragPos = { x: number; y: number };

// 모달 헤더바를 마우스로 누른 채 움직이면 모달 전체가 따라 이동하게 해주는 훅.
// pos는 기본(중앙) 위치로부터의 픽셀 오프셋이며, onMouseDown을 헤더바에 걸어 쓴다.
function useDraggablePosition(initial: DragPos) {
  const [pos, setPos] = useState<DragPos>(initial);
  const [dragging, setDragging] = useState(false);
  const start = useRef<DragPos>({ x: 0, y: 0 });
  const origin = useRef<DragPos>({ x: 0, y: 0 });

  const onMouseDown = (e: React.MouseEvent) => {
    start.current = { x: e.clientX, y: e.clientY };
    origin.current = pos;
    setDragging(true);
  };

  useEffect(() => {
    if (!dragging) return;
    const handleMouseMove = (e: MouseEvent) => {
      setPos({
        x: origin.current.x + (e.clientX - start.current.x),
        y: origin.current.y + (e.clientY - start.current.y),
      });
    };
    const handleMouseUp = () => setDragging(false);
    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [dragging]);

  return { pos, setPos, onMouseDown };
}

export const Header: React.FC = () => {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [methodologyOpen, setMethodologyOpen] = useState(false);
  const { selectedCodes } = useCompareStore();
  const { breadcrumb, visible: breadcrumbVisible } = useHeaderBreadcrumbStore();

  // Methodology 모달은 중앙 정렬된 카드를 기준으로 한 translate 오프셋(드래그 델타)을 쓴다.
  // DETAIL 모달은 열릴 때마다 Methodology 카드의 실제 화면 좌표(getBoundingClientRect)를
  // 기준으로 절대 top/left를 계산해야 카드 크기가 서로 달라도(폭 512px vs 672px)
  // "top 동일, left +10px"이 실제 화면에서 정확히 맞는다 — 두 카드 모두 같은 중앙 정렬
  // translate만 쓰면 폭 차이의 절반만큼 어긋난다.
  const methodologyDrag = useDraggablePosition({ x: 0, y: 0 });
  const methodologyCardRef = useRef<HTMLDivElement>(null);
  const detailsDrag = useDraggablePosition({ x: 100, y: 100 });
  const [detailsOpen, setDetailsOpen] = useState(false);

  const isExplore =
    location.pathname.startsWith("/explore") || location.pathname === "/";
  const isCompare = location.pathname.startsWith("/compare");

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
              onClick={() => {
                methodologyDrag.setPos({ x: 0, y: 0 });
                setMethodologyOpen(true);
              }}
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
                methodologyDrag.setPos({ x: 0, y: 0 });
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
          <div
            ref={methodologyCardRef}
            className="bg-[#f5f5f0] border-2 border-black w-full max-w-lg p-6 space-y-4 shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"
            style={{
              transform: `translate(${methodologyDrag.pos.x}px, ${methodologyDrag.pos.y}px)`,
            }}
          >
            <div
              onMouseDown={methodologyDrag.onMouseDown}
              className="flex items-center justify-between border-b border-black pb-3 cursor-move select-none"
            >
              <h3 className="font-extrabold text-lg flex items-center gap-2">
                <span className="bg-[#d4ff00] text-black px-2 py-0.5 font-mono text-xs border border-black">
                  METHODOLOGY
                </span>
                데이터 기반 탐색 점수 산출 로직
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    const rect = methodologyCardRef.current?.getBoundingClientRect();
                    if (rect) {
                      detailsDrag.setPos({ x: rect.left + 10, y: rect.top });
                    }
                    setDetailsOpen(true);
                  }}
                  onMouseDown={(e) => e.stopPropagation()}
                  className="relative inline-flex group"
                >
                  <FileQuestionMark className="w-4 h-4 text-gray-400 hover:text-black cursor-pointer transition-colors" />
                  <span className="pointer-events-none absolute left-1/2 -top-2 -translate-x-1/2 -translate-y-full whitespace-nowrap bg-black text-white text-[11px] font-mono px-2 py-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                    산출 로직 자세히 보기
                    <span className="absolute left-1/2 top-full -translate-x-1/2 w-0 h-0 border-x-4 border-x-transparent border-t-4 border-t-black" />
                  </span>
                </button>
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
              {/* 2026.09.21 유동인구통계 --> 거래 활성도로 수정 (backup:추정매출, 점포 수, 유동 인구 통계를 기반으로 창업자가 우선적으로)*/}
              추정매출, 점포 수, 거래 활성도를 기반으로 창업자가 우선적으로 현장
              조사할 가치가 높은 상권을 정량화합니다.
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
                <span>3. 경쟁 여건 (Competition Intensity - 역산)</span>
                {/* 2026.09.21 경쟁 강도--> 경쟁 여건*/}
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

      {/* 산출 로직 상세 모달 — Methodology 모달 위에 겹쳐서 뜨며, 상단 바를 잡고 드래그해
          자리를 옮길 수 있다. 바깥 래퍼는 pointer-events-none으로 비워둬 카드 밖 클릭은
          아래 Methodology 모달까지 그대로 전달되게 한다. */}
      {detailsOpen && (
        <div className="fixed inset-0 z-[60] pointer-events-none">
          <div
            className="pointer-events-auto fixed bg-white border-2 border-black w-full max-w-2xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)]"
            style={{
              top: detailsDrag.pos.y,
              left: detailsDrag.pos.x,
            }}
          >
            <div
              onMouseDown={detailsDrag.onMouseDown}
              className="flex items-center justify-between border-b-2 border-black px-4 py-2.5 bg-[#d4ff00] cursor-move select-none"
            >
              <h4 className="font-extrabold text-sm flex items-center gap-2">
                <span className="bg-black text-white px-1.5 py-0.5 font-mono text-[10px]">
                  DETAIL
                </span>
                산출 로직 자세히 보기
              </h4>
              <button
                onClick={() => setDetailsOpen(false)}
                className="p-1 hover:bg-black hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-4 space-y-4 font-mono text-[11px] text-gray-800 max-h-[75vh] overflow-y-auto">
              <div className="bg-[#d4ff00] border border-black px-3 py-2 font-bold text-black">
                핵심 대원칙: 모든 점수는 높을수록 진입하기 유리한 좋은
                상권입니다.
              </div>

              {/* 1. Growth Score */}
              <section className="border border-black">
                <header className="bg-black text-white px-3 py-1.5 font-bold flex items-center gap-2">
                  <span className="bg-[#d4ff00] text-black px-1.5 py-0.5 text-[10px]">
                    01
                  </span>
                  성장 점수 (Growth Score) · 윈저라이징
                </header>
                <div className="p-3 space-y-2 bg-[#f5f5f0]">
                  <p>
                    <strong>목적</strong>: 신규 진입 상권의 기저효과(착시)를
                    제거하여 기존 우수 상권의 변별력을 구제합니다.
                  </p>
                  <p>
                    <strong>원리</strong>: 상위 95% 경계선 밖의 극단치를
                    강제로 깎아내려 전체 점수 왜곡을 방지합니다.
                  </p>
                  <table className="w-full border-collapse border border-black bg-white text-[10px] sm:text-[11px]">
                    <thead>
                      <tr className="bg-[#eeede6] border-b border-black">
                        <th className="p-1.5 border-r border-black text-left">
                          상권
                        </th>
                        <th className="p-1.5 border-r border-black">
                          실제 성장률
                        </th>
                        <th className="p-1.5 border-r border-black">
                          기존 정규화
                        </th>
                        <th className="p-1.5 border-r border-black">
                          변경 후
                        </th>
                        <th className="p-1.5 text-left">비고</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          A 상권 (신규 진입)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          +4,900%
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          100점
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold">
                          100점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          경계값 클리핑으로 타 상권 왜곡 방지
                        </td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          성수동 (우수 상권)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          +25%
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          0.5점
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold text-[#0a7a3d]">
                          92점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          진짜 유망 상권의 변별력 회복
                        </td>
                      </tr>
                      <tr>
                        <td className="p-1.5 border-r border-black font-bold">
                          평범 상권 (평균 수준)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          +5%
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          0.1점
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold">
                          50점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          평균 수준 점수의 정상화
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {/* 2. Transaction Score */}
              <section className="border border-black">
                <header className="bg-black text-white px-3 py-1.5 font-bold flex items-center gap-2">
                  <span className="bg-[#d4ff00] text-black px-1.5 py-0.5 text-[10px]">
                    02
                  </span>
                  거래 활성도 점수 (Transaction Score) · 로그 변환
                </header>
                <div className="p-3 space-y-2 bg-[#f5f5f0]">
                  <p>
                    <strong>목적</strong>: 대형 상권과 골목 상권 간의 압도적인
                    체급 격차를 완화합니다.
                  </p>
                  <p>
                    <strong>원리</strong>: 숫자가 커질수록 머리를 누르는
                    고무줄 효과(자연로그 변환)로 100배의 차이를 1.5배 차이로
                    압축합니다.
                  </p>
                  <table className="w-full border-collapse border border-black bg-white text-[10px] sm:text-[11px]">
                    <thead>
                      <tr className="bg-[#eeede6] border-b border-black">
                        <th className="p-1.5 border-r border-black text-left">
                          상권
                        </th>
                        <th className="p-1.5 border-r border-black">
                          실제 거래
                        </th>
                        <th className="p-1.5 border-r border-black">
                          기존 선형
                        </th>
                        <th className="p-1.5 border-r border-black">
                          변경 후
                        </th>
                        <th className="p-1.5 text-left">비고</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          강남역 (초대형)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          1,000,000건
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          100점
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold">
                          100점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          최상위 체급 인정
                        </td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          대학가 (알짜 시장)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          50,000건
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          5.0점
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold text-[#0a7a3d]">
                          81.4점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          매력적인 알짜 시장으로 부각
                        </td>
                      </tr>
                      <tr>
                        <td className="p-1.5 border-r border-black font-bold">
                          골목상권 (소규모)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          10,000건
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          1.0점
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold text-[#0a7a3d]">
                          68.2점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          비교 가능한 궤도 진입
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {/* 3. Competition Score */}
              <section className="border border-black">
                <header className="bg-black text-white px-3 py-1.5 font-bold flex items-center gap-2">
                  <span className="bg-[#d4ff00] text-black px-1.5 py-0.5 text-[10px]">
                    03
                  </span>
                  경쟁 점수 (Competition Score) · 3차원 모델
                </header>
                <div className="p-3 space-y-2 bg-[#f5f5f0]">
                  <p>
                    <strong>목적</strong>: 창업자 진입 시 매력도를 평가합니다
                    (점수가 높을수록 경쟁 빈틈이 많아 안전한 꿀 상권).
                  </p>
                  <p>
                    <strong>가중치 반영 논리</strong>: 점포 수(50%) + 점포당
                    수요(30%) + 폐업률(20%)로 구성되며, 모든 항목은
                    안전할수록 고득점으로 설계됩니다.
                  </p>
                  <table className="w-full border-collapse border border-black bg-white text-[10px] sm:text-[11px]">
                    <thead>
                      <tr className="bg-[#eeede6] border-b border-black">
                        <th className="p-1.5 border-r border-black text-left">
                          항목 (가중치)
                        </th>
                        <th className="p-1.5 border-r border-black">
                          A 상권 (레드오션)
                        </th>
                        <th className="p-1.5 border-r border-black">
                          B 상권 (블루오션)
                        </th>
                        <th className="p-1.5 text-left">해석</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          점포 수 (50%)
                        </td>
                        <td className="p-1.5 border-r border-black text-center text-red-600">
                          200개(포화) → 10점
                        </td>
                        <td className="p-1.5 border-r border-black text-center text-[#0a7a3d]">
                          5개(여유) → 90점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          점포 수가 적을수록 고득점
                        </td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          점포당 수요 (30%)
                        </td>
                        <td className="p-1.5 border-r border-black text-center text-red-600">
                          월 10명(치열) → 20점
                        </td>
                        <td className="p-1.5 border-r border-black text-center text-[#0a7a3d]">
                          월 500명(풍부) → 80점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          내 몫이 많을수록 고득점
                        </td>
                      </tr>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          폐업률 (20%)
                        </td>
                        <td className="p-1.5 border-r border-black text-center text-red-600">
                          15%(위험) → 15점
                        </td>
                        <td className="p-1.5 border-r border-black text-center text-[#0a7a3d]">
                          1%(안전) → 95점
                        </td>
                        <td className="p-1.5 text-gray-600">
                          낮고 안전할수록 고득점
                        </td>
                      </tr>
                      <tr className="bg-[#eeede6]">
                        <td className="p-1.5 border-r border-black font-bold">
                          최종 경쟁 점수
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold text-red-600">
                          14점 (진입 위험)
                        </td>
                        <td className="p-1.5 border-r border-black text-center font-bold text-[#0a7a3d]">
                          88점 (안전 및 추천)
                        </td>
                        <td className="p-1.5" />
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>

              {/* 4. Exploration Score */}
              <section className="border border-black">
                <header className="bg-black text-white px-3 py-1.5 font-bold flex items-center gap-2">
                  <span className="bg-[#d4ff00] text-black px-1.5 py-0.5 text-[10px]">
                    04
                  </span>
                  최종 탐색 점수 (Exploration Score) · 종합 가중치
                </header>
                <div className="p-3 space-y-2 bg-[#f5f5f0]">
                  <p>
                    <strong>목적</strong>: 서비스 아이덴티티인 '새로운 기회
                    탐색'에 최적화된 상권을 우선 추천합니다.
                  </p>
                  <p>
                    <strong>종합 산출식</strong>: (성장 점수 × 0.40) + (거래
                    활성도 점수 × 0.35) + (경쟁 점수 × 0.25)
                  </p>
                  <table className="w-full border-collapse border border-black bg-white text-[10px] sm:text-[11px]">
                    <thead>
                      <tr className="bg-[#eeede6] border-b border-black">
                        <th className="p-1.5 border-r border-black text-left">
                          유형
                        </th>
                        <th className="p-1.5 border-r border-black">
                          거래량
                        </th>
                        <th className="p-1.5 border-r border-black">
                          성장성
                        </th>
                        <th className="p-1.5 border-r border-black">
                          경쟁 빈틈
                        </th>
                        <th className="p-1.5">최종 점수</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-gray-300">
                        <td className="p-1.5 border-r border-black font-bold">
                          신림동형 (정체된 대형 상권)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          95점
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          40점
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          30점
                        </td>
                        <td className="p-1.5 text-center font-bold">
                          56.75점
                        </td>
                      </tr>
                      <tr className="bg-[#d4ff00]/30">
                        <td className="p-1.5 border-r border-black font-bold">
                          성수동형 (성장하는 유망 상권)
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          70점
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          90점
                        </td>
                        <td className="p-1.5 border-r border-black text-center">
                          70점
                        </td>
                        <td className="p-1.5 text-center font-bold text-[#0a7a3d]">
                          78.00점 (우승)
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div className="text-gray-600 space-y-0.5">
                    <p>
                      신림동형: (40×0.4) + (95×0.35) + (30×0.25) = 56.75점
                    </p>
                    <p>
                      성수동형: (90×0.4) + (70×0.35) + (70×0.25) = 78.00점
                    </p>
                  </div>
                  <div className="border-l-4 border-[#d4ff00] pl-3 py-1 italic text-gray-700">
                    "순수 매출 크기만 보면 신림동형이 높겠지만, 이는 기회를
                    발굴하는 탐색 서비스 목적에 맞지 않습니다. 따라서
                    성장성(40%)에 가장 높은 가중치를 두어, 체급은 작아도
                    향후 진입 시 상승을 기대할 수 있는 성수동형 상권이
                    최상위에 노출되도록 설계했습니다."
                  </div>
                </div>
              </section>

              <p className="text-gray-500">
                등급 기준: 70점 이상 <strong>높음/좋음</strong> · 40~70점{" "}
                <strong>보통</strong> · 40점 미만 <strong>낮음/나쁨</strong>
              </p>
            </div>
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
