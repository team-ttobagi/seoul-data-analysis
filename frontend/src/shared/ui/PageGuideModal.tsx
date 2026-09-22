import React, { useEffect } from "react";
import { useLocation } from "react-router-dom";
import { X } from "lucide-react";
import { useDraggablePosition } from "../lib/useDraggablePosition";

interface GuideItem {
  text: string;
  // public/ 기준 경로. 있으면 텍스트 바로 아래에 그 기능을 보여주는 스크린샷을 넣는다.
  image?: string;
}

// 헤더 nav의 "?" 아이콘을 누르면 현재 보고 있는 화면(탐색/상세/비교)에 맞는
// 사용법 안내 모달을 띄운다. 화면 종류별 안내 문구는 실제 UI 기능을 그대로 요약한다.
function getGuideContent(pathname: string): {
  title: string;
  items: GuideItem[];
} {
  const isDistrictDetail = pathname.startsWith("/district");
  const isCompare = pathname.startsWith("/compare");

  if (isDistrictDetail) {
    return {
      title: "상권 상세 화면 사용법",
      items: [
        {
          text: "OVERALL INSIGHT 카드에서 이 상권의 종합 SCORE와 AI 인사이트 요약을 확인합니다.",
          image: "/guide/overview-score.png",
        },
        {
          text: "경쟁은 어떨까? 카드에서 매출·거래량·경쟁 여건 수준을 확인합니다.",
          image: "/guide/competition-overview.png",
        },
        {
          text: "어디가 강할까? 탭(매출/거래건수/성장률/탐색점수)으로 서울 전체 상권과의 순위를 비교합니다.",
          image: "/guide/district-ranking.png",
        },
        {
          text: "언제 · 누가 · 어느 요일 카드에서 시간대·연령대·요일별 소비 패턴을 확인합니다.",
          image: "/guide/consumption-patterns.png",
        },
        // {
        //   text: "스크롤해서 상단 정보가 헤더 밑으로 가리면, 헤더에 같은 정보가 나타납니다.",
        // },
      ],
    };
  }

  if (isCompare) {
    return {
      title: "비교 화면 사용법",
      items: [
        {
          text: "탐색 화면에서 담아둔 상권 중 최대 3개까지 나란히 비교표로 볼 수 있습니다.",
          image: "/guide/compare-columns.png",
        },
        {
          text: "휴지통 아이콘을 클릭해 비교 지표에서 제외할 수 있습니다.",
          image: "/guide/compare-remove-column.png",
        },
        {
          text: "상권 추가 (5/7) : 최대 7개까지 선택하실 수 있고, 현재 5개 상권을 선택했다는 뜻입니다.",
          image: "/guide/compare-manage-districts.png",
        },
        {
          text: "선택 초기화를 클릭하시면 비교 지표 테이블이 초기화 되고 상권 추가에서 비교할 다른 상권들을 다시 선택 하실 수 있습니다.",
          image: "/guide/compare-clear-selection.png",
        },
        {
          text: "표의 각 행에서 탐색점수·매출·거래건수·경쟁 여건 등 핵심 지표를 한눈에 비교합니다.",
          image: "/guide/compare-metrics-rows.png",
        },
        // {
        //   text: "데이터를 불러오는 동안 화면 중앙에 로딩 표시가 뜨고, 각 셀에는 스켈레톤이 나타납니다.",
        // },
        {
          text: "각 열 맨 아래 'OO 심층 보기' 버튼을 누르면 그 상권의 상세 화면으로 이동합니다.",
          image: "/guide/compare-detail-action.png",
        },
      ],
    };
  }

  return {
    title: "탐색 화면 사용법",
    items: [
      {
        text: "상단 필터바에서 지역 · 업종 · 분기를 선택하면 추천 상권 리스트가 바뀝니다.",
        image: "/guide/search.png",
      },
      {
        text: "'상권 검색'에 이름을 입력하면 목록을 바로 좁혀서 찾을 수 있습니다.",
        image: "/guide/search-dropdown.png",
      },
      // { text: "오른쪽 '추천 기준' 패널에서 이 리스트가 매출 성장(40%)·거래량(35%)·경쟁 여건(25%) 가중치로 산출된다는 걸 확인할 수 있습니다." },
      {
        text: "카드를 클릭하면 그 상권의 상세 화면으로 이동합니다.",
        image: "/guide/explore-card-click.png",
      },
      {
        text: "카드의 '비교함에 담기'를 누르면 최대 7개 상권을 비교 목록에 저장할 수 있습니다.",
        image: "/guide/explore-card-compare-toggle.png",
      },
      {
        text: "헤더의 '산출 로직' 버튼으로 SCORE 산출 방식을 자세히 볼 수 있습니다.",
        image: "/guide/header-methodology-button.png",
      },
      {
        text: "헤더의 '비교' 메뉴에서 담아둔 상권 개수를 바로 확인할 수 있습니다.",
        image: "/guide/header-compare-menu.png",
      },
    ],
  };
}

interface PageGuideModalProps {
  open: boolean;
  onClose: () => void;
}

export const PageGuideModal: React.FC<PageGuideModalProps> = ({
  open,
  onClose,
}) => {
  const location = useLocation();
  const drag = useDraggablePosition({ x: 0, y: 0 });
  const content = getGuideContent(location.pathname);

  // 열릴 때마다 항상 중앙(오프셋 0,0)에서 다시 시작한다.
  useEffect(() => {
    if (open) {
      drag.setPos({ x: 0, y: 0 });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div
        className="bg-[#f5f5f0] border-2 border-black w-full max-w-lg p-6 space-y-4 shadow-[3px_3px_0px_0px_rgba(0,0,0,0.2)]"
        style={{
          transform: `translate(${drag.pos.x}px, ${drag.pos.y}px)`,
        }}
      >
        <div
          onMouseDown={drag.onMouseDown}
          className="flex items-center justify-between border-b border-black pb-3 cursor-move select-none"
        >
          <h3 className="font-extrabold text-lg flex items-center gap-2">
            <span className="bg-[#d4ff00] text-black px-2 py-0.5 font-mono text-xs border border-black">
              GUIDE
            </span>
            {content.title}
          </h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-black hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <ul className="space-y-3 font-mono text-xs text-gray-800 max-h-[70vh] overflow-y-auto scrollbar-gray">
          {content.items.map((item, idx) => (
            <li key={idx} className="space-y-2">
              <div className="flex gap-2">
                <span className="text-gray-400 shrink-0">{"›"}</span>
                <span className="leading-relaxed">{item.text}</span>
              </div>
              {item.image && (
                <img
                  src={item.image}
                  alt=""
                  className="border border-black max-w-full"
                />
              )}
            </li>
          ))}
        </ul>

        <button
          onClick={onClose}
          className="w-full py-2.5 bg-black text-white font-bold text-sm hover:bg-[#d4ff00] hover:text-black border border-black transition-colors"
        >
          닫기
        </button>
      </div>
    </div>
  );
};
