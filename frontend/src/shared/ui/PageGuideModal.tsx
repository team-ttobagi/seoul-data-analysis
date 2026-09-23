import React, { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { X } from "lucide-react";
import { useDraggablePosition } from "../lib/useDraggablePosition";

interface GuideItem {
  // 사용자의 궁금증을 표현한 질문형 제목.
  title: string;
  // 해당 기능의 목적과 사용자가 확인할 수 있는 결과.
  description: string;
  // 기능을 사용하는 데 필요한 최소 단계.
  steps: string[];
  // public/ 기준 경로. 있으면 "화면 예시 보기"를 눌렀을 때 스크린샷을 보여준다.
  image?: string;
}

type GuideSectionKey = "explore" | "district" | "compare";

interface GuideSection {
  tabLabel: string;
  title: string;
  items: GuideItem[];
}

// 헤더의 탐색/상세/비교 탭으로 화면을 고르면 그 화면의 질문 중심 도움말이 뜬다.
// 각 항목은 실제 UI 기능을 그대로 설명하며, 확인되지 않은 계산식·해석이나
// 구현되지 않은 기능은 담지 않는다.
const GUIDE_SECTIONS: Record<GuideSectionKey, GuideSection> = {
  explore: {
    tabLabel: "탐색",
    title: "탐색 화면 사용법",
    items: [
      {
        title: "원하는 지역·업종·분기로 상권을 어떻게 찾나요?",
        description:
          "상단 필터바에서 조건을 선택하면 추천 상권 리스트가 그 조건에 맞게 바뀝니다.",
        steps: [
          "업종 카테고리를 선택합니다.",
          "분석 지역을 선택합니다.",
          "기준 분기를 선택합니다.",
        ],
        image: "/guide/search.png",
      },
      {
        title: "특정 상권 이름으로 바로 찾을 수 있나요?",
        description:
          "'상권 검색'에 이름을 입력하면 목록이 입력한 글자를 포함하는 상권으로 바로 좁혀집니다.",
        steps: [
          "'상권 검색' 입력창에 상권 이름을 입력합니다.",
          "아래에 뜨는 목록에서 원하는 상권을 선택합니다.",
        ],
        image: "/guide/search-dropdown.png",
      },
      {
        title: "상권 상세 정보는 어떻게 보나요?",
        description: "카드를 클릭하면 그 상권의 상세 화면으로 이동합니다.",
        steps: ["목록에서 원하는 상권 카드를 클릭합니다."],
        image: "/guide/explore-card-click.png",
      },
      {
        title: "여러 상권을 어떻게 비교 목록에 담나요?",
        description:
          "카드의 '비교' 버튼을 누르면 최대 7개 상권을 비교 목록에 저장할 수 있습니다.",
        steps: ["카드의 '비교' 버튼을 클릭합니다."],
        image: "/guide/explore-card-compare-toggle.png",
      },
      {
        title: "SCORE는 어떤 기준으로 계산되는지 어디서 확인하나요?",
        description:
          "헤더의 '산출 로직' 버튼을 누르면 SCORE 산출 방식을 자세히 볼 수 있습니다.",
        steps: ["헤더의 '산출 로직' 버튼을 클릭합니다."],
        image: "/guide/header-methodology-button.png",
      },
      {
        title: "담아둔 상권 개수는 어디서 확인하나요?",
        description:
          "헤더의 '비교' 메뉴에서 지금까지 담아둔 상권 개수를 바로 확인할 수 있습니다.",
        steps: ["헤더 오른쪽 위 '비교' 메뉴를 확인합니다."],
        image: "/guide/header-compare-menu.png",
      },
    ],
  },
  district: {
    tabLabel: "상세",
    title: "상권 상세 화면 사용법",
    items: [
        {
          title: "이 상권의 종합 점수와 AI 요약은 어디서 보나요?",
          description:
            "OVERALL INSIGHT 카드에서 이 상권의 종합 SCORE와 AI 인사이트 요약을 확인할 수 있습니다.",
          steps: ["화면 상단 OVERALL INSIGHT 카드를 확인합니다."],
          image: "/guide/overview-score.png",
        },
        {
          title: "이 상권의 경쟁 상황은 어떻게 확인하나요?",
          description:
            "경쟁은 어떨까? 카드에서 매출·거래량·경쟁 여건 수준을 확인할 수 있습니다.",
          steps: ["'경쟁은 어떨까?' 카드를 확인합니다."],
          image: "/guide/competition-overview.png",
        },
        {
          title: "다른 상권과의 순위를 비교할 수 있나요?",
          description:
            "어디가 강할까? 탭(매출/거래건수/성장률/탐색점수)으로 서울 전체 상권과의 순위를 비교할 수 있습니다.",
          steps: [
            "'어디가 강할까?' 카드에서 비교 기준 탭을 선택합니다.",
            "순위 목록에서 서울 전체 상권과의 순위를 확인합니다.",
          ],
          image: "/guide/district-ranking.png",
        },
        {
          title: "언제·누가·어느 요일에 소비가 많은지 알 수 있나요?",
          description:
            "언제 · 누가 · 어느 요일 카드에서 시간대·연령대·요일별 소비 패턴을 확인할 수 있습니다.",
          steps: ["시간대별·연령대별·요일별 카드를 각각 확인합니다."],
          image: "/guide/consumption-patterns.png",
        },
    ],
  },
  compare: {
    tabLabel: "비교",
    title: "비교 화면 사용법",
    items: [
      {
        title: "여러 상권을 한 화면에서 비교할 수 있나요?",
        description:
          "탐색 화면에서 담아둔 상권 중 최대 3개까지 나란히 비교표로 볼 수 있습니다.",
        steps: [
          "탐색 화면에서 상권을 비교 목록에 담습니다.",
          "헤더의 '비교' 메뉴로 이동합니다.",
        ],
        image: "/guide/compare-columns.png",
      },
      {
        title: "특정 상권을 비교표에서 빼고 싶어요.",
        description:
          "휴지통 아이콘을 클릭해 그 상권을 비교 지표에서 제외할 수 있습니다.",
        steps: ["열 상단의 휴지통 아이콘을 클릭합니다."],
        image: "/guide/compare-remove-column.png",
      },
      {
        title: "'상권 추가 (N/7)'은 무엇을 의미하나요?",
        description:
          "상권 추가 (5/7)처럼, 최대 7개까지 선택할 수 있고 지금까지 몇 개를 선택했는지를 뜻합니다.",
        steps: ["'상권 추가' 옆 숫자(N/7)로 선택한 개수를 확인합니다."],
        image: "/guide/compare-manage-districts.png",
      },
      {
        title: "비교 목록을 전체 초기화할 수 있나요?",
        description:
          "선택 초기화를 클릭하면 비교 지표 테이블이 초기화되고, 상권 추가에서 비교할 다른 상권들을 다시 선택할 수 있습니다.",
        steps: ["'선택 초기화' 버튼을 클릭합니다."],
        image: "/guide/compare-clear-selection.png",
      },
      {
        title: "각 상권의 핵심 지표는 어디서 한눈에 보나요?",
        description:
          "표의 각 행에서 탐색점수·매출·거래건수·경쟁 여건 등 핵심 지표를 한눈에 비교할 수 있습니다.",
        steps: ["비교표의 각 행을 확인합니다."],
        image: "/guide/compare-metrics-rows.png",
      },
      {
        title: "비교하던 상권의 상세 화면으로 바로 이동할 수 있나요?",
        description:
          "각 열 맨 아래 'OO 심층 보기' 버튼을 누르면 그 상권의 상세 화면으로 이동합니다.",
        steps: ["원하는 열 맨 아래 'OO 심층 보기' 버튼을 클릭합니다."],
        image: "/guide/compare-detail-action.png",
      },
    ],
  },
};

// 모달을 처음 열 때, 지금 보고 있는 화면에 맞는 탭을 기본으로 선택해둔다.
// 이후에는 탭을 직접 눌러 다른 화면의 도움말로 바로 전환할 수 있다.
function getDefaultSection(pathname: string): GuideSectionKey {
  if (pathname.startsWith("/district")) return "district";
  if (pathname.startsWith("/compare")) return "compare";
  return "explore";
}

interface PageGuideModalProps {
  open: boolean;
  onClose: () => void;
}

const FOCUSABLE_SELECTOR =
  'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';

export const PageGuideModal: React.FC<PageGuideModalProps> = ({
  open,
  onClose,
}) => {
  const location = useLocation();
  const drag = useDraggablePosition({ x: 0, y: 0 });

  // 탭: 모달을 열 때는 지금 보고 있는 화면에 맞는 탭이 기본으로 선택되고,
  // 이후에는 탭을 직접 눌러 다른 화면의 도움말로 전환할 수 있다.
  const [activeSection, setActiveSection] = useState<GuideSectionKey>(() =>
    getDefaultSection(location.pathname),
  );
  const content = GUIDE_SECTIONS[activeSection];

  // 아코디언: 한 번에 하나의 질문만 펼친다. 처음엔 첫 번째 질문이 펼쳐진 상태로 시작한다.
  const [expandedIndex, setExpandedIndex] = useState(0);
  // 화면 예시(스크린샷)는 항목별로 토글— 기본은 숨김, 질문을 바꾸면 다시 숨긴다.
  const [imageVisible, setImageVisible] = useState(false);

  const panelRef = useRef<HTMLDivElement>(null);
  const previouslyFocused = useRef<HTMLElement | null>(null);

  // 열릴 때: 중앙(오프셋 0,0)에서 다시 시작 + 현재 화면에 맞는 탭 + 첫 질문 펼침 + 내부로 포커스 이동.
  // 닫힐 때: 열기 전 포커스였던 요소로 복귀 — 배경 페이지의 키보드 포커스 흐름을 지킨다.
  useEffect(() => {
    if (open) {
      drag.setPos({ x: 0, y: 0 });
      setActiveSection(getDefaultSection(location.pathname));
      setExpandedIndex(0);
      setImageVisible(false);
      previouslyFocused.current =
        document.activeElement instanceof HTMLElement
          ? document.activeElement
          : null;
      // 모달 DOM이 그려진 다음 프레임에 포커스를 넣는다.
      const id = window.requestAnimationFrame(() => {
        panelRef.current?.focus();
      });
      return () => window.cancelAnimationFrame(id);
    }

    previouslyFocused.current?.focus();
    previouslyFocused.current = null;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  // Escape로 닫기 + Tab을 모달 내부로 가둔다(배경 페이지로 포커스가 새지 않도록).
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.stopPropagation();
        onClose();
        return;
      }
      if (e.key !== "Tab") return;

      const focusable = panelRef.current?.querySelectorAll<HTMLElement>(
        FOCUSABLE_SELECTOR,
      );
      if (!focusable || focusable.length === 0) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];

      // 열리자마자는 패널 컨테이너 자체(tabIndex=-1)가 포커스를 갖고 있어 focusable
      // 목록에는 없다 — 그 상태에서 Shift+Tab을 눌러도 모달을 벗어나지 않도록 함께 처리한다.
      const atStart =
        document.activeElement === first ||
        document.activeElement === panelRef.current;

      if (e.shiftKey && atStart) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [open, onClose]);

  if (!open) return null;

  const toggleItem = (idx: number) => {
    setImageVisible(false);
    setExpandedIndex((current) => (current === idx ? -1 : idx));
  };

  const handleTabClick = (key: GuideSectionKey) => {
    setActiveSection(key);
    setExpandedIndex(0);
    setImageVisible(false);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div
        ref={panelRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="page-guide-title"
        tabIndex={-1}
        className="bg-[#f5f5f0] border-2 border-black w-full max-w-lg sm:max-w-xl max-h-[85vh] flex flex-col shadow-[3px_3px_0px_0px_rgba(0,0,0,0.2)] focus:outline-none"
        style={{
          transform: `translate(${drag.pos.x}px, ${drag.pos.y}px)`,
        }}
      >
        <div
          onMouseDown={drag.onMouseDown}
          className="flex items-center justify-between border-b border-black p-4 sm:p-6 sm:pb-4 cursor-move select-none shrink-0"
        >
          <h3
            id="page-guide-title"
            className="font-extrabold text-lg flex items-center gap-2"
          >
            <span className="bg-[#d4ff00] text-black px-2 py-0.5 font-mono text-xs border border-black">
              GUIDE
            </span>
            {content.title}
          </h3>
          <button
            onClick={onClose}
            onMouseDown={(e) => e.stopPropagation()}
            aria-label="도움말 닫기"
            className="p-1 hover:bg-black hover:text-white transition-colors shrink-0"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div
          role="tablist"
          aria-label="화면 선택"
          className="flex border-b border-black shrink-0 font-mono text-sm font-bold"
        >
          {(Object.keys(GUIDE_SECTIONS) as GuideSectionKey[]).map((key) => {
            const isActive = key === activeSection;
            const tabId = `guide-tab-${key}`;
            const panelId = `guide-tabpanel-${key}`;
            return (
              <button
                key={key}
                type="button"
                role="tab"
                id={tabId}
                aria-selected={isActive}
                aria-controls={panelId}
                onClick={() => handleTabClick(key)}
                onMouseDown={(e) => e.stopPropagation()}
                className={`flex-1 py-2.5 border-r border-black last:border-r-0 transition-colors ${
                  isActive
                    ? "bg-[#d4ff00] text-black"
                    : "bg-white text-gray-700 hover:bg-gray-100"
                }`}
              >
                {GUIDE_SECTIONS[key].tabLabel}
              </button>
            );
          })}
        </div>

        <div
          id={`guide-tabpanel-${activeSection}`}
          role="tabpanel"
          aria-labelledby={`guide-tab-${activeSection}`}
          className="px-4 sm:px-6 py-4 space-y-2 overflow-y-auto scrollbar-gray"
        >
          {content.items.map((item, idx) => {
            const isExpanded = expandedIndex === idx;
            const panelId = `guide-panel-${idx}`;
            const buttonId = `guide-question-${idx}`;

            return (
              <div key={item.title} className="border border-black bg-white">
                <h4>
                  <button
                    type="button"
                    id={buttonId}
                    aria-expanded={isExpanded}
                    aria-controls={panelId}
                    onClick={() => toggleItem(idx)}
                    className="w-full flex items-center justify-between gap-3 p-3 text-left font-mono text-sm font-bold text-black hover:bg-[#f5f5f0] transition-colors"
                  >
                    <span>{item.title}</span>
                    <span
                      aria-hidden="true"
                      className={`shrink-0 transition-transform ${isExpanded ? "rotate-45" : ""}`}
                    >
                      +
                    </span>
                  </button>
                </h4>

                {isExpanded && (
                  <div
                    id={panelId}
                    role="region"
                    aria-labelledby={buttonId}
                    className="border-t border-black p-3 space-y-3 font-mono text-sm text-gray-800 leading-relaxed"
                  >
                    <p>{item.description}</p>

                    <ol className="list-decimal list-inside space-y-1 text-gray-700">
                      {item.steps.map((step, stepIdx) => (
                        <li key={stepIdx}>{step}</li>
                      ))}
                    </ol>

                    {item.image && (
                      <div>
                        <button
                          type="button"
                          onClick={() => setImageVisible((v) => !v)}
                          className="px-2.5 py-1 border border-black bg-white hover:bg-black hover:text-white transition-colors text-xs font-bold"
                        >
                          {imageVisible ? "화면 예시 숨기기" : "화면 예시 보기"}
                        </button>

                        {imageVisible && (
                          <img
                            src={item.image}
                            alt={`${item.title} 화면 예시`}
                            className="mt-2 border border-black max-w-full h-auto"
                          />
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="p-4 sm:p-6 pt-3 border-t border-black shrink-0">
          <button
            onClick={onClose}
            className="w-full py-2.5 bg-black text-white font-bold text-sm hover:bg-[#d4ff00] hover:text-black border border-black transition-colors"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  );
};
