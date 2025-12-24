<template>
  <v-container class="py-10">
    <header class="mb-8">
      <h1 class="text-h4 font-weight-bold mb-4">보관함</h1>
      
      <div class="d-flex gap-2">
        <v-chip 
          filter
          :variant="currentTab === 'all' ? 'elevated' : 'outlined'"
          color="primary"
          @click="selectTab('all')"
        >
          전체
        </v-chip>
        <v-chip 
          filter
          :variant="currentTab === 'saved' ? 'elevated' : 'outlined'"
          color="primary"
          @click="selectTab('saved', 'saved-section')"
        >
          나중에 볼 영화 보관함
        </v-chip>
        <v-chip 
          filter
          :variant="currentTab === 'rated' ? 'elevated' : 'outlined'"
          color="primary"
          @click="selectTab('rated', 'rated-section')"
        >
          평가한 영화
        </v-chip>
      </div>
    </header>

    <section id="saved-section" class="mb-12">
      <h2 class="text-h5 font-weight-bold mb-4">나중에 볼 영화 보관함</h2>
      
      <div v-if="libraryStore.isLoading" class="d-flex justify-center">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>

      <div v-else-if="libraryStore.savedMovies.length === 0" class="text-grey pa-4">
        보관된 영화가 없습니다.
      </div>

      <v-row v-else justify="start">
        <v-col 
          v-for="movie in libraryStore.savedMovies" 
          :key="movie.id"
          cols="6" sm="4" md="3" lg="2" 
        >
          <MovieCard :movie="movie" :rounded="false" :center="false" />
        </v-col>
      </v-row>
    </section>

    <v-divider class="mb-12"></v-divider>

    <section id="rated-section">
      <h2 class="text-h5 font-weight-bold mb-6">평가한 영화</h2>

      <div 
        v-for="group in libraryStore.ratedMoviesGrouped" 
        :key="group.score"
        class="mb-10"
      >
        <div class="d-flex justify-space-between align-center mb-2 px-1">
          <div class="d-flex align-center">
            <span class="text-h6 font-weight-bold mr-2">{{ group.label }}</span>
          </div>
          
          <v-btn variant="text" size="small" append-icon="mdi-chevron-right">
            더보기
          </v-btn>
        </div>

        <v-slide-group show-arrows>
          <v-slide-group-item
            v-for="movie in group.list"
            :key="movie.id"
          >
            <div class="ma-2" style="width: 170px;"> 
              <MovieCard :movie="movie" :rounded="false" :center="false" />
            </div>
          </v-slide-group-item>
        </v-slide-group>
      </div>
    </section>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useLibraryStore } from '@/stores/libraryStore';
import MovieCard from '@/components/movie/MovieCard.vue';

const libraryStore = useLibraryStore();
const currentTab = ref('all');

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
    scrollToSection(sectionId);
  }
};

onMounted(() => {
  libraryStore.fetchSavedMovies();
  libraryStore.fetchRatedMovies();
});
</script>

<style scoped>
.gap-2 {
  gap: 8px;
}
</style>
