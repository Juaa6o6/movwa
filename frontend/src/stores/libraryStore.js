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
    { id: 101, title: '저장 영화 1', poster_path: null, release_date: '2021-09-17' },
    { id: 102, title: '저장 영화 2', poster_path: null, release_date: '2019-05-30' },
    { id: 103, title: '저장 영화 3', poster_path: null, release_date: '2010-07-16' },
    { id: 104, title: '저장 영화 4', poster_path: null, release_date: '2014-11-06' },
    { id: 105, title: '저장 영화 5', poster_path: null, release_date: '2019-10-02' },
    { id: 106, title: '저장 영화 6', poster_path: null, release_date: '2019-04-24' },
    { id: 107, title: '저장 영화 7', poster_path: null, release_date: '2008-07-16' },
    { id: 108, title: '저장 영화 8', poster_path: null, release_date: '2016-12-07' },
    { id: 109, title: '저장 영화 9', poster_path: null, release_date: '2010-06-16' },
    { id: 110, title: '저장 영화 10', poster_path: null, release_date: '2017-02-24' },
    { id: 111, title: '저장 영화 11', poster_path: null, release_date: '1997-12-19' },
    { id: 112, title: '저장 영화 12', poster_path: null, release_date: '2001-07-18' },
    { id: 113, title: '저장 영화 13', poster_path: null, release_date: '2003-12-05' },
    { id: 114, title: '저장 영화 14', poster_path: null, release_date: '2006-10-20' },
    { id: 115, title: '저장 영화 15', poster_path: null, release_date: '2011-03-18' },
  ];

  const mockRatedData = [
    { movie: { id: 201, title: '평가 영화 1', poster_path: null }, rating: 5.0 },
    { movie: { id: 202, title: '평가 영화 2', poster_path: null }, rating: 5.0 },
    { movie: { id: 203, title: '평가 영화 3', poster_path: null }, rating: 5.0 },
    { movie: { id: 204, title: '평가 영화 4', poster_path: null }, rating: 5.0 },
    { movie: { id: 205, title: '평가 영화 5', poster_path: null }, rating: 5.0 },
    { movie: { id: 206, title: '평가 영화 6', poster_path: null }, rating: 5.0 },
    { movie: { id: 207, title: '평가 영화 7', poster_path: null }, rating: 5.0 },
    { movie: { id: 208, title: '평가 영화 8', poster_path: null }, rating: 5.0 },
    { movie: { id: 209, title: '평가 영화 9', poster_path: null }, rating: 5.0 },
    { movie: { id: 210, title: '평가 영화 10', poster_path: null }, rating: 5.0 },
    { movie: { id: 211, title: '평가 영화 11', poster_path: null }, rating: 5.0 },
    { movie: { id: 212, title: '평가 영화 12', poster_path: null }, rating: 5.0 },
    { movie: { id: 213, title: '평가 영화 13', poster_path: null }, rating: 5.0 },
    { movie: { id: 214, title: '평가 영화 14', poster_path: null }, rating: 5.0 },
    { movie: { id: 215, title: '평가 영화 15', poster_path: null }, rating: 5.0 },
  ];
  // --- [Mock Data 끝] ---


  // [핵심 변경] 점수별(0.5 단위) 그룹화 로직
  const ratedMoviesGrouped = computed(() => {
    const scores = [5.0, 4.5, 4.0, 3.5, 3.0, 2.5, 2.0, 1.5, 1.0, 0.5];
    const groups = scores.map((score) => ({
      score,
      label: `${score.toFixed(1)} 평가함`,
      list: [],
    }));

    ratedMoviesRaw.value.forEach((item) => {
      const rating = parseFloat(item.rating);
      const group = groups.find((g) => g.score === rating);
      if (group) {
        group.list.push(item.movie);
      }
    });

    return groups.filter((g) => g.list.length > 0);
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
