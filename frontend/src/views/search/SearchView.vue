<template>
  <v-container class="py-10" fluid>
    <div class="search-wrapper">
      <header class="mb-8">
        <h1 class="text-h5 font-weight-bold">
          {{ headerTitle }}
        </h1>
      </header>

      <section>
        <h2 class="text-h6 font-weight-bold mb-4">영화</h2>

        <div v-if="isLoading && movies.length === 0" class="d-flex justify-center py-6">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else-if="movies.length === 0" class="text-grey pa-4">
          검색 결과가 없습니다.
        </div>

        <div v-else class="grid-wrapper">
          <div
            v-for="movie in movies"
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
          </div>
        </div>
        <div v-if="isLoading && movies.length > 0" class="d-flex justify-center py-6">
          <v-progress-circular indeterminate color="primary" />
        </div>
        <div ref="observerTarget" class="observer-target"></div>
      </section>
    </div>
  </v-container>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import moviesApi from '@/api/moviesApi';

const route = useRoute();
const router = useRouter();

const movies = ref([]);
const isLoading = ref(false);
const page = ref(1);
const hasMore = ref(true);
const observerTarget = ref(null);
let observer;

const query = computed(() => {
  const value = route.query.q;
  return typeof value === 'string' ? value.trim() : '';
});

const headerTitle = computed(() => {
  if (!query.value) return '검색 결과';
  return `“${query.value}” 검색 결과`;
});

const fetchSearch = async (pageToLoad = 1) => {
  if (!query.value) {
    movies.value = [];
    hasMore.value = false;
    return;
  }
  if (isLoading.value) return;
  isLoading.value = true;
  try {
    const res = await moviesApi.searchMovies(query.value, 'popularity', pageToLoad);
    const data = res.data?.results ?? res.data;
    const list = Array.isArray(data) ? data : [];
    if (pageToLoad === 1) {
      movies.value = list;
    } else {
      movies.value = [...movies.value, ...list];
    }
    if (res.data?.next === null || list.length === 0) {
      hasMore.value = false;
    }
  } catch (error) {
    console.error(error);
    if (pageToLoad === 1) {
      movies.value = [];
    }
    hasMore.value = false;
  } finally {
    isLoading.value = false;
    await nextTick();
    setupObserver();
  }
};

const resetAndFetch = () => {
  page.value = 1;
  hasMore.value = true;
  fetchSearch(1);
};

watch(query, resetAndFetch, { immediate: true });

const setupObserver = () => {
  if (observer) observer.disconnect();
  observer = new IntersectionObserver((entries) => {
    const entry = entries[0];
    if (!entry?.isIntersecting || isLoading.value || !hasMore.value) return;
    page.value += 1;
    fetchSearch(page.value);
  }, { rootMargin: '200px' });

  if (observerTarget.value) {
    observer.observe(observerTarget.value);
  }
};

onMounted(setupObserver);
watch(
  () => observerTarget.value,
  (value) => {
    if (value) setupObserver();
  }
);
onBeforeUnmount(() => {
  if (observer) observer.disconnect();
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
.search-wrapper {
  --side-gap: clamp(16px, 5vw, 60px);
  max-width: 1240px;
  width: min(1240px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
}

.grid-wrapper {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 24px;
}

@media (max-width: 1200px) {
  .grid-wrapper {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .grid-wrapper {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .grid-wrapper {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
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
  border-radius: 8px;
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

.observer-target {
  width: 100%;
  height: 1px;
}
</style>
