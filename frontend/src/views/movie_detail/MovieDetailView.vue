<template>
  <v-container v-if="movieStore.isLoading" class="fill-height justify-center bg-black">
    <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
  </v-container>

  <v-container fluid v-else-if="movieStore.movie" class="pa-0 fill-height bg-black">
    <v-row no-gutters class="fill-height">
      
      <v-col cols="12" md="8" class="fill-height" style="overflow-y: auto; height: 100vh;">
        <MovieHeroSection 
          :movie="movieStore.movie"
          :youtube-url="movieStore.youtubeUrl"
        />
        
        <v-container class="pa-8 text-white">
          <MovieMainContent 
            :movie="movieStore.movie"
            :cast-list="movieStore.castList"
          />
        </v-container>
      </v-col>

      <v-col cols="12" md="4" class="fill-height" style="border-left: 1px solid #333; height: 100vh;">
        <MovieRightPanel 
          :movie="movieStore.movie" 
        />
      </v-col>

    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useMovieStore } from '@/stores/movieStore';

import MovieHeroSection from '@/components/movie/MovieHeroSection.vue';
import MovieMainContent from '@/components/movie/MovieMainContent.vue';
import MovieRightPanel from '@/components/movie/MovieRightPanel.vue';

const route = useRoute();
const movieStore = useMovieStore();

const loadData = (id) => {
  if (id) movieStore.fetchMovieDetail(id);
};

onMounted(() => loadData(route.params.id));
watch(() => route.params.id, (newId) => loadData(newId));
</script>