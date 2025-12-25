<template>
  <v-container class="py-10" fluid>
    <div class="library-wrapper" :class="{ 'all-tab': currentTab === 'all' }">
      <header class="mb-8">
        <h1 class="text-h4 font-weight-bold mb-4">보관함</h1>
        
        <div class="d-flex gap-2">
          <v-chip 
            filter
            :variant="currentTab === 'all' ? 'elevated' : 'outlined'"
            color="primary"
            class="tab-chip"
            @click="selectTab('all')"
          >
            전체
          </v-chip>
          <v-chip 
            filter
            :variant="currentTab === 'saved' ? 'elevated' : 'outlined'"
            color="primary"
            class="tab-chip"
            @click="selectTab('saved', 'saved-section')"
          >
            나중에 볼 영화 보관함
          </v-chip>
          <v-chip 
            filter
            :variant="currentTab === 'rated' ? 'elevated' : 'outlined'"
            color="primary"
            class="tab-chip"
            @click="selectTab('rated', 'rated-section')"
          >
            평가한 영화
          </v-chip>
        </div>
      </header>

    <section v-if="currentTab !== 'rated'" id="saved-section" class="mb-12">
      <div v-if="currentTab !== 'saved'" class="rated-header mb-4">
        <div class="rated-title">
          <h2 class="text-h5 font-weight-bold mb-3">나중에 볼 영화 보관함</h2>
        </div>
      </div>
      
      <div v-if="libraryStore.isLoading" class="d-flex justify-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <div v-else-if="libraryStore.savedMovies.length === 0" class="text-grey pa-4">
        보관된 영화가 없습니다.
      </div>

      <div v-else>
        <div v-if="currentTab === 'saved'" class="saved-grid">
          <div
            v-for="movie in libraryStore.savedMovies"
            :key="movie.id"
            class="saved-card"
            @click="goToDetail(movie.id)"
          >
            <div class="saved-poster">
              <div v-if="!movie.poster_path" class="poster-placeholder saved-placeholder">
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
            <div class="saved-movie-title text-truncate">
              {{ movie.title }}
            </div>
          </div>
        </div>

        <div v-else class="scroll-wrapper">
          <v-btn
            icon="mdi-chevron-left"
            size="small"
            class="scroll-btn left-btn elevation-3"
            @click="scrollContainer(savedScrollRef, 'left')"
          />

          <div class="scroll-container saved-scroll" ref="savedScrollRef">
            <div class="saved-row">
              <div
                v-for="movie in libraryStore.savedMovies"
                :key="movie.id"
                class="saved-card"
                @click="goToDetail(movie.id)"
              >
                <div class="saved-poster">
                  <div v-if="!movie.poster_path" class="poster-placeholder saved-placeholder">
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
                <div class="saved-movie-title text-truncate">
                  {{ movie.title }}
                </div>
              </div>
            </div>
          </div>

          <v-btn
            icon="mdi-chevron-right"
            size="small"
            class="scroll-btn right-btn elevation-3"
            @click="scrollContainer(savedScrollRef, 'right')"
          />
        </div>
      </div>
    </section>

    <v-divider v-if="currentTab === 'all'" class="mb-12"></v-divider>

    <section v-if="currentTab !== 'saved'" id="rated-section">
      <h2 v-if="currentTab !== 'rated'" class="text-h5 font-weight-bold mb-6">평가한 영화</h2>

      <div
        v-for="group in libraryStore.ratedMoviesGrouped"
        :key="group.score"
        class="rated-group"
      >
        <div class="rated-header">
          <div class="rated-title">
            <span class="rated-score">{{ group.label }}</span>
            <span class="rated-count">{{ group.list.length }}</span>
          </div>
          <v-btn
            variant="text"
            size="small"
            append-icon="mdi-chevron-right"
            @click="goToRatedGroup(group.score)"
          >
            더보기
          </v-btn>
        </div>

        <div class="scroll-wrapper rated-wrapper">
          <v-btn
            icon="mdi-chevron-left"
            size="small"
            class="scroll-btn left-btn elevation-3"
            @click="scrollRated(group.score, 'left')"
          />

          <div class="scroll-container rated-scroll" :ref="(el) => setRatedRef(group.score, el)">
            <div class="rated-row">
              <div
                v-for="movie in group.list"
                :key="movie.id"
                class="rated-card"
                @click="goToDetail(movie.id)"
              >
                <div class="rated-poster">
                  <div v-if="!movie.poster_path" class="poster-placeholder rated-placeholder">
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

          <v-btn
            icon="mdi-chevron-right"
            size="small"
            class="scroll-btn right-btn elevation-3"
            @click="scrollRated(group.score, 'right')"
          />
        </div>
      </div>
      </section>
    </div>
  </v-container>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useLibraryStore } from '@/stores/libraryStore';

const libraryStore = useLibraryStore();
const currentTab = ref('all');
const router = useRouter();
const route = useRoute();
const savedScrollRef = ref(null);
const ratedScrollRefs = new Map();

// 스크롤 이동
const scrollToSection = (id) => {
  const element = document.getElementById(id);
  if (element) {
    // 헤더 높이만큼 빼고 스크롤 (가려짐 방지)
    const headerOffset = 80;
    const elementPosition = element.getBoundingClientRect().top;
    const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

    window.scrollTo({
      top: offsetPosition,
      behavior: "smooth"
    });
  }
};

// 탭 선택
const selectTab = (tabName, sectionId) => {
  currentTab.value = tabName;
  if (sectionId) {
    nextTick(() => {
      scrollToSection(sectionId);
    });
  }
};

onMounted(() => {
  libraryStore.fetchSavedMovies();
  libraryStore.fetchRatedMovies();

  const initialTab = route.query.tab;
  if (initialTab === 'saved') {
    selectTab('saved', 'saved-section');
  } else if (initialTab === 'rated') {
    selectTab('rated', 'rated-section');
  }
});

watch(
  () => route.query.tab,
  (tab) => {
    if (tab === 'saved') {
      selectTab('saved', 'saved-section');
    } else if (tab === 'rated') {
      selectTab('rated', 'rated-section');
    } else {
      selectTab('all');
    }
  }
);

const setRatedRef = (score, el) => {
  if (!el) {
    ratedScrollRefs.delete(score);
    return;
  }
  ratedScrollRefs.set(score, el);
};

const scrollContainer = (targetRef, direction) => {
  const el = targetRef?.value ?? targetRef;
  if (!el) return;
  const scrollAmount = 420;
  if (direction === 'left') {
    el.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  } else {
    el.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  }
};

const scrollRated = (score, direction) => {
  const el = ratedScrollRefs.get(score);
  if (!el) return;
  const scrollAmount = 420;
  if (direction === 'left') {
    el.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  } else {
    el.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  }
};

const posterUrl = (movie) => {
  if (!movie?.poster_path) return "https://via.placeholder.com/300x450?text=No+Poster";
  return `https://image.tmdb.org/t/p/w500${movie.poster_path}`;
};

const goToDetail = (id) => {
  router.push(`/movie/${id}`);
};

const goToRatedGroup = (score) => {
  const scoreKey = Math.round(score * 2);
  router.push(`/library/ratings/${scoreKey}`);
};
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}

.tab-chip {
  min-height: 36px;
  padding: 0 12px;
  font-size: 0.95rem;
}

.library-wrapper {
  --side-gap: clamp(16px, 5vw, 60px);
  max-width: 1240px;
  width: min(1240px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
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
  width: 100%;
  max-width: 100%;
}

.scroll-container::-webkit-scrollbar {
  display: none;
}

.saved-row,
.rated-row {
  display: inline-flex;
  gap: var(--card-gap, 18px);
}

.saved-grid {
  display: grid;
  --saved-card-width: 114px;
  grid-template-columns: repeat(auto-fit, var(--saved-card-width));
  column-gap: 10px;
  row-gap: 30px;
  justify-content: start;
}

.saved-grid .saved-card {
  width: var(--saved-card-width);
  flex: 0 0 var(--saved-card-width);
}

.saved-scroll,
.rated-scroll {
  --card-width: 114px;
  --card-gap: 10px;
}

.saved-row {
  width: max-content;
  min-width: max-content;
}

.saved-card {
  transition: transform 0.2s ease;
  cursor: pointer;
  width: var(--card-width, 140px);
  flex: 0 0 var(--card-width, 140px);
}

.saved-card:hover {
  transform: scale(1.03);
}

.saved-poster {
  border-radius: 8px;
  overflow: hidden;
}

.saved-movie-title {
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

.saved-placeholder {
  border-radius: 8px;
  overflow: hidden;
}

.rated-placeholder {
  border-radius: 10px;
  overflow: hidden;
}

.rated-group {
  margin-bottom: 36px;
}

.rated-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}

.rated-title {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.rated-score {
  font-size: 1.25rem;
  font-weight: 700;
}

.rated-count {
  font-size: 1.25rem;
  font-weight: 700;
  color: #ff3b6e;
}

.rated-card {
  cursor: pointer;
  width: var(--card-width, 140px);
  flex: 0 0 var(--card-width, 140px);
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

.scroll-btn {
  position: absolute;
  z-index: 10;
  top: 50%;
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
