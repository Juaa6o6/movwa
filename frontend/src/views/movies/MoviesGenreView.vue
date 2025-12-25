<template>
  <v-container class="py-10" fluid>
    <div class="movies-wrapper">
      <header class="movies-header mb-10">
        <div class="left-header">
          <h1 class="text-h4 font-weight-bold">영화</h1>
          <v-menu location="bottom start" offset="8">
            <template #activator="{ props }">
              <v-chip
                v-bind="props"
                filter
                variant="outlined"
                color="primary"
                class="tab-chip genre-chip"
                append-icon="mdi-menu-down"
              >
                {{ selectedGenreLabel }}
              </v-chip>
            </template>
            <v-card class="genre-menu">
              <v-list density="compact" class="genre-list">
                <v-list-item
                  v-for="genre in genres"
                  :key="genre.value"
                  :class="{ 'genre-active': genre.value === selectedGenre }"
                  @click="goToGenre(genre)"
                >
                  <template #title>
                    <span class="genre-text">{{ genre.label }}</span>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
        </div>

        <div class="sort-wrapper">
          <v-menu location="bottom end" offset="8">
            <template #activator="{ props }">
              <v-chip
                v-bind="props"
                filter
                variant="outlined"
                color="primary"
                class="tab-chip sort-chip"
                append-icon="mdi-menu-down"
              >
                {{ selectedSortLabel }}
              </v-chip>
            </template>
            <v-card class="sort-menu">
              <v-list density="compact" class="sort-list">
                <v-list-item
                  v-for="option in sortOptions"
                  :key="option.value"
                  :class="{ 'sort-active': option.value === selectedSort }"
                  @click="selectSort(option)"
                >
                  <template #title>
                    <span class="sort-text">{{ option.label }}</span>
                  </template>
                </v-list-item>
              </v-list>
            </v-card>
          </v-menu>
        </div>
      </header>

      <div v-if="isLoading" class="d-flex justify-center py-6">
        <v-progress-circular indeterminate color="primary" />
      </div>

      <div v-else-if="filteredMovies.length === 0" class="text-grey pa-4">
        선택한 장르의 영화가 없습니다.
      </div>

      <div v-else class="grid-wrapper">
        <div class="movie-card" v-for="movie in sortedMovies" :key="movie.id" @click="goToDetail(movie.id)">
          <div class="movie-poster">
            <div v-if="!movie.poster_path" class="poster-placeholder">
              <span class="poster-placeholder-text">NO POSTER</span>
            </div>
            <v-img v-else :src="posterUrl(movie)" aspect-ratio="2/3" cover />
          </div>
          <div class="movie-title text-truncate">{{ movie.title }}</div>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import moviesApi from '@/api/moviesApi';

const route = useRoute();
const router = useRouter();

const genres = [
  { label: '영화 전체', value: null },
  { label: '모험', value: '모험' },
  { label: '판타지', value: '판타지' },
  { label: 'SF', value: 'SF' },
  { label: '애니메이션', value: '애니메이션' },
  { label: '드라마', value: '드라마' },
  { label: '공포', value: '공포' },
  { label: '액션', value: '액션' },
  { label: '로맨스', value: '로맨스' },
  { label: '코미디', value: '코미디' },
  { label: '스릴러', value: '스릴러' },
  { label: '범죄', value: '범죄' },
  { label: '다큐멘터리', value: '다큐멘터리' },
  { label: '가족', value: '가족' },
];

const sortOptions = [
  { label: '업데이트순', value: 'updated' },
  { label: '개봉일순', value: 'release' },
  { label: '인기순', value: 'popular' },
  { label: '가나다순', value: 'alpha' },
];

const selectedSort = ref('popular');
const movies = ref([]);
const isLoading = ref(false);

const selectedGenre = computed(() => decodeURIComponent(route.params.genre || ''));
const selectedGenreLabel = computed(() => {
  if (!selectedGenre.value || selectedGenre.value === 'all') return '영화 전체';
  return selectedGenre.value;
});

const fetchMovies = async () => {
  isLoading.value = true;
  try {
    const res = await moviesApi.getMoviesList(200);
    movies.value = Array.isArray(res.data?.results) ? res.data.results : (Array.isArray(res.data) ? res.data : []);
  } catch (error) {
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(fetchMovies);

const goToGenre = (genre) => {
  if (!genre.value) {
    router.push('/movies/genre/all');
    return;
  }
  const encoded = encodeURIComponent(genre.value);
  router.push(`/movies/genre/${encoded}`);
};

const selectSort = (option) => {
  selectedSort.value = option.value;
};

const selectedSortLabel = computed(() => {
  const match = sortOptions.find((option) => option.value === selectedSort.value);
  return match?.label || '인기순';
});

const filteredMovies = computed(() => {
  if (!selectedGenre.value || selectedGenre.value === 'all') return movies.value;
  return movies.value.filter((movie) => Array.isArray(movie.genres) && movie.genres.includes(selectedGenre.value));
});

const sortedMovies = computed(() => {
  const list = [...filteredMovies.value];
  switch (selectedSort.value) {
    case 'release':
      return list.sort((a, b) => (b.release_date || '').localeCompare(a.release_date || ''));
    case 'alpha':
      return list.sort((a, b) => (a.title || '').localeCompare(b.title || '', 'ko'));
    case 'popular':
      return list.sort((a, b) => (b.vote_average || 0) - (a.vote_average || 0));
    case 'updated':
    default:
      return list;
  }
});

const posterUrl = (movie) => {
  if (!movie?.poster_path) return "https://via.placeholder.com/300x450?text=No+Poster";
  return `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
};

const goToDetail = (id) => {
  router.push(`/movie/${id}`);
};
</script>

<style scoped>
.movies-wrapper {
  --side-gap: clamp(16px, 5vw, 60px);
  max-width: 1240px;
  width: min(1240px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
}

.movies-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.left-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.genre-chip,
.sort-chip {
  min-height: 36px;
  padding: 0 12px;
  font-size: 0.95rem;
}

.genre-menu,
.sort-menu {
  background: #ffffff;
  color: #111;
  border-radius: 12px;
  min-width: 160px;
  padding: 6px 0;
}

.genre-list,
.sort-list {
  background: transparent;
  max-height: 320px;
  overflow-y: auto;
}

.genre-text,
.sort-text {
  color: #111;
  font-weight: 700;
}

.genre-active,
.sort-active {
  background: rgba(0, 0, 0, 0.06);
}

.genre-list :deep(.v-list-item:hover),
.sort-list :deep(.v-list-item:hover) {
  background: rgba(0, 0, 0, 0.06);
}

.grid-wrapper {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
}

.movie-card {
  display: flex;
  flex-direction: column;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.movie-card:hover {
  transform: scale(1.02);
}

.movie-poster {
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 2 / 3;
  background: #2b2b2b;
  width: 100%;
}

.movie-title {
  margin-top: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #222;
}

.poster-placeholder {
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  background: #2b2b2b;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #cfcfcf;
  font-weight: 600;
  font-size: 0.8rem;
}

.poster-placeholder-text {
  letter-spacing: 0.08em;
}
</style>
