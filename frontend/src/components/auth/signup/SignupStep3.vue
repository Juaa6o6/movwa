<template>
  <v-card class="pa-5" elevation="0">
    <v-card-title class="text-center text-h5 font-weight-bold text-primary mb-1">
      어떤 콘텐츠를 좋아하세요?
    </v-card-title>
    <v-card-subtitle class="text-center mb-5">
      비슷한 콘텐츠를 추천해드려요.
    </v-card-subtitle>

    <v-sheet class="overflow-y-auto mb-5" max-height="400">
      <v-item-group multiple v-model="authStore.signupForm.genres">
        <v-container class="pa-0">
          <v-row>
            <v-col v-for="genre in genres" :key="genre.id" cols="4">
              <v-item v-slot="{ isSelected, toggle }">
                <v-card
                  :color="isSelected ? 'primary' : 'grey-lighten-4'"
                  class="d-flex align-center justify-center"
                  height="80"
                  @click="toggle"
                  flat
                  rounded="lg"
                >
                  <span :class="isSelected ? 'text-white' : 'text-grey-darken-2'" class="text-body-2 font-weight-bold">
                    {{ genre.name }}
                  </span>
                </v-card>
              </v-item>
            </v-col>
          </v-row>
        </v-container>
      </v-item-group>
    </v-sheet>

    <v-progress-linear model-value="100" color="primary" height="6" rounded class="mb-5"></v-progress-linear>

    <div class="d-flex gap-2">
      <v-btn variant="tonal" size="large" class="flex-grow-1" @click="$emit('prev')">뒤로</v-btn>
      <v-btn color="primary" size="large" class="flex-grow-1" flat @click="onComplete">완료</v-btn>
    </div>
  </v-card>
</template>

<script setup>
import { useAuthStore } from '@/stores/authStore'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()
const emit = defineEmits(['prev'])

const genres = [
  { id: 1, name: '액션' }, { id: 2, name: '로맨스' }, { id: 3, name: '코미디' },
  { id: 4, name: 'SF' }, { id: 5, name: '공포' }, { id: 6, name: '드라마' },
  { id: 7, name: '판타지' }, { id: 8, name: '다큐' }, { id: 9, name: '애니' }
]

const onComplete = async () => {
  const success = await authStore.signup()
  if (success) {
    router.push({ name: 'LoginView' }) // 성공 시 로그인 페이지로
  }
}
</script>

<style scoped>
.gap-2 { gap: 8px; }
</style>