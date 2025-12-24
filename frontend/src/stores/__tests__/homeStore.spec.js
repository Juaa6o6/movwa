import { describe, it, expect, vi, beforeEach } from "vitest";
import { setActivePinia, createPinia } from "pinia";
import { useHomeStore } from "@/stores/homeStore";

vi.mock("@/api/moviesApi", () => ({
  default: {
    getRecommendations: vi.fn().mockResolvedValue({ data: [] }),
    getUserMovieLogs: vi.fn().mockResolvedValue({ data: [] }),
    getTodayPicks: vi.fn().mockResolvedValue({ data: [] }),
    passMovie: vi.fn().mockResolvedValue({}),
    likeMovie: vi.fn().mockResolvedValue({}),
    rateMovie: vi.fn().mockResolvedValue({}),
    deleteRate: vi.fn().mockResolvedValue({}),
    saveMovie: vi.fn().mockResolvedValue({}),
  },
}));

const makeMovie = (overrides = {}) => ({
  id: "00000000-0000-0000-0000-000000000001",
  status: null,
  rating: null,
  ...overrides,
});

describe("homeStore actions", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  it("calls deleteRate before PASS when movie has rating", async () => {
    const store = useHomeStore();
    store.recList = [makeMovie({ status: "rated", rating: 4.5 })];
    store.currentIndex = 0;

    await store.passCurrentMovie();

    const api = (await import("@/api/moviesApi")).default;
    expect(api.deleteRate).toHaveBeenCalledTimes(1);
    expect(api.passMovie).toHaveBeenCalledTimes(1);
  });

  it("calls deleteRate before LIKE when movie has rating", async () => {
    const store = useHomeStore();
    store.recList = [makeMovie({ status: "rated", rating: 4.0 })];
    store.currentIndex = 0;

    await store.likeCurrentMovie();

    const api = (await import("@/api/moviesApi")).default;
    expect(api.deleteRate).toHaveBeenCalledTimes(1);
    expect(api.likeMovie).toHaveBeenCalledTimes(1);
  });

  it("calls deleteRate before SAVE when movie has rating", async () => {
    const store = useHomeStore();
    store.recList = [makeMovie({ status: "rated", rating: 3.5 })];
    store.currentIndex = 0;

    await store.saveCurrentMovie();

    const api = (await import("@/api/moviesApi")).default;
    expect(api.deleteRate).toHaveBeenCalledTimes(1);
    expect(api.saveMovie).toHaveBeenCalledTimes(1);
  });
});
