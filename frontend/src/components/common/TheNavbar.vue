<template>
  <v-app-bar flat color="white" height="80" class="px-4 border-b">
    <router-link to="/home" class="d-flex align-center cursor-pointer">
      <img src="@/assets/logo/movwa_logo.png" alt="MOVWA" height="40" />
    </router-link>

    <div class="ml-10 d-flex gap-4">
      <v-btn 
        to="/movies" 
        variant="text" 
        :color="isActive('/movies') ? 'black' : 'grey-lighten-1'"
        :class="['nav-btn', 'text-subtitle-1', isActive('/movies') ? 'font-weight-bold' : '']"
      >
        영화
      </v-btn>
      
      <v-btn 
        to="/library" 
        variant="text" 
        :color="isActive('/library') ? 'black' : 'grey-lighten-1'"
        :class="['nav-btn', 'text-subtitle-1', isActive('/library') ? 'font-weight-bold' : '']"
      >
        보관함
      </v-btn>
    </div>

    <v-spacer></v-spacer>

    <v-text-field
      v-model="searchQuery"
      prepend-inner-icon="mdi-magnify"
      placeholder="제목, 장르로 검색해보세요"
      variant="outlined"
      density="compact"
      rounded="xl"
      bg-color="white"
      color="primary"
      hide-details
      style="max-width: 320px;"
      class="mr-4"
      @keyup.enter="handleSearch"
    ></v-text-field>

    <v-menu min-width="200px" rounded offset="12">
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props">
          <v-avatar color="grey-lighten-4" size="40">
            <img v-if="profileImageUrl" :src="profileImageUrl" alt="profile" />
            <v-icon v-else icon="mdi-account" color="grey-darken-1"></v-icon>
          </v-avatar>
        </v-btn>
      </template>
      <v-card>
        <v-card-text>
          <div class="profile-menu">
            <p class="text-caption mt-1 mb-1">@{{ authStore.user?.username || 'username' }}</p>
            <v-btn rounded variant="text" block class="menu-btn" @click="goToProfile">내 프로필</v-btn>
            <v-divider class="my-3"></v-divider>
            <v-btn rounded variant="text" block class="menu-btn" @click="handleLogout">로그아웃</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { ref, watch, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router'; // 1. useRoute 추가!
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute(); // 2. 현재 주소 정보를 담은 변수
const searchQuery = ref('');
const profileImageUrl = computed(() => authStore.user?.profile_image_url || null);

// 3. 현재 주소가 path와 일치하는지 확인하는 함수
// 예: 현재 주소가 /movies라면 isActive('/movies')는 true가 됨
const isActive = (path) => {
  return route.path.startsWith(path);
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};

const goToProfile = () => {
  router.push('/profile');
};

const handleSearch = () => {
  const query = searchQuery.value.trim();
  if (!query) return;
  router.push({ path: '/search', query: { q: query } });
};

onMounted(() => {
  if (!authStore.user) {
    authStore.fetchUser();
  }
});

watch(
  () => route.query.q,
  (value) => {
    if (route.path.startsWith('/search')) {
      searchQuery.value = typeof value === 'string' ? value : '';
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.gap-4 { gap: 16px; }
a { text-decoration: none; }
.nav-btn { background-color: transparent !important; }
.nav-btn.v-btn--active { background-color: transparent !important; }
.nav-btn:hover { background-color: transparent !important; }
.nav-btn:focus-visible { background-color: transparent !important; }
:deep(.nav-btn .v-btn__overlay) { opacity: 0 !important; }
:deep(.nav-btn .v-btn__underlay) { opacity: 0 !important; }
:deep(.nav-btn .v-ripple__container) { opacity: 0 !important; }

.profile-menu {
  text-align: left;
  padding-top: 2px;
}

.menu-btn {
  margin-top: 0;
  min-height: 32px;
}

:deep(.v-avatar img) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
