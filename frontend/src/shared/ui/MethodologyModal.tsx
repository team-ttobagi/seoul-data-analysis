import React, { useEffect, useRef, useState } from "react";
import { X, Info, FileQuestionMark } from "lucide-react";
import { useDraggablePosition } from "../lib/useDraggablePosition";

interface MethodologyModalProps {
  open: boolean;
  onClose: () => void;
}

// METHODOLOGY(가중치 요약) 모달과, 그 안의 "?" 아이콘으로 여는 DETAIL(산출 로직 자세히
// 보기) 모달을 함께 관리한다. DETAIL은 METHODOLOGY 카드 위에 겹쳐서 뜨고, 열릴 때마다
// METHODOLOGY의 실제 화면 좌표(getBoundingClientRect)를 기준으로 위치를 잡아야 카드
// 크기가 서로 달라도(폭 512px vs 672px) "top 동일, left +10px"이 정확히 맞는다.
export const MethodologyModal: React.FC<MethodologyModalProps> = ({
  open,
  onClose,
}) => {
  const methodologyDrag = useDraggablePosition({ x: 0, y: 0 });
  const methodologyCardRef = useRef<HTMLDivElement>(null);
  const detailsDrag = useDraggablePosition({ x: 100, y: 100 });
  const [detailsOpen, setDetailsOpen] = useState(false);

  // 열릴 때마다 항상 중앙(오프셋 0,0)에서 다시 시작한다.
  useEffect(() => {
    if (open) {
      methodologyDrag.setPos({ x: 0, y: 0 });
    } else {
      setDetailsOpen(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (!open) return null;

  return (
    <>
      {/* Methodology Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
        <div
          ref={methodologyCardRef}
          className="bg-[#f5f5f0] border-2 border-black w-full max-w-lg p-6 space-y-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,0.2)]"
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
                    // DETAIL 모달(max-w-2xl = 672px)이 화면 오른쪽 밖으로 나가지
                    // 않도록, 화면 폭이 좁으면 오른쪽 여백 16px에 맞춰 x를 눌러준다.
                    const DETAIL_MODAL_WIDTH = 672;
                    const maxX = window.innerWidth - DETAIL_MODAL_WIDTH - 16;
                    detailsDrag.setPos({
                      x: Math.min(rect.left + rect.width + 10, Math.max(16, maxX)),
                      y: rect.top,
                    });
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
              onClick={onClose}
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
            onClick={onClose}
            className="w-full py-2.5 bg-black text-white font-bold text-sm hover:bg-[#d4ff00] hover:text-black border border-black transition-colors"
          >
            닫기
          </button>
        </div>
      </div>

      {/* 산출 로직 상세 모달 — Methodology 모달 위에 겹쳐서 뜨며, 상단 바를 잡고 드래그해
          자리를 옮길 수 있다. 바깥 래퍼는 pointer-events-none으로 비워둬 카드 밖 클릭은
          아래 Methodology 모달까지 그대로 전달되게 한다. */}
      {detailsOpen && (
        <div className="fixed inset-0 z-[60] pointer-events-none">
          <div
            className="pointer-events-auto fixed bg-white border-2 border-black w-full max-w-2xl shadow-[3px_3px_0px_0px_rgba(0,0,0,0.2)]"
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

            <div className="scrollbar-gray p-4 space-y-4 font-mono text-[11px] text-gray-800 max-h-[75vh] overflow-y-auto">
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
