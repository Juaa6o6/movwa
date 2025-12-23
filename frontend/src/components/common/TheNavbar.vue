<template>
  <v-app-bar flat color="white" height="80" class="px-4 border-b">
    <router-link to="/home" class="d-flex align-center cursor-pointer">
      <img src="@/assets/logo/movwa_logo.png" alt="MOVWA" height="40" />
    </router-link>

    <div class="ml-10 d-flex gap-4">
      <v-btn to="/home" variant="text"color="black" class="text-subtitle-1 font-weight-bold">영화</v-btn>
      <v-btn to="/library" variant="text" color="grey-lighten-1" class="text-subtitle-1">보관함</v-btn>
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
    ></v-text-field>

    <v-menu min-width="200px" rounded>
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props">
          <v-avatar color="grey-lighten-4" size="40">
            <v-icon icon="mdi-account" color="grey-darken-1"></v-icon>
          </v-avatar>
        </v-btn>
      </template>
      <v-card>
        <v-card-text>
          <div class="mx-auto text-center">
            <h3>{{ user?.username || '사용자' }}</h3>
            <p class="text-caption mt-1">{{ user?.email }}</p>
            <v-divider class="my-3"></v-divider>
            <v-btn rounded variant="text" block @click="handleLogout">로그아웃</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router'; // 1. 라우터 가져오기
import { useAuthStore } from '@/stores/authStore'; // authStore 경로 확인

const authStore = useAuthStore();
const router = useRouter(); // 2. 라우터 사용 설정
const searchQuery = ref('');
const user = authStore.user;

// 3. 로그아웃 함수 만들기
const handleLogout = () => {
  authStore.logout();      // 스토어에서 토큰 삭제
  router.push('/login');   // 로그인 페이지로 이동
  // window.location.reload(); // (혹시 화면 갱신 안 되면 주석 풀고 사용)
};
</script>

<style scoped>
.gap-4 { gap: 16px; }
a { text-decoration: none; }
</style>