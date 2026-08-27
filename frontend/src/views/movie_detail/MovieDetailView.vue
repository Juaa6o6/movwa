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
                {{ isSaved ? 'SAVED' : 'SAVE' }}
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
        
        </v-col>

      <v-col cols="12" md="4" class="fill-height bg-grey-lighten-5" style="border-left: 1px solid #e0e0e0; height: calc(100vh - 80px);">
        <MovieRightPanel
          :movie="movieStore.movie"
          :related-videos="movieStore.relatedVideos"
          :review-action-label="reviewActionLabel"
          @open-review-dialog="showReviewDialog = true"
        />
      </v-col>

    </v-row>

    <MovieReviewDialog 
      v-model:show="showReviewDialog"
      :initial-rating="userReview?.rating ?? 5.0"
      :initial-content="userReview?.content ?? ''"
      :is-edit="Boolean(userReview)"
      @submit="handleReviewSubmit"
    />
  </v-container>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'; // ✅ computed 추가 완료
import { useRoute } from 'vue-router';
import { useMovieStore } from '@/stores/movieStore';
import moviesApi from '@/api/moviesApi';
import reviewsApi from '@/api/reviewsApi';
import { useAuthStore } from '@/stores/authStore';

import MovieHeroSection from '@/components/movie/MovieHeroSection.vue';
import MovieMainContent from '@/components/movie/MovieMainContent.vue';
import MovieRightPanel from '@/components/movie/MovieRightPanel.vue';
import MovieReviewDialog from '@/components/movie/MovieReviewDialog.vue'; // ✨ 추가

const route = useRoute();
const movieStore = useMovieStore();
const authStore = useAuthStore();

// ✨ 추가된 상태 변수들
const isLiked = ref(false);
const isSaved = ref(false);
const showReviewDialog = ref(false); // ✨ 팝업 상태 추가

const currentUserId = computed(() => authStore.user?.id ?? authStore.user?.pk ?? null);
const userReview = computed(() => {
  if (!movieStore.movie?.reviews?.length || !currentUserId.value) return null;
  return movieStore.movie.reviews.find((review) => review.user?.id === currentUserId.value) || null;
});
const reviewActionLabel = computed(() => (userReview.value ? '리뷰 수정하기' : '리뷰 남기기'));

// [리뷰 등록 처리 함수 추가]
const handleReviewSubmit = async (reviewData) => {
  try {
    if (userReview.value?.id) {
      await reviewsApi.updateReview(userReview.value.id, {
        rating: reviewData.rating,
        content: reviewData.content,
        is_spoiler: false
      });
    } else {
      await reviewsApi.createReview({
        movie_id: route.params.id,
        rating: reviewData.rating,
        content: reviewData.content,
        is_spoiler: false
      });
    }
    const reviewRes = await moviesApi.getMovieReviews(route.params.id);
    if (movieStore.movie) {
      movieStore.movie.reviews = Array.isArray(reviewRes.data) ? reviewRes.data : [];
    }
  } catch (err) {
    console.error('리뷰 저장 실패:', err);
    alert('리뷰 저장에 실패했습니다. 다시 시도해주세요.');
  }
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

const loadData = async (id) => {
  if (id) {
    await movieStore.fetchMovieDetail(id);
    await syncUserLog(id);
  }
};

// ✨ 버튼 기능 함수들
const toggleLike = async () => {
  try {
    const res = await moviesApi.likeMovie(route.params.id, !isLiked.value);
    isLiked.value = res.data?.is_liked ?? !isLiked.value;
  } catch (err) {
    console.error('좋아요 처리 실패:', err);
  }
};

const toggleSave = async () => {
  try {
    const res = await moviesApi.saveMovie(route.params.id, !isSaved.value);
    isSaved.value = res.data?.is_saved ?? !isSaved.value;
  } catch (err) {
    console.error('보관하기 처리 실패:', err);
  }
};

const shareMovie = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href);
    alert('주소가 복사되었습니다! 🔗');
  } catch (err) {
    console.error('복사 실패', err);
  }
};

const syncUserLog = async (id) => {
  try {
    const res = await moviesApi.getUserMovieLogs([id]);
    const log = Array.isArray(res.data) ? res.data[0] : null;
    isLiked.value = log?.is_liked ?? false;
    isSaved.value = log?.is_saved ?? false;
  } catch (err) {
    console.error('유저 로그 조회 실패:', err);
    isLiked.value = false;
    isSaved.value = false;
  }
};

onMounted(() => loadData(route.params.id));
watch(() => route.params.id, (newId) => loadData(newId));

</script>

<style scoped>
.gap-3 { gap: 12px; }
</style>
