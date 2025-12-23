<template>
  <div v-if="movies.length === 0" class="text-center text-grey py-10">
    아직 '좋아요'한 영화가 없습니다.
  </div>

  <v-row v-else dense>
    <v-col
      v-for="movie in movies"
      :key="movie.id"
      cols="6"
      sm="4"
      md="2"
      lg="2"
    >
      <v-card
        class="movie-card rounded-0 cursor-pointer"
        flat
        @click="goToDetail(movie.id)"
      >
        <v-img
          :src="posterUrl(movie)"
          aspect-ratio="2/3"
          cover
          class="bg-grey-darken-4"
        >
          <template v-slot:placeholder>
            <div class="d-flex align-center justify-center fill-height">
              <v-progress-circular indeterminate color="grey-lighten-4" />
            </div>
          </template>
          
          <div class="hover-overlay d-flex align-end pa-2">
              <span class="text-white text-caption font-weight-bold text-truncate">
                  {{ movie.title }}
              </span>
          </div>
        </v-img>
      </v-card>
    </v-col>
  </v-row>
</template>

<script setup>
import { useRouter } from 'vue-router';

defineProps({
  movies: { type: Array, default: () => [] },
});

const router = useRouter();

const posterUrl = (m) => {
  if (!m?.poster_path) return "https://via.placeholder.com/300x450?text=No+Poster";
  // 해상도를 조금 높임 (w500)
  return `https://image.tmdb.org/t/p/w500${m.poster_path}`;
};

const goToDetail = (id) => {
  router.push(`/movie/${id}`);
};
</script>

<style scoped lang="scss">
.movie-card {
  transition: transform 0.2s ease-in-out;
  position: relative;
  
  /* 호버 효과 */
  &:hover {
    transform: scale(1.03);
    z-index: 2;
    
    .hover-overlay {
        opacity: 1;
    }
  }
}

/* 기본적으로 오버레이 숨김 */
.hover-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(0,0,0,0.8), transparent 50%);
    opacity: 0;
    transition: opacity 0.2s;
}
</style>