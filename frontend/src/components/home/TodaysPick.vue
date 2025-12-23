<template>
  <v-container class="mt-8">
    <h3 class="text-h5 font-weight-bold text-white mb-4">오늘의 픽 영화</h3>
    
    <v-row>
      <v-col 
        v-for="movie in movies" 
        :key="movie.id"
        cols="6" sm="4" md="2"
      >
        <v-card 
          color="teal-accent-3" 
          height="200" 
          class="d-flex align-center justify-center rounded-lg elevation-4 cursor-pointer movie-card"
          @click="$router.push(`/movie/${movie.id}`)"
        >
          <v-img 
            v-if="movie.poster_path" 
            :src="`https://image.tmdb.org/t/p/w342${movie.poster_path}`" 
            cover 
            height="100%" 
            width="100%"
            class="rounded-lg"
          >
            <template v-slot:placeholder>
              <div class="d-flex align-center justify-center fill-height bg-grey-darken-3">
                <v-progress-circular indeterminate color="teal-accent-3"></v-progress-circular>
              </div>
            </template>
          </v-img>
          
          <span v-else class="text-white font-weight-bold px-2 text-center">
            {{ movie.title }}
          </span>
        </v-card>
      </v-col>
      
      <v-col v-if="!movies || movies.length === 0" cols="12">
        <div class="empty-box d-flex flex-column align-center justify-center text-grey">
          <v-icon size="48" class="mb-2 opacity-50">mdi-heart-off-outline</v-icon>
          <p>아직 '좋아요'한 영화가 없습니다.</p>
          <p class="text-caption">마음에 드는 영화에 LIKE를 눌러보세요!</p>
        </div>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
// Props 정의
const props = defineProps({
  movies: {
    type: Array,
    // ✨ 핵심: 데이터가 안 넘어왔을 때를 대비해 빈 배열을 기본값으로 설정
    default: () => [] 
  }
});
</script>

<style scoped>
.movie-card {
  transition: transform 0.2s;
}
.movie-card:hover {
  transform: translateY(-5px);
}
.empty-box {
  min-height: 200px;
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}
</style>