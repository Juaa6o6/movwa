<template>
  <v-container class="py-10" fluid>
    <div class="follow-wrapper">
      <h1 class="page-title">팔로워</h1>

      <div v-if="loading" class="state-text">불러오는 중...</div>
      <div v-else-if="error" class="state-text error">{{ error }}</div>

      <div v-else>
        <div v-if="users.length === 0" class="state-text empty">
          아직 팔로워가 없습니다.
        </div>
        <div v-else class="follow-list">
          <div v-for="user in users" :key="user.id" class="follow-card">
            <div class="follow-avatar">
              <img v-if="user.profile_image_url" :src="user.profile_image_url" alt="profile" />
              <v-icon v-else icon="mdi-account" size="24" color="grey-darken-1"></v-icon>
            </div>
            <div class="follow-info">
              <div class="follow-name">{{ user.nickname || user.username }}</div>
              <div class="follow-subtitle">사용자 소개: -</div>
            </div>
            <v-btn
              variant="tonal"
              size="small"
              class="follow-btn"
              @click="handleToggle(user)"
            >
              {{ user.is_following ? "팔로잉" : "팔로우" }}
            </v-btn>
          </div>
        </div>
      </div>
    </div>
  </v-container>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useAuthStore } from "@/stores/authStore";
import accountsApi from "@/api/accountsApi";

const authStore = useAuthStore();
const users = ref([]);
const loading = ref(true);
const error = ref("");

const loadFollowers = async () => {
  loading.value = true;
  error.value = "";

  try {
    if (!authStore.user) {
      await authStore.fetchUser();
    }

    const username = authStore.user?.username;
    if (!username) {
      error.value = "사용자 정보를 불러올 수 없습니다.";
      return;
    }

    const res = await accountsApi.getFollowers(username);
    const list = Array.isArray(res.data) ? res.data : res.data?.results || [];
    users.value = list;
  } catch (err) {
    console.error("팔로워 목록 조회 실패:", err);
    error.value = "팔로워 목록을 불러오지 못했습니다.";
  } finally {
    loading.value = false;
  }
};

const handleToggle = async (user) => {
  try {
    const res = await accountsApi.toggleFollow(user.username);
    if (typeof res.data?.is_following === "boolean") {
      user.is_following = res.data.is_following;
    } else {
      user.is_following = !user.is_following;
    }
  } catch (err) {
    console.error("팔로우 토글 실패:", err);
  }
};

onMounted(loadFollowers);
</script>

<style scoped>
.follow-wrapper {
  --side-gap: clamp(24px, 6vw, 80px);
  max-width: 760px;
  width: min(760px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
  display: grid;
  gap: 20px;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
}

.follow-list {
  display: grid;
  gap: 16px;
}

.follow-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
  padding: 16px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
}

.follow-avatar {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.follow-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.follow-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.follow-name {
  font-weight: 700;
}

.follow-subtitle {
  font-size: 0.85rem;
  color: #6b7280;
}

.follow-btn {
  min-width: 72px;
  border-radius: 12px;
  font-weight: 700;
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
