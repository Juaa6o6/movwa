<template>
  <v-card
    :class="cardClass"
    elevation="0"
    @click="goToDetail"
  >
    <v-img
      :src="posterUrl"
      aspect-ratio="2/3"
      cover
      :class="posterClass"
      bg-color="grey-lighten-2"
    >
      <template v-slot:placeholder>
        <div class="d-flex align-center justify-center fill-height">
          <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
        </div>
      </template>
    </v-img>

    </v-card>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';

// 부모 컴포넌트(LibraryView)에서 영화 객체를 받음
const props = defineProps({
  movie: {
    type: Object,
    required: true,
  },
  rounded: {
    type: Boolean,
    default: true,
  },
  center: {
    type: Boolean,
    default: true,
  },
});

const router = useRouter();

// TMDB 이미지 기본 URL (환경변수나 설정 파일로 빼는 것이 좋음)
const IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500';

const posterUrl = computed(() => {
  if (props.movie.poster_path) {
    return `${IMAGE_BASE_URL}${props.movie.poster_path}`;
  }
  return '@/assets/no-poster.png'; // 대체 이미지
});

const releaseYear = computed(() => {
  if (!props.movie.release_date) return '';
  return props.movie.release_date.split('-')[0];
});

const goToDetail = () => {
  router.push({ 
    name: 'MovieDetail', // 라우터에 정의된 상세페이지 이름
    params: { id: props.movie.id } // 또는 movie_id 등 라우터 설정에 맞게
  });
};
</script>

<style scoped>
.movie-card {
  transition: transform 0.2s;
}
.movie-card:hover {
  transform: translateY(-5px);
}
</style>