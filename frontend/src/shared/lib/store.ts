import { create } from "zustand";

interface CompareState {
  selectedCodes: string[];
  areaNamesByCode: Record<string, string>;
  rememberAreaName: (code: string, name: string) => void;
  addDistrict: (code: string, name?: string) => void;
  removeDistrict: (code: string) => void;
  toggleDistrict: (code: string, name?: string) => void;
  clearDistricts: () => void;
  isDistrictSelected: (code: string) => boolean;
}

export const useCompareStore = create<CompareState>((set, get) => ({
  selectedCodes: [],
  areaNamesByCode: {},

  rememberAreaName: (code, name) => {
    set((state) => ({
      areaNamesByCode: {
        ...state.areaNamesByCode,
        [code]: name,
      },
    }));
  },
  addDistrict: (code: string, name?: string) => {
    const current = get().selectedCodes;
    if (current.includes(code)) return;
    if (current.length >= 7) {
      window.alert("비교 상권 트레이에 7개까지 담을 수 있습니다.");
      return;
    }
    set((state) => ({
      selectedCodes: [...current, code],
      areaNamesByCode: name
        ? { ...state.areaNamesByCode, [code]: name }
        : state.areaNamesByCode,
    }));
  },
  removeDistrict: (code: string) => {
    set((state) => {
      const { [code]: _removedName, ...remainingNames } =
        state.areaNamesByCode;

      return {
        selectedCodes: state.selectedCodes.filter((c) => c !== code),
        areaNamesByCode: remainingNames,
      };
    });
  },
  toggleDistrict: (code: string, name?: string) => {
    const { selectedCodes, addDistrict, removeDistrict } = get();
    if (selectedCodes.includes(code)) {
      removeDistrict(code);
    } else {
      addDistrict(code, name);
    }
  },
  clearDistricts: () => set({ selectedCodes: [], areaNamesByCode: {} }),
  isDistrictSelected: (code: string) => get().selectedCodes.includes(code),
}));

interface ExploreState {
  selectedDistrictCode: string;
  keyword: string;
  // 업종 카테고리/기준 분기 — 첫 진입 시에는 빈 값이라 ExplorePage 기본값(CS100010/최신 분기)이
  // 적용되지만, 사용자가 직접 선택하면 Compare 화면을 오갔다 돌아와도 그 선택이 유지된다.
  industryCode: string;
  quarterCode: string;

  setDistrict: (code: string) => void;
  setKeyword: (keyword: string) => void;
  setIndustry: (code: string) => void;
  setQuarter: (code: string) => void;
}

// 상권 상세 화면의 브레드크럼("서울 > OO > 업종 | 분기")이 스크롤로 헤더 밑에 가리면
// 헤더에 같은 내용을 그대로 노출한다. DistrictDetailPage가 IntersectionObserver로
// visible을 갱신하고, Header는 이 값을 구독해 표시 여부만 결정한다.
interface HeaderBreadcrumbState {
  breadcrumb: { pathLabel: string; quarterLabel: string } | null;
  visible: boolean;
  setBreadcrumb: (
    breadcrumb: { pathLabel: string; quarterLabel: string } | null,
  ) => void;
  setVisible: (visible: boolean) => void;
}

export const useHeaderBreadcrumbStore = create<HeaderBreadcrumbState>(
  (set) => ({
    breadcrumb: null,
    visible: false,
    setBreadcrumb: (breadcrumb) => set({ breadcrumb }),
    setVisible: (visible) => set({ visible }),
  }),
);

export const useExploreStore = create<ExploreState>((set) => ({
  selectedDistrictCode: "",
  keyword: "",
  industryCode: "",
  quarterCode: "",

  setDistrict: (code) => {
    set({
      selectedDistrictCode: code,
      keyword: "",
    });
  },

  setKeyword: (keyword) => {
    set({ keyword });
  },

  setIndustry: (code) => {
    set({ industryCode: code });
  },

  setQuarter: (code) => {
    set({ quarterCode: code });
  },
}));
