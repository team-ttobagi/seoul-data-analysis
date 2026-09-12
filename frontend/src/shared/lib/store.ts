import { create } from "zustand";

interface CompareState {
  selectedCodes: string[];
  areaNamesByCode: Record<string, string>;
  rememberAreaName: (code: string, name: string) => void;
  addDistrict: (code: string) => void;
  removeDistrict: (code: string) => void;
  toggleDistrict: (code: string) => void;
  clearDistricts: () => void;
  isDistrictSelected: (code: string) => boolean;
}

export const useCompareStore = create<CompareState>((set, get) => ({
  selectedCodes: ["SEONGSU", "HONGDAE", "SHAROSU"],
  areaNamesByCode: {},

  rememberAreaName: (code, name) => {
    set((state) => ({
      areaNamesByCode: {
        ...state.areaNamesByCode,
        [code]: name,
      },
    }));
  },
  addDistrict: (code: string) => {
    const current = get().selectedCodes;
    if (current.includes(code)) return;
    if (current.length >= 3) {
      set({ selectedCodes: [...current.slice(1), code] });
    } else {
      set({ selectedCodes: [...current, code] });
    }
  },
  removeDistrict: (code: string) => {
    set({ selectedCodes: get().selectedCodes.filter((c) => c !== code) });
  },
  toggleDistrict: (code: string) => {
    const { selectedCodes, addDistrict, removeDistrict } = get();
    if (selectedCodes.includes(code)) {
      removeDistrict(code);
    } else {
      addDistrict(code);
    }
  },
  clearDistricts: () => set({ selectedCodes: [] }),
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
