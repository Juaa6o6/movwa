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
        :class="['text-subtitle-1', isActive('/movies') ? 'font-weight-bold' : '']"
      >
        영화
      </v-btn>
      
      <v-btn 
        to="/library" 
        variant="text" 
        :color="isActive('/library') ? 'black' : 'grey-lighten-1'"
        :class="['text-subtitle-1', isActive('/library') ? 'font-weight-bold' : '']"
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
            <h3>{{ authStore.user?.username || '사용자' }}</h3>
            <p class="text-caption mt-1">{{ authStore.user?.email }}</p>
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
import { useRouter, useRoute } from 'vue-router'; // 1. useRoute 추가!
import { useAuthStore } from '@/stores/authStore';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute(); // 2. 현재 주소 정보를 담은 변수
const searchQuery = ref('');

// 3. 현재 주소가 path와 일치하는지 확인하는 함수
// 예: 현재 주소가 /movies라면 isActive('/movies')는 true가 됨
const isActive = (path) => {
  return route.path.startsWith(path);
};

const handleLogout = () => {
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.gap-4 { gap: 16px; }
a { text-decoration: none; }
</style>