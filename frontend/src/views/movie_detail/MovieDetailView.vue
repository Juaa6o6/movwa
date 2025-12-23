<template>
  <v-container v-if="movieStore.isLoading" class="fill-height justify-center bg-white">
    <v-progress-circular indeterminate size="64" color="primary"></v-progress-circular>
  </v-container>

  <v-container fluid v-else-if="movieStore.movie" class="pa-0 fill-height bg-white text-black">
    <v-row no-gutters class="fill-height">
      
      <v-col cols="12" md="8" class="fill-height d-flex flex-column" style="overflow-y: auto; max-height: calc(100vh - 80px);">
        
        <MovieHeroSection 
          :movie="movieStore.movie"
          :youtube-url="finalYoutubeUrl" 
        />
        
        <div class="pa-6 bg-white border-b">
          <div class="d-flex justify-space-between align-center mb-3">
            <h1 class="text-h4 font-weight-bold mr-4" style="word-break: keep-all; line-height: 1.2;">
              {{ movieStore.movie.title }}
            </h1>

            <div class="d-flex align-center gap-3 flex-shrink-0">
              <div class="d-flex align-center bg-grey-darken-3 rounded-pill px-3 py-1" style="height: 44px;">
                 <v-btn 
                  :icon="isLiked ? 'mdi-heart' : 'mdi-heart-outline'" 
                  :color="isLiked ? 'red' : 'white'"
                  variant="text" 
                  density="comfortable"
                  @click="toggleLike"
                ></v-btn>
                <div style="width: 1px; height: 16px; background-color: #555; margin: 0 8px;"></div>
                <v-btn 
                  icon="mdi-share-variant-outline" 
                  color="white" 
                  variant="text" 
                  density="comfortable"
                  @click="shareMovie"
                ></v-btn>
              </div>

              <v-btn 
                :prepend-icon="isSaved ? 'mdi-check' : 'mdi-bookmark-outline'"
                :color="isSaved ? 'primary' : 'black'"
                :variant="isSaved ? 'flat' : 'outlined'"
                class="px-5 font-weight-bold"
                rounded="pill"
                height="44"
                @click="toggleSave"
              >
                {{ isSaved ? '보관됨' : '보관하기' }}
              </v-btn>
            </div>
          </div>

          <div class="d-flex align-center text-body-2 text-grey-darken-2">
             <v-icon icon="mdi-star" color="amber" size="small" class="mr-1 pb-1"></v-icon>
             <span class="text-black font-weight-bold mr-2">{{ movieStore.movie.vote_average?.toFixed(1) }}</span>
             <span class="text-grey-lighten-2 mx-2">|</span>
             <span>{{ movieStore.movie.release_date?.split('-')[0] }}</span>
             <span class="text-grey-lighten-2 mx-2">|</span>
             <span class="text-truncate" style="max-width: 250px;">
               {{ movieStore.movie.genres?.map(g => g.name || g).join(', ') }}
             </span>
             <span class="text-grey-lighten-2 mx-2">|</span>
             <span v-if="movieStore.movie.runtime">{{ movieStore.movie.runtime }}분</span>
          </div>
        </div>

        <v-container class="pa-6 pb-0">
          <MovieMainContent 
            :movie="movieStore.movie"
            :cast-list="movieStore.castList"
            :crew-list="movieStore.crewList" 
          />
        </v-container>
<!-- //나중에 관련영상 수정하기*/ -->
        <v-container class="pa-6" v-if="relatedVideos.length > 0">
          <h3 class="text-h5 font-weight-bold mb-4">관련 영상</h3>
          <v-row>
            <v-col cols="12" sm="6" md="3" v-for="video in relatedVideos" :key="video.id">
              <v-card @click="playRelatedVideo(video.key)" class="cursor-pointer" hover rounded="lg" elevation="2">
                <v-img 
                  :src="`https://img.youtube.com/vi/${video.key}/mqdefault.jpg`" 
                  aspect-ratio="16/9" 
                  cover
                >
                  <div class="d-flex fill-height align-center justify-center">
                    <v-icon icon="mdi-play-circle" size="48" color="rgba(255,255,255,0.8)"></v-icon>
                  </div>
                </v-img>
                <v-card-text class="pa-2 text-caption text-truncate font-weight-medium">
                  {{ video.name }}
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
        </v-col>

      <v-col cols="12" md="4" class="fill-height bg-grey-lighten-5" style="border-left: 1px solid #e0e0e0; height: calc(100vh - 80px);">
        <MovieRightPanel 
          :movie="movieStore.movie" 
          @open-review-dialog="showReviewDialog = true"
        />
      </v-col>

    </v-row>

    <MovieReviewDialog 
      v-model:show="showReviewDialog"
      @submit="handleReviewSubmit"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'; // ✅ computed 추가 완료
import { useRoute } from 'vue-router';
import { useMovieStore } from '@/stores/movieStore';

import MovieHeroSection from '@/components/movie/MovieHeroSection.vue';
import MovieMainContent from '@/components/movie/MovieMainContent.vue';
import MovieRightPanel from '@/components/movie/MovieRightPanel.vue';
import MovieReviewDialog from '@/components/movie/MovieReviewDialog.vue'; // ✨ 추가

const route = useRoute();
const movieStore = useMovieStore();

// ✨ 추가된 상태 변수들
const isLiked = ref(false);
const isSaved = ref(false);
const showReviewDialog = ref(false); // ✨ 팝업 상태 추가

// [리뷰 등록 처리 함수 추가]
const handleReviewSubmit = (reviewData) => {
  console.log('등록할 리뷰:', reviewData);
  // 여기에 Django 백엔드 API 서버로 POST 요청을 보내는 코드가 들어갑니다.
  alert('리뷰가 등록되었습니다!');
};

// ✨ 유튜브 URL 자동재생 처리 (computed로 해결)
const finalYoutubeUrl = computed(() => {
  const url = movieStore.youtubeUrl;
  if (!url) return '';
  // 이미 autoplay가 있으면 그대로 리턴
  if (url.includes('autoplay=1')) return url;
  
  // URL에 ?가 이미 있는지 확인하여 연결 문자 결정
  const separator = url.includes('?') ? '&' : '?';
  return `${url}${separator}autoplay=1&mute=1&controls=1&modestbranding=1&rel=0`;
});

// ✨ 관련 영상 4개 가져오기
const relatedVideos = computed(() => {
  if (!movieStore.movie?.videos?.results) return [];
  // YouTube 영상만 필터링 -> 상위 4개 자르기
  return movieStore.movie.videos.results
    .filter(v => v.site === 'YouTube')
    .slice(0, 4);
});

const loadData = (id) => {
  if (id) {
    movieStore.fetchMovieDetail(id);
    isLiked.value = false; 
    isSaved.value = false;
  }
};

// ✨ 버튼 기능 함수들
const toggleLike = () => { isLiked.value = !isLiked.value; };
const toggleSave = () => { isSaved.value = !isSaved.value;};

const shareMovie = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    alert('주소가 복사되었습니다! 🔗');
  } catch (err) {
    console.error('복사 실패', err);
  }
};

/// 관련 영상 클릭 시 재생
const playRelatedVideo = (videoKey) => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  // store의 url을 업데이트하면 finalYoutubeUrl도 자동으로 반응합니다.
  movieStore.youtubeUrl = `https://www.youtube.com/embed/${videoKey}`;
};

onMounted(() => loadData(route.params.id));
watch(() => route.params.id, (newId) => loadData(newId));

</script>

<style scoped>
.gap-3 { gap: 12px; }
</style>