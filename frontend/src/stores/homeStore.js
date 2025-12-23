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
      recList.value = recList.value.map(m => ({ ...m, status: null }));
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
    // 상태 교체: pass
    currentMovie.value.status = 'passed';
    
    // 오늘의 픽에 있다면 제거
    removeFromPicks(currentMovie.value.id);
    
    // PASS는 다음 영화로 넘김
    setTimeout(() => next(), 300);
  };

  // 2. LIKE
  const likeCurrentMovie = async () => {
    if (!currentMovie.value) return;
    
    // 토글 로직: 이미 liked면 취소, 아니면 liked로 변경
    const isAlready = currentMovie.value.status === 'liked';
    currentMovie.value.status = isAlready ? null : 'liked';

    if (!isAlready) {
        addToPicks(currentMovie.value);
    } else {
        removeFromPicks(currentMovie.value.id);
    }
    
    // LIKE는 다음 영화로 넘김 (취향에 따라 제거 가능)
    // setTimeout(() => next(), 300); 
  };

  // 3. RATE (스크롤 제거됨)
  const rateCurrentMovie = async (rating) => {
    if (!currentMovie.value) return;
    
    // 상태 교체: rated
    currentMovie.value.status = 'rated';
    currentMovie.value.rating = rating;
    
    // 오늘의 픽에서는 제거 (평가함으로 이동한다고 가정)
    removeFromPicks(currentMovie.value.id);

    console.log(`Rate: ${rating}점 저장 -> 상태 변경됨`);
    // ❗ 여기있던 next()를 제거했습니다. (가로 스크롤 안 함)
  };

  // 4. SAVE (상호 배타적 적용)
  const saveCurrentMovie = async () => {
    if (!currentMovie.value) return;
    
    // 토글 로직
    const isAlready = currentMovie.value.status === 'saved';
    currentMovie.value.status = isAlready ? null : 'saved';
    
    // 저장된 영화는 오늘의 픽에서는 제외(성격이 다르므로)하거나 유지
    removeFromPicks(currentMovie.value.id);
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
    passCurrentMovie, likeCurrentMovie, rateCurrentMovie, saveCurrentMovie, toggleMute
  };
});