// src/stores/homeStore.js
import { defineStore } from "pinia";
import movieApi from "@/api/moviesApi";


const shuffleList = (list) => {
  const arr = [...list];
  for (let i = arr.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
};

export const useHomeStore = defineStore("home", {
  state: () => ({
    recList: [],
    currentIndex: 0,
    isLoading: false,
  }),

  getters: {
    currentMovie(state) {
      return state.recList[state.currentIndex] || null;
    },
  },

  actions: {
    // REC-01, REC-02
    async initHome() {
      this.isLoading = true;
      try {
        const res = await movieApi.getRecommendations(10);
        // 백엔드 응답 형태에 따라 둘 중 하나
        const list = Array.isArray(res.data)
          ? res.data
          : res.data.results || [];
        this.recList = shuffleList(list);
        this.currentIndex = 0;
      } catch (e) {
        console.error("홈 추천 영화 로딩 실패", e);
      } finally {
        this.isLoading = false;
      }
    },

    // 썸네일 클릭
    selectIndex(index) {
      this.currentIndex = index;
    },

    // 좌/우 이동
    next() {
      if (!this.recList.length) return;
      this.currentIndex =
        (this.currentIndex + 1) % this.recList.length;
    },

    prev() {
      if (!this.recList.length) return;
      this.currentIndex =
        (this.currentIndex - 1 + this.recList.length) %
        this.recList.length;
    },

    // REC-04 PASS
    async passCurrentMovie() {
      const movie = this.currentMovie;
      if (!movie) return;

      await movieApi.passMovie(movie.id);
      this.next();
    },

    // REC-05 LIKE
    async likeCurrentMovie() {
      const movie = this.currentMovie;
      if (!movie) return;

      await movieApi.likeMovie(movie.id, true);
      this.next();
    },

    // REC-06 RATE
    async rateCurrentMovie(rating) {
      const movie = this.currentMovie;
      if (!movie) return;

      await movieApi.rateMovie(movie.id, rating);
      this.next();
    },

    // REC-07 SAVE
    async saveCurrentMovie() {
      const movie = this.currentMovie;
      if (!movie) return;

      await movieApi.saveMovie(movie.id);
    },
  },
});
