import { create } from 'zustand';

type AppState = {
  selectedScenario: string | null;
  setSelectedScenario: (scenarioId: string | null) => void;
};

export const useAppStore = create<AppState>((set) => ({
  selectedScenario: null,
  setSelectedScenario: (scenarioId) => set({ selectedScenario: scenarioId })
}));
