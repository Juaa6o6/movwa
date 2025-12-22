<template>
  <v-app-bar flat color="black" height="80" class="px-4 border-b border-grey-darken-3">
    <router-link to="/home" class="d-flex align-center cursor-pointer">
      <img src="@/assets/logo/movwa_logo.png" alt="MOVWA" height="40" />
    </router-link>

    <div class="ml-10 d-flex gap-4">
      <v-btn to="/home" variant="text" color="white" class="text-subtitle-1 font-weight-bold">영화</v-btn>
      <v-btn to="/library" variant="text" color="grey-lighten-1" class="text-subtitle-1">보관함</v-btn>
    </div>

    <v-spacer></v-spacer>

    <v-text-field
      v-model="searchQuery"
      prepend-inner-icon="mdi-magnify"
      placeholder="제목, 장르, 배우로 검색해보세요"
      variant="outlined"
      density="compact"
      rounded="xl"
      bg-color="grey-darken-4"
      color="white"
      hide-details
      style="max-width: 300px;"
      class="mr-4"
    ></v-text-field>

    <v-menu min-width="200px" rounded>
      <template v-slot:activator="{ props }">
        <v-btn icon v-bind="props">
          <v-avatar color="grey-darken-3" size="40">
            <v-icon icon="mdi-account" color="white"></v-icon>
          </v-avatar>
        </v-btn>
      </template>
      <v-card color="grey-darken-3">
        <v-card-text>
          <div class="mx-auto text-center">
            <h3>{{ user?.username || '사용자' }}</h3>
            <p class="text-caption mt-1">{{ user?.email }}</p>
            <v-divider class="my-3"></v-divider>
            <v-btn rounded variant="text" block>로그아웃</v-btn>
          </div>
        </v-card-text>
      </v-card>
    </v-menu>
  </v-app-bar>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore'; // authStore 경로 확인

const authStore = useAuthStore();
const searchQuery = ref('');
const user = authStore.user;
</script>

<style scoped>
.gap-4 { gap: 16px; }
a { text-decoration: none; }
</style>