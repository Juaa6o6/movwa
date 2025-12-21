<template>
  <v-card class="pa-5" elevation="0">
    <v-card-title class="text-center text-h5 font-weight-bold text-primary mb-1">
      프로필 정보를 입력해 주세요
    </v-card-title>
    <v-card-subtitle class="text-center mb-5">
      서비스 내에서 보여질 프로필입니다.
    </v-card-subtitle>

    <div class="text-center mb-5">
      <v-avatar size="100" color="grey-lighten-3">
        <v-icon size="50" color="grey">mdi-account</v-icon>
      </v-avatar>
    </div>

    <v-form ref="form" @submit.prevent="onNext">
      <v-text-field
        v-model="authStore.signupForm.nickname"
        label="닉네임"
        variant="outlined"
        :rules="[rules.required]"
        class="mb-2"
      ></v-text-field>

      <v-text-field
        v-model="authStore.signupForm.username"
        label="핸들 (고유 ID)"
        prefix="@"
        variant="outlined"
        :rules="[rules.required, rules.alphaNum]"
        hint="영문, 숫자, 밑줄만 가능"
        class="mb-4"
      ></v-text-field>

      <v-progress-linear model-value="66" color="primary" height="6" rounded class="mb-5"></v-progress-linear>

      <div class="d-flex gap-2">
        <v-btn variant="tonal" size="large" class="flex-grow-1" @click="$emit('prev')">뒤로</v-btn>
        <v-btn type="submit" color="primary" size="large" class="flex-grow-1" flat>다음</v-btn>
      </div>
    </v-form>
  </v-card>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const emit = defineEmits(['next', 'prev'])
const form = ref(null)

const rules = {
  required: v => !!v || '필수 입력입니다.',
  alphaNum: v => /^[a-zA-Z0-9_]+$/.test(v) || '영문, 숫자, 밑줄만 가능'
}

const onNext = async () => {
  const { valid } = await form.value.validate()
  if (valid) emit('next')
}
</script>

<style scoped>
.gap-2 { gap: 8px; }
</style>