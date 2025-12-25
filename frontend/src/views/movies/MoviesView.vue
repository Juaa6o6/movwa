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
                장르
              </v-chip>
            </template>
            <v-card class="genre-menu">
              <v-list density="compact" class="genre-list">
                <v-list-item
                  v-for="genre in genres"
                  :key="genre.value"
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

      <section class="movies-section">
        <div class="section-header">
          <h2 class="text-h6 font-weight-bold">박스오피스 순위</h2>
        </div>

        <div v-if="loading.boxOffice" class="d-flex justify-center py-6">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else class="scroll-wrapper">
          <v-btn
            icon="mdi-chevron-left"
            size="small"
            class="scroll-btn left-btn elevation-3"
            @click="scrollContainer(boxOfficeRef, 'left')"
          />
          <div class="scroll-container" ref="boxOfficeRef">
            <div class="card-row">
              <div
                v-for="item in boxOfficeMovies"
                :key="item.id"
                class="movie-card boxoffice-card"
                @click="goToDetail(item.id)"
              >
                <div class="movie-poster">
                  <div v-if="item.rank" class="rank-badge">{{ item.rank }}</div>
                  <div v-if="!item.poster_path" class="poster-placeholder">
                    <span class="poster-placeholder-text">NO POSTER</span>
                  </div>
                  <v-img v-else :src="posterUrl(item)" aspect-ratio="2/3" cover />
                </div>
                <div class="movie-title text-truncate">{{ item.title }}</div>
                <div class="movie-meta">{{ formatReleaseYear(item.release_date) }} · {{ formatLanguage(item.original_language) }} · {{ formatGenre(item.genres) }}</div>
                <div class="movie-rating">평균 ★ {{ formatRating(item.vote_average) }}</div>
              </div>
            </div>
          </div>
          <v-btn
            icon="mdi-chevron-right"
            size="small"
            class="scroll-btn right-btn elevation-3"
            @click="scrollContainer(boxOfficeRef, 'right')"
          />
        </div>
      </section>

      <section class="movies-section">
        <div class="section-header">
          <h2 class="text-h6 font-weight-bold">개봉 예정 영화</h2>
        </div>

        <div v-if="loading.upcoming" class="d-flex justify-center py-6">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else class="scroll-wrapper">
          <v-btn
            icon="mdi-chevron-left"
            size="small"
            class="scroll-btn left-btn elevation-3"
            @click="scrollContainer(upcomingRef, 'left')"
          />
          <div class="scroll-container" ref="upcomingRef">
            <div class="card-row">
              <div
                v-for="movie in upcomingMovies"
                :key="movie.id"
                class="movie-card"
                @click="goToDetail(movie.id)"
              >
                <div class="movie-poster">
                  <div v-if="!movie.poster_path" class="poster-placeholder">
                    <span class="poster-placeholder-text">NO POSTER</span>
                  </div>
                  <v-img v-else :src="posterUrl(movie)" aspect-ratio="2/3" cover />
                </div>
                <div class="movie-title text-truncate">{{ movie.title }}</div>
                <div class="movie-meta">{{ formatReleaseDate(movie.release_date) }}</div>
              </div>
            </div>
          </div>
          <v-btn
            icon="mdi-chevron-right"
            size="small"
            class="scroll-btn right-btn elevation-3"
            @click="scrollContainer(upcomingRef, 'right')"
          />
        </div>
      </section>

      <section class="movies-section">
        <div class="section-header">
          <h2 class="text-h6 font-weight-bold">띵작 영화</h2>
        </div>

        <div v-if="loading.topRated" class="d-flex justify-center py-6">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else class="scroll-wrapper">
          <v-btn
            icon="mdi-chevron-left"
            size="small"
            class="scroll-btn left-btn elevation-3"
            @click="scrollContainer(topRatedRef, 'left')"
          />
          <div class="scroll-container" ref="topRatedRef">
            <div class="card-row">
              <div
                v-for="movie in topRatedMovies"
                :key="movie.id"
                class="movie-card"
                @click="goToDetail(movie.id)"
              >
                <div class="movie-poster">
                  <div v-if="!movie.poster_path" class="poster-placeholder">
                    <span class="poster-placeholder-text">NO POSTER</span>
                  </div>
                  <v-img v-else :src="posterUrl(movie)" aspect-ratio="2/3" cover />
                </div>
                <div class="movie-title text-truncate">{{ movie.title }}</div>
                <div class="movie-meta">{{ formatReleaseYear(movie.release_date) }} · {{ formatLanguage(movie.original_language) }} · {{ formatGenre(movie.genres) }}</div>
                <div class="movie-rating">평균 ★ {{ formatRating(movie.vote_average) }}</div>
              </div>
            </div>
          </div>
          <v-btn
            icon="mdi-chevron-right"
            size="small"
            class="scroll-btn right-btn elevation-3"
            @click="scrollContainer(topRatedRef, 'right')"
          />
        </div>
      </section>
    </div>
  </v-container>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue';
import { useRouter } from 'vue-router';
import moviesApi from '@/api/moviesApi';

const router = useRouter();
const boxOfficeRef = ref(null);
const upcomingRef = ref(null);
const topRatedRef = ref(null);

const loading = reactive({
  boxOffice: false,
  upcoming: false,
  topRated: false,
});

const boxOfficeMovies = ref([]);
const upcomingMovies = ref([]);
const topRatedMovies = ref([]);
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
const selectedSortLabel = computed(() => {
  const match = sortOptions.find((option) => option.value === selectedSort.value);
  return match?.label || '인기순';
});

const fetchBoxOffice = async () => {
  loading.boxOffice = true;
  try {
    const res = await moviesApi.getBoxOffice();
    const results = res.data?.results || [];
    boxOfficeMovies.value = results
      .map((item) => ({
        ...(item.movie || item),
        rank: item.rank,
      }))
      .filter((movie) => movie?.id);
  } catch (error) {
    console.error(error);
  } finally {
    loading.boxOffice = false;
  }
};

const fetchUpcoming = async () => {
  loading.upcoming = true;
  try {
    const res = await moviesApi.getUpcomingMovies();
    upcomingMovies.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.upcoming = false;
  }
};

const fetchTopRated = async () => {
  loading.topRated = true;
  try {
    const res = await moviesApi.getTopRatedMovies();
    topRatedMovies.value = Array.isArray(res.data) ? res.data : [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.topRated = false;
  }
};

onMounted(() => {
  fetchBoxOffice();
  fetchUpcoming();
  fetchTopRated();
});

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

const scrollContainer = (targetRef, direction) => {
  const el = targetRef?.value ?? targetRef;
  if (!el) return;
  const scrollAmount = 420;
  el.scrollBy({ left: direction === 'left' ? -scrollAmount : scrollAmount, behavior: 'smooth' });
};

const posterUrl = (movie) => {
  if (!movie?.poster_path) return "https://via.placeholder.com/300x450?text=No+Poster";
  return `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
};

const formatReleaseYear = (dateStr) => {
  if (!dateStr) return "-";
  return dateStr.split("-")[0];
};

const formatReleaseDate = (dateStr) => {
  if (!dateStr) return "-";
  return dateStr.replace(/-/g, ".");
};

const formatLanguage = (lang) => {
  if (!lang) return "-";
  const normalized = lang.toLowerCase();
  const languageMap = {
    ko: "한국",
    en: "미국",
    ja: "일본",
    zh: "중국",
    fr: "프랑스",
    de: "독일",
    es: "스페인",
  };
  return languageMap[normalized] || normalized.toUpperCase();
};

const formatGenre = (genres) => {
  if (!Array.isArray(genres) || genres.length === 0) return "-";
  return genres[0];
};

const formatRating = (rating) => {
  if (rating === null || rating === undefined) return "-";
  const value = Number(rating);
  if (!Number.isFinite(value) || value <= 0) return "-";
  return value.toFixed(1);
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
  gap: 12px;
  flex-wrap: wrap;
}

.left-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tab-chip {
  min-height: 36px;
  padding: 0 12px;
  font-size: 0.95rem;
}

.genre-chip {
  min-height: 36px;
  padding: 0 12px;
  font-size: 0.95rem;
}

.genre-menu {
  background: #ffffff;
  color: #111;
  border-radius: 12px;
  min-width: 160px;
  padding: 6px 0;
}

.genre-list {
  background: transparent;
  max-height: 320px;
  overflow-y: auto;
}

.genre-text {
  color: #111;
  font-weight: 700;
}

.genre-list :deep(.v-list-item) {
  color: #111;
  font-weight: 600;
}

.genre-active {
  background: rgba(0, 0, 0, 0.06);
}

.genre-list :deep(.v-list-item:hover) {
  background: rgba(0, 0, 0, 0.06);
}

.sort-menu {
  background: #ffffff;
  color: #111;
  border-radius: 12px;
  min-width: 160px;
  padding: 6px 0;
}

.sort-list {
  background: transparent;
  max-height: 320px;
  overflow-y: auto;
}

.sort-text {
  color: #111;
  font-weight: 700;
}

.sort-active {
  background: rgba(0, 0, 0, 0.06);
}

.sort-list :deep(.v-list-item:hover) {
  background: rgba(0, 0, 0, 0.06);
}

.movies-section {
  margin-bottom: 36px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.scroll-wrapper {
  position: relative;
  width: 100%;
}

.scroll-container {
  overflow-x: auto;
  scroll-behavior: smooth;
  padding: 8px 4px 6px;
  scrollbar-width: none;
}

.scroll-container::-webkit-scrollbar {
  display: none;
}

.card-row {
  display: inline-flex;
  gap: 10px;
}

.movie-card {
  width: 238px;
  flex: 0 0 238px;
  cursor: pointer;
  transition: transform 0.2s ease;
  display: flex;
  flex-direction: column;
}

.boxoffice-card {
  width: 238px;
  flex: 0 0 238px;
}

.movie-card:hover {
  transform: scale(1.03);
}

.movie-poster {
  border-radius: 10px;
  overflow: hidden;
  aspect-ratio: 2 / 3;
  background: #2b2b2b;
  width: 100%;
  position: relative;
}

.movie-poster :deep(.v-img) {
  width: 100%;
  height: 100%;
}

.movie-title {
  margin-top: 6px;
  font-size: 0.9rem;
  color: #333;
  font-weight: 700;
  min-height: 1.2em;
}

.movie-meta {
  margin-top: 4px;
  font-size: 0.78rem;
  color: #6b7280;
  font-weight: 700;
  min-height: 1.1em;
}

.movie-rating {
  margin-top: 2px;
  font-size: 0.78rem;
  color: #6b7280;
  font-weight: 700;
  min-height: 1.1em;
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

.rank-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  font-weight: 900;
  font-size: 0.9rem;
  padding: 3px 10px;
  border-radius: 6px;
  z-index: 1;
}

.scroll-btn {
  position: absolute;
  z-index: 10;
  top: 45%;
  transform: translateY(-50%);
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #000 !important;
  opacity: 0;
  transition: opacity 0.3s;
}

.scroll-wrapper:hover .scroll-btn {
  opacity: 1;
}

.left-btn { left: -18px; }
.right-btn { right: -18px; }

@media (max-width: 1200px) {
  .left-btn { left: 6px; }
  .right-btn { right: 6px; }
}
</style>
