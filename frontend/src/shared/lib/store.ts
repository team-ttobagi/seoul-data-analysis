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

  setDistrict: (code: string) => void;
  setKeyword: (keyword: string) => void;
}

export const useExploreStore = create<ExploreState>((set) => ({
  selectedDistrictCode: "",
  keyword: "",

  setDistrict: (code) => {
    set({
      selectedDistrictCode: code,
      keyword: "",
    });
  },

  setKeyword: (keyword) => {
    set({ keyword });
  },
}));
