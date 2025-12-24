// src/stores/libraryStore.js
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import libraryApi from '@/api/libraryApi';

// [테스트 모드]
const USE_MOCK_DATA = true;

export const useLibraryStore = defineStore('library', () => {
  const savedMovies = ref([]);
  const ratedMoviesRaw = ref([]);
  const isLoading = ref(false);

  // --- [Mock Data: 다양한 점수와 포스터 추가] ---
  const mockSavedData = [
    { id: 101, title: '오징어 게임', poster_path: '/d9uzSlOqC9y95V77P187j4K71k.jpg', release_date: '2021-09-17' },
    { id: 102, title: '기생충', poster_path: '/7TuXkF8a2t57T1a7fXk59u5r7.jpg', release_date: '2019-05-30' },
    { id: 104, title: '인셉션', poster_path: '/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg', release_date: '2010-07-16' },
    { id: 105, title: '인터스텔라', poster_path: '/gEU2QniL6E8ahDaX06e8q288KZD.jpg', release_date: '2014-11-06' },
  ];

  const mockRatedData = [
    // 5??    { movie: { id: 201, title: '쇼생크 탈출', poster_path: '/q6y0Go1r1rFOpT97fT1.jpg' }, rating: 5.0 },
    
    // 4점대 (4.5, 4.0)
    { movie: { id: 204, title: '펄프 픽션', poster_path: '/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg' }, rating: 4.5 },
    { movie: { id: 206, title: '매트릭스', poster_path: '/f89U3ADr1tn54VDArZBiTxxpoe.jpg' }, rating: 4.0 },

    // 3점대 (3.5, 3.0)
    { movie: { id: 207, title: '테넷', poster_path: '/k68nPLbISTURPC96kLaGTrG6mH.jpg' }, rating: 3.5 },
    
    // 2점대 (2.5, 2.0)
    { movie: { id: 208, title: '망작1', poster_path: null }, rating: 2.5 }, 
    
    // 1점대
    { movie: { id: 209, title: '망작2', poster_path: null }, rating: 1.0 },
  ];
  // --- [Mock Data 끝] ---


  // [핵심 변경] 점수대별 그룹화 로직
  const ratedMoviesGrouped = computed(() => {
    // 1. ?????? ????????(5, 4, 3, 2, 1, 0)
    const groups = [
      { score: 5, label: '5.0 ??????', list: [] },
      { score: 4, label: '4???? (4.0 ~ 4.5)', list: [] },
      { score: 3, label: '3???? (3.0 ~ 3.5)', list: [] },
      { score: 2, label: '2???? (2.0 ~ 2.5)', list: [] },
      { score: 1, label: '1???? (1.0 ~ 1.5)', list: [] },
      { score: 0, label: '0???? (0.0 ~ 0.5)', list: [] },
    ];

    // 2. ?????????????
    ratedMoviesRaw.value.forEach(item => {
      const rating = parseFloat(item.rating);
      // Math.floor(4.5) -> 4, Math.floor(5.0) -> 5
      const groupIndex = 5 - Math.floor(rating); // 5???? index 0, 4???? index 1...

      if (groups[groupIndex]) {
        groups[groupIndex].list.push(item.movie);
      }
    });

    // 3. ??????????? ?????? ????? (?????????? ?????????????? ??????????? ??????????????????????????)
    return groups.filter(g => g.list.length > 0);
  });
  const fetchSavedMovies = async () => {
    isLoading.value = true;
    try {
      if (USE_MOCK_DATA) {
        setTimeout(() => { savedMovies.value = mockSavedData; isLoading.value = false; }, 500);
      } else {
        const res = await libraryApi.getSavedMovies();
        savedMovies.value = res.data;
        isLoading.value = false;
      }
    } catch (err) {
      console.error(err);
      isLoading.value = false;
    }
  };

  const fetchRatedMovies = async () => {
    isLoading.value = true;
    try {
      if (USE_MOCK_DATA) {
        setTimeout(() => { ratedMoviesRaw.value = mockRatedData; isLoading.value = false; }, 500);
      } else {
        const res = await libraryApi.getRatedMovies();
        ratedMoviesRaw.value = res.data; 
        isLoading.value = false;
      }
    } catch (err) {
      console.error(err);
      isLoading.value = false;
    }
  };

  return { 
    savedMovies, 
    ratedMoviesRaw, 
    ratedMoviesGrouped, // 이름 변경됨 (Grouped)
    isLoading, 
    fetchSavedMovies, 
    fetchRatedMovies 
  };
});
