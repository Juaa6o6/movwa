<template>
  <v-container class="py-10" fluid>
    <div class="reviews-wrapper">
      <h1 class="page-title">코멘트</h1>

      <v-tabs v-model="activeTab" class="reviews-tabs" align-tabs="start">
        <v-tab value="written">작성한 코멘트</v-tab>
        <v-tab value="liked">좋아요한 코멘트</v-tab>
      </v-tabs>

      <v-window v-model="activeTab" class="reviews-window">
        <v-window-item value="written">
          <div v-if="loading" class="state-text">불러오는 중...</div>
          <div v-else-if="error" class="state-text error">{{ error }}</div>
          <div v-else>
            <div v-if="reviews.length === 0" class="state-text empty">
              작성한 코멘트가 없습니다.
            </div>
            <div v-else class="review-list">
              <article v-for="review in reviews" :key="review.id" class="review-card">
                <div class="review-header">
                  <div class="review-user">
                    <div class="user-icon">
                      <img
                        v-if="review.user?.profile_image_url"
                        :src="review.user.profile_image_url"
                        alt="profile"
                      />
                      <v-icon v-else icon="mdi-account" size="18" color="grey-darken-1"></v-icon>
                    </div>
                    <div class="user-name">
                      {{ review.user?.nickname || authStore.user?.nickname || authStore.user?.username || "사용자" }}
                    </div>
                  </div>
                  <div class="review-rating">
                    <v-icon icon="mdi-star" size="16" color="amber-darken-2"></v-icon>
                    <span>{{ formatRating(review.rating) }}</span>
                  </div>
                </div>

                <div class="review-body">
                  <div class="review-poster">
                    <img v-if="review.movie?.poster_path" :src="getPosterUrl(review.movie)" alt="poster" />
                    <div v-else class="poster-placeholder"></div>
                  </div>
                  <div class="review-meta">
                    <div class="review-movie-title">{{ review.movie?.title || "영화 이름" }}</div>
                    <div class="review-movie-subtitle">{{ formatReleaseYear(review.movie?.release_date) }}</div>
                  </div>
                </div>

                <div class="review-content">
                  {{ review.content }}
                </div>

                <div class="review-actions">
                  <v-icon icon="mdi-thumb-up-outline" size="16" color="grey-darken-1"></v-icon>
                  <span>{{ review.like_count ?? 0 }}</span>
                </div>
              </article>
            </div>
          </div>
        </v-window-item>
        <v-window-item value="liked">
          <div class="state-text empty">
            좋아요한 코멘트는 아직 제공되지 않습니다.
          </div>
        </v-window-item>
      </v-window>
    </div>
  </v-container>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/authStore";
import reviewsApi from "@/api/reviewsApi";

const authStore = useAuthStore();
const reviews = ref([]);
const loading = ref(true);
const error = ref("");
const activeTab = ref("written");

const getPosterUrl = (movie) => `https://image.tmdb.org/t/p/w500${movie.poster_path}`;

const formatRating = (value) => {
  if (typeof value !== "number") return "-";
  return value.toFixed(1);
};

const formatReleaseYear = (dateValue) => {
  if (!dateValue) return "개봉년도";
  const year = String(dateValue).slice(0, 4);
  return year ? `${year}` : "개봉년도";
};

const loadMyReviews = async () => {
  loading.value = true;
  error.value = "";

  try {
    if (!authStore.user) {
      await authStore.fetchUser();
    }

    const res = await reviewsApi.getMyReviews();
    const list = Array.isArray(res.data) ? res.data : res.data?.results || [];
    reviews.value = list;
  } catch (err) {
    console.error("내 리뷰 조회 실패:", err);
    error.value = "코멘트를 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
};

onMounted(loadMyReviews);
</script>

<style scoped>
.reviews-wrapper {
  --side-gap: clamp(24px, 6vw, 80px);
  max-width: 900px;
  width: min(900px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
}

.reviews-tabs {
  border-bottom: 1px solid #e5e7eb;
}

.reviews-tabs :deep(.v-slide-group__content) {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.reviews-tabs :deep(.v-tab) {
  width: 100%;
  font-weight: 700;
  color: #9ca3af;
}

.reviews-tabs :deep(.v-tab--selected) {
  color: #111827;
}

.reviews-tabs :deep(.v-slide-group__content .v-slide-group__selection-indicator) {
  height: 2px;
  background-color: #3b82f6;
}

.reviews-window {
  padding-top: 12px;
}

.review-list {
  display: grid;
  gap: 16px;
}

.review-card {
  background: #ebebeb;
  border-radius: 16px;
  padding: 16px;
  display: grid;
  gap: 12px;
}

.review-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.review-user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
}

.user-icon {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.user-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.review-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
}

.review-body {
  display: flex;
  gap: 12px;
  align-items: center;
}

.review-poster {
  width: 64px;
  height: 88px;
  border-radius: 10px;
  overflow: hidden;
  background: #d1d5db;
  flex-shrink: 0;
}

.review-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  background: #d1d5db;
}

.review-meta {
  display: grid;
  gap: 4px;
}

.review-movie-title {
  font-weight: 700;
}

.review-movie-subtitle {
  font-size: 0.85rem;
  color: #6b7280;
}

.review-content {
  font-size: 0.9rem;
  color: #374151;
}

.review-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: #6b7280;
}

.state-text {
  color: #6b7280;
  font-size: 0.95rem;
}

.state-text.error {
  color: #ef4444;
}

.state-text.empty {
  text-align: center;
  padding: 24px 0;
}
</style>
