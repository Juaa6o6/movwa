<template>
  <v-container v-if="movieStore.isLoading" class="fill-height justify-center">
    <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
  </v-container>

  <v-container fluid class="pa-0" v-else-if="movieStore.movie">
    
    <MovieHeroSection 
      :movie="movieStore.movie"
      :youtube-url="movieStore.youtubeUrl"
    />

    <v-container class="mt-8" style="max-width: 1200px;"> <v-row>
        <v-col cols="12" md="8" lg="8">
          <MovieMainContent 
            :movie="movieStore.movie"
            :cast-list="movieStore.castList"
          />
        </v-col>

        <v-col cols="12" md="4" lg="4">
          <MovieRightPanel :movie="movieStore.movie" />
        </v-col>
      </v-row>
    </v-container>

  </v-container>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useMovieStore } from '@/stores/movieStore';

import MovieHeroSection from '@/components/movie/MovieHeroSection.vue';
import MovieMainContent from '@/components/movie/MovieMainContent.vue';
// ❗ 이름 변경 주의: MovieSideInfo -> MovieRightPanel
import MovieRightPanel from '@/components/movie/MovieRightPanel.vue'; 

const route = useRoute();
const movieStore = useMovieStore();

const loadData = (id) => {
  if (id) movieStore.fetchMovieDetail(id);
};

onMounted(() => loadData(route.params.id));
watch(() => route.params.id, (newId) => loadData(newId));
</script>