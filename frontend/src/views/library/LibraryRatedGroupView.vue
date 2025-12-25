<template>
  <v-container class="py-10" fluid>
    <div class="library-wrapper">
      <header class="mb-6">
        <h1 class="text-h5 font-weight-bold">평가한 영화</h1>
      </header>

      <div class="rated-group-title mb-6">
        <span class="rated-score-label">{{ scoreLabel }}점 준 영화</span>
        <span class="rated-count">{{ ratedMovies.length }}</span>
      </div>

      <div v-if="libraryStore.isLoading" class="d-flex justify-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <div v-else-if="ratedMovies.length === 0" class="text-grey pa-4">
        해당 점수로 평가한 영화가 없습니다.
      </div>

      <div v-else class="rated-grid">
        <div
          v-for="movie in ratedMovies"
          :key="movie.id"
          class="rated-card"
          @click="goToDetail(movie.id)"
        >
          <div class="rated-poster">
            <div v-if="!movie.poster_path" class="poster-placeholder">
              <span class="poster-placeholder-text">NO POSTER</span>
            </div>
            <v-img
              v-else
              :src="posterUrl(movie)"
              aspect-ratio="2/3"
              cover
            >
              <template v-slot:placeholder>
                <div class="d-flex align-center justify-center fill-height">
                  <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
                </div>
              </template>
            </v-img>
          </div>
          <div class="rated-movie-title text-truncate">
            {{ movie.title }}
          </div>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useLibraryStore } from '@/stores/libraryStore';

const libraryStore = useLibraryStore();
const route = useRoute();
const router = useRouter();

const scoreKey = computed(() => Number(route.params.score));
const scoreValue = computed(() => scoreKey.value / 2);
const scoreLabel = computed(() => scoreValue.value.toFixed(1));

const ratedMovies = computed(() => {
  return libraryStore.ratedMoviesRaw
    .filter((item) => Number(item.rating) === scoreValue.value)
    .map((item) => item.movie);
});

onMounted(() => {
  if (libraryStore.ratedMoviesRaw.length === 0) {
    libraryStore.fetchRatedMovies();
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
.library-wrapper {
  --side-gap: clamp(16px, 5vw, 60px);
  max-width: 1240px;
  width: min(1240px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
}

.rated-group-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.rated-score-label {
  font-size: 1.2rem;
  font-weight: 700;
  color: #111;
}

.rated-count {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ff3b6e;
}

.rated-grid {
  display: grid;
  --rated-card-width: 114px;
  grid-template-columns: repeat(auto-fit, var(--rated-card-width));
  column-gap: 10px;
  row-gap: 16px;
  justify-content: start;
}

.rated-card {
  cursor: pointer;
  width: var(--rated-card-width);
  transition: transform 0.2s ease;
}

.rated-card:hover {
  transform: scale(1.03);
}

.rated-poster {
  border-radius: 8px;
  overflow: hidden;
}

.rated-movie-title {
  margin-top: 6px;
  font-size: 0.9rem;
  color: #333;
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
