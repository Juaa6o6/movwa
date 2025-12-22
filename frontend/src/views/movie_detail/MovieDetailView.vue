<template>
  <v-container v-if="movieStore.isLoading" class="fill-height justify-center bg-white">
    <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
  </v-container>

  <v-container fluid v-else-if="movieStore.movie" class="pa-0 fill-height bg-white text-black">
    <v-row no-gutters class="fill-height">
      
      <v-col cols="12" md="8" class="fill-height d-flex flex-column" style="overflow-y: auto; max-height: calc(100vh - 80px);">
        
        <MovieHeroSection 
          :movie="movieStore.movie"
          :youtube-url="movieStore.youtubeUrl"
        />
        
        <v-container class="pa-8">
          <div class="d-flex align-start gap-6 mb-8">
             
             <v-card elevation="4" rounded="lg" width="140" class="flex-shrink-0">
               <v-img 
                  v-if="movieStore.movie.poster_path"
                  :src="getImageUrl(movieStore.movie.poster_path)"
                  aspect-ratio="2/3"
                  cover
               ></v-img>
             </v-card>
             
             <div class="pt-2">
                <h1 class="text-h4 font-weight-bold mb-2">{{ movieStore.movie.title }}</h1>
                
                <div class="d-flex align-center text-grey-darken-1 mb-3 text-body-2">
                   <span class="mr-3 font-weight-medium">{{ movieStore.movie.release_date?.split('-')[0] }}</span>
                   <v-divider vertical class="mx-2"></v-divider>
                   <span class="mr-3" v-if="movieStore.movie.runtime">{{ movieStore.movie.runtime }}분</span>
                   <v-divider vertical class="mx-2"></v-divider>
                   <span>{{ movieStore.movie.original_language?.toUpperCase() || 'KO' }}</span>
                </div>

                <div class="d-flex gap-2 mb-4">
                  <v-chip 
                    v-for="genre in movieStore.movie.genres" 
                    :key="genre.id || genre"
                    size="small" 
                    color="grey-darken-3" 
                    variant="tonal"
                    label
                  >
                    {{ genre.name || genre }}
                  </v-chip>
                </div>

                <div class="d-flex align-center">
                   <v-rating
                     :model-value="movieStore.movie.vote_average / 2"
                     color="amber-darken-2"
                     density="compact"
                     half-increments
                     readonly
                     size="small"
                   ></v-rating>
                   <span class="text-h6 font-weight-bold ml-2 text-black">
                     {{ movieStore.movie.vote_average?.toFixed(1) }}
                   </span>
                </div>
             </div>
          </div>

          <v-divider class="mb-8"></v-divider>

          <MovieMainContent 
            :movie="movieStore.movie"
            :cast-list="movieStore.castList"
          />
        </v-container>
      </v-col>

      <v-col cols="12" md="4" class="fill-height bg-grey-lighten-5" style="border-left: 1px solid #e0e0e0; height: calc(100vh - 80px);">
        <MovieRightPanel :movie="movieStore.movie" />
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

// TMDB 이미지 전체 경로 만들기 함수
const getImageUrl = (path) => {
  if (!path) return '';
  return `https://image.tmdb.org/t/p/w300${path}`; // 포스터는 너무 클 필요 없으니 w300 사용
};

const loadData = (id) => {
  if (id) movieStore.fetchMovieDetail(id);
};

onMounted(() => loadData(route.params.id));
watch(() => route.params.id, (newId) => loadData(newId));
</script>

<style scoped>
.gap-6 { gap: 24px; }
.gap-2 { gap: 8px; }
</style>