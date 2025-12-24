// src/stores/homeStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import movieApi from '@/api/moviesApi';

export const useHomeStore = defineStore('home', () => {
  const recList = ref([]);
  const todaysPicks = ref([]);
  const currentIndex = ref(0);
  const isLoading = ref(false);
  const isMuted = ref(true);

  const currentMovie = computed(() => {
    return recList.value[currentIndex.value] || null;
  });

  const initHome = async () => {
    isLoading.value = true;
    try {
      const res = await movieApi.getRecommendations(10);
      recList.value = Array.isArray(res.data) ? res.data : (res.data.results || []);
      // 초기 status는 null
      recList.value = recList.value.map(m => ({ ...m, status: null, rating: null }));
      const movieIds = recList.value.map((m) => m.id).filter(Boolean);
      if (movieIds.length) {
        const logsRes = await movieApi.getUserMovieLogs(movieIds);
        const logs = Array.isArray(logsRes.data) ? logsRes.data : [];
        const logMap = new Map(logs.map((log) => [log.movie_id, log]));
        recList.value = recList.value.map((movie) => {
          const log = logMap.get(movie.id);
          if (!log) return movie;

          let status = null;
          if (log.rating !== null && log.rating !== undefined) {
            status = "rated";
          } else if (log.is_saved) {
            status = "saved";
          } else if (log.is_liked === true) {
            status = "liked";
          } else if (log.is_liked === false) {
            status = "passed";
          }

          return {
            ...movie,
            status,
            rating: log.rating ?? null,
          };
        });
      }

      const picksRes = await movieApi.getTodayPicks();
      todaysPicks.value = Array.isArray(picksRes.data)
        ? picksRes.data
        : (picksRes.data.results || []);
      currentIndex.value = 0;
    } catch (e) {
      console.error(e);
    } finally {
      isLoading.value = false;
    }
  };

  const selectIndex = (index) => currentIndex.value = index;

  const next = () => {
    if (!recList.value.length) return;
    currentIndex.value = (currentIndex.value + 1) % recList.value.length;
  };

  const prev = () => {
    if (!recList.value.length) return;
    currentIndex.value = (currentIndex.value - 1 + recList.value.length) % recList.value.length;
  };

  // === 액션 로직 (상호 배타적) ===

  // 1. PASS
  const passCurrentMovie = async () => {
    if (!currentMovie.value) return;
    const prevStatus = currentMovie.value.status;
    const prevRating = currentMovie.value.rating;
    const hadRating = prevRating !== null && prevRating !== undefined;

    // 상태 교체: pass (낙관적 UI)
    currentMovie.value.status = 'passed';
    currentMovie.value.rating = null;
    removeFromPicks(currentMovie.value.id);

    try {
      if (hadRating) {
        await movieApi.deleteRate(currentMovie.value.id);
      }
      await movieApi.passMovie(currentMovie.value.id);
      setTimeout(() => next(), 300);
    } catch (e) {
      console.error(e);
      currentMovie.value.status = prevStatus;
      currentMovie.value.rating = prevRating;
      if (prevStatus === 'liked') {
        addToPicks(currentMovie.value);
      }
    }
  };

  // 2. LIKE
  const likeCurrentMovie = async () => {
    if (!currentMovie.value) return;

    const prevStatus = currentMovie.value.status;
    const prevRating = currentMovie.value.rating;
    const hadRating = prevRating !== null && prevRating !== undefined;
    const isAlready = prevStatus === 'liked';
    currentMovie.value.status = isAlready ? null : 'liked';

    if (isAlready) {
      removeFromPicks(currentMovie.value.id);
    } else {
      addToPicks(currentMovie.value);
    }

    try {
      if (hadRating) {
        await movieApi.deleteRate(currentMovie.value.id);
        currentMovie.value.rating = null;
      }
      if (!isAlready && prevStatus === 'saved') {
        await movieApi.saveMovie(currentMovie.value.id, false);
      }
      await movieApi.likeMovie(currentMovie.value.id, isAlready ? null : true);
    } catch (e) {
      console.error(e);
      currentMovie.value.status = prevStatus;
      currentMovie.value.rating = prevRating;
      if (prevStatus === 'liked') {
        addToPicks(currentMovie.value);
      } else {
        removeFromPicks(currentMovie.value.id);
      }
    }
  };

  // 3. RATE (스크롤 제거됨)
  const rateCurrentMovie = async (rating) => {
    if (!currentMovie.value) return;
    if (rating == null || rating <= 0) return;
    const prevStatus = currentMovie.value.status;
    const prevRating = currentMovie.value.rating;

    currentMovie.value.status = 'rated';
    currentMovie.value.rating = rating;
    removeFromPicks(currentMovie.value.id);

    try {
      await movieApi.rateMovie(currentMovie.value.id, rating);
    } catch (e) {
      console.error(e);
      currentMovie.value.status = prevStatus;
      currentMovie.value.rating = prevRating;
      if (prevStatus === 'liked') {
        addToPicks(currentMovie.value);
      }
    }
  };

  const clearRateCurrentMovie = async () => {
    if (!currentMovie.value) return;
    const prevStatus = currentMovie.value.status;
    const prevRating = currentMovie.value.rating;

    currentMovie.value.status = null;
    currentMovie.value.rating = null;

    try {
      await movieApi.deleteRate(currentMovie.value.id);
    } catch (e) {
      console.error(e);
      currentMovie.value.status = prevStatus;
      currentMovie.value.rating = prevRating;
    }
  };

  // 4. SAVE (상호 배타적 적용)
  const saveCurrentMovie = async () => {
    if (!currentMovie.value) return;
    const prevStatus = currentMovie.value.status;
    const prevRating = currentMovie.value.rating;
    const hadRating = prevRating !== null && prevRating !== undefined;
    const isAlready = prevStatus === 'saved';
    const nextStatus = isAlready ? null : 'saved';
    currentMovie.value.status = nextStatus;
    removeFromPicks(currentMovie.value.id);

    try {
      if (hadRating) {
        await movieApi.deleteRate(currentMovie.value.id);
        currentMovie.value.rating = null;
      }
      if (!isAlready && (prevStatus === 'liked' || prevStatus === 'passed')) {
        await movieApi.likeMovie(currentMovie.value.id, null);
      }
      await movieApi.saveMovie(currentMovie.value.id, !isAlready);
    } catch (e) {
      console.error(e);
      currentMovie.value.status = prevStatus;
      currentMovie.value.rating = prevRating;
      if (prevStatus === 'liked') {
        addToPicks(currentMovie.value);
      }
    }
  };

  // 5. MUTE
  const toggleMute = () => {
    isMuted.value = !isMuted.value;
  };

  // 유틸리티
  const addToPicks = (movie) => {
    if (!todaysPicks.value.find(m => m.id === movie.id)) {
        todaysPicks.value.unshift(movie);
    }
  };
  const removeFromPicks = (movieId) => {
    todaysPicks.value = todaysPicks.value.filter(m => m.id !== movieId);
  };

  return {
    recList, todaysPicks, currentIndex, isLoading, currentMovie, isMuted,
    initHome, selectIndex, next, prev,
    passCurrentMovie, likeCurrentMovie, rateCurrentMovie, clearRateCurrentMovie,
    saveCurrentMovie, toggleMute
  };
});
