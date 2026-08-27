<template>
  <div class="d-flex flex-column fill-height bg-white text-black">
    
    <v-tabs
      v-model="tab"
      color="black"
      align-tabs="center"
      bg-color="grey-lighten-4"
      class="border-b"
    >
      <v-tab :value="1" class="text-body-1 font-weight-bold">리뷰</v-tab>
      <v-tab :value="2" class="text-body-1 font-weight-bold">추천 콘텐츠</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="flex-grow-1" style="overflow-y: auto;">
      
      <v-window-item :value="1" class="pa-4">
        <v-btn 
          block 
          color="primary" 
          class="mb-4" 
          size="large" 
          variant="flat" 
          elevation="0"
          @click="$emit('open-review-dialog')" 
        >
          <v-icon start>mdi-pencil</v-icon>
          {{ reviewActionLabel }}
        </v-btn>

        <div v-if="movie?.reviews?.length > 0">
          <v-card
            v-for="review in movie.reviews"
            :key="review.id"
            color="white" 
            class="mb-3 pa-3 border"
            variant="flat"
          >
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="d-flex align-center">
                <v-avatar color="grey-lighten-2" size="24" class="mr-2">
                  <img
                    v-if="getProfileImageUrl(review)"
                    :src="getProfileImageUrl(review)"
                    alt="profile"
                  />
                  <v-icon v-else size="16" color="grey-darken-2">mdi-account</v-icon>
                </v-avatar>
                <span class="font-weight-bold text-subtitle-2 text-black">{{ getReviewerName(review) }}</span>
              </div>
              <v-rating
                :model-value="review.rating"
                color="amber"
                density="comfortable"
                size="22"
                readonly
                half-increments
                class="review-rating"
              ></v-rating>
            </div>
            <p class="text-body-2 text-grey-darken-3">{{ review.content }}</p>
            <div class="review-footer">
              <div class="review-actions">
                <v-btn
                  size="small"
                  variant="tonal"
                  class="like-btn"
                  :class="{ 'is-disabled': isOwnReview(review) }"
                  :disabled="isOwnReview(review)"
                  @click="toggleReviewLike(review)"
                >
                  <v-icon
                    :icon="review.is_liked ? 'mdi-thumb-up' : 'mdi-thumb-up-outline'"
                    size="14"
                  ></v-icon>
                  <span>{{ review.like_count ?? 0 }}</span>
                </v-btn>
              </div>
              <div class="review-date">{{ formatDate(review.created_at) }}</div>
            </div>
          </v-card>
        </div>

        <div v-else class="text-center py-10 text-grey">
          <v-icon size="40" class="mb-2 text-grey-lighten-1">mdi-comment-outline</v-icon>
          <p>아직 작성된 리뷰가 없습니다.<br>첫 번째 리뷰를 남겨보세요!</p>
        </div>
      </v-window-item>

      <v-window-item :value="2" class="pa-4">
        <div v-if="relatedVideos?.length > 0">
          <v-row dense>
            <v-col cols="6" v-for="video in relatedVideos" :key="video.video_id">
              <v-card
                :href="`https://www.youtube.com/watch?v=${video.video_id}`"
                target="_blank"
                color="grey-lighten-4"
                class="border"
                hover
                flat
              >
                <v-img
                  :src="video.thumbnail"
                  height="110"
                  cover
                >
                  <template #error>
                    <div class="d-flex align-center justify-center fill-height bg-grey-lighten-3">
                      <v-icon color="grey">mdi-play-circle-outline</v-icon>
                    </div>
                  </template>
                </v-img>
                <v-card-text class="pa-2">
                  <p class="text-caption text-black font-weight-medium" style="line-height:1.3; display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;">
                    {{ video.title }}
                  </p>
                  <p class="text-caption text-grey mt-1" style="overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">
                    {{ video.channel_title }}
                  </p>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </div>
        <div v-else class="text-center py-10 text-grey">
          <v-icon size="40" class="mb-2 text-grey-lighten-1">mdi-youtube</v-icon>
          <p>관련 영상을 불러오는 중이거나<br>준비된 영상이 없습니다.</p>
        </div>
      </v-window-item>

    </v-window>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import reviewsApi from '@/api/reviewsApi';
import { useAuthStore } from '@/stores/authStore';

// ✨ 부모 컴포넌트로 보낼 이벤트 정의
defineEmits(['open-review-dialog']);

defineProps({
  movie: Object,
  relatedVideos: {
    type: Array,
    default: () => []
  },
  reviewActionLabel: {
    type: String,
    default: '리뷰 남기기'
  }
});

const tab = ref(1);
const authStore = useAuthStore();
const currentUserId = computed(() => authStore.user?.id ?? authStore.user?.pk ?? null);

const getReviewerName = (review) => {
  return review.user?.nickname || review.user?.username || '사용자';
};

const formatDate = (dateValue) => {
  if (!dateValue) return '';
  const date = new Date(dateValue);
  if (Number.isNaN(date.getTime())) return '';
  return date.toLocaleDateString('ko-KR');
};

const getProfileImageUrl = (review) => {
  const url = review?.user?.profile_image_url;
  if (!url) return '';
  if (url.startsWith('http')) return url;
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
  const prefix = url.startsWith('/') ? '' : '/';
  return `${base}${prefix}${url}`;
};

const isOwnReview = (review) => {
  if (!currentUserId.value) return false;
  return review.user?.id === currentUserId.value;
};

const toggleReviewLike = async (review) => {
  if (isOwnReview(review)) return;
  try {
    const res = await reviewsApi.toggleLike(review.id);
    if (typeof res.data?.is_liked === 'boolean') {
      review.is_liked = res.data.is_liked;
    } else {
      review.is_liked = !review.is_liked;
    }
    if (typeof res.data?.like_count === 'number') {
      review.like_count = res.data.like_count;
    }
  } catch (err) {
    console.error('리뷰 좋아요 실패:', err);
  }
};
</script>

<style scoped>
:deep(.v-avatar img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.review-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 0.75rem;
  color: #9e9e9e;
}

.review-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.like-btn {
  min-width: 0;
  padding: 4px 10px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: none;
  color: #3f3f46;
}

.like-btn.is-disabled {
  opacity: 0.4;
  pointer-events: none;
}

.review-date {
  color: #9e9e9e;
}
/* ✨ 스크롤바 디자인: 화이트 테마에 맞게 밝은 회색으로 변경 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1; /* 트랙 밝게 */
}
::-webkit-scrollbar-thumb {
  background: #c1c1c1; /* 핸들(잡는 부분) 밝은 회색 */
  border-radius: 3px;
}
</style>
