<template>
  <v-card class="pa-5" elevation="0">
    <v-card-title class="text-center text-h5 font-weight-bold mb-4">
      회원 정보를 입력해주세요
    </v-card-title>
    
    <v-form ref="form" @submit.prevent="onNext">
      <v-text-field
        v-model="authStore.signupForm.email"
        label="이메일 (아이디)"
        placeholder="example@movwa.com"
        variant="outlined"
        :rules="[rules.required, rules.email]"
        class="mb-2"
      ></v-text-field>

      <v-text-field
        v-model="authStore.signupForm.password"
        label="비밀번호"
        type="password"
        variant="outlined"
        :rules="[rules.required, rules.minPw]"
        class="mb-2"
      ></v-text-field>

      <v-text-field
        v-model="passwordConfirm"
        label="비밀번호 확인"
        type="password"
        variant="outlined"
        :rules="[rules.required, passwordMatchRule]"
        class="mb-4"
      ></v-text-field>

      <v-checkbox
        label="모두 확인하였으며 동의합니다."
        color="primary"
        hide-details
        class="mb-5"
      ></v-checkbox>

      <v-progress-linear model-value="33" color="primary" height="6" rounded class="mb-5"></v-progress-linear>

      <v-btn type="submit" color="primary" block size="large" flat>다음</v-btn>
    </v-form>
  </v-card>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/authStore'

const authStore = useAuthStore()
const emit = defineEmits(['next']) // 부모에게 '다음' 신호 보냄
const form = ref(null)
const passwordConfirm = ref('')

const rules = {
  required: v => !!v || '필수 입력입니다.',
  email: v => /.+@.+\..+/.test(v) || '이메일 형식이 아닙니다.',
  minPw: v => (v && v.length >= 8) || '8자 이상이어야 합니다.'
}

const passwordMatchRule = computed(() => {
  return () => authStore.signupForm.password === passwordConfirm.value || '비밀번호가 일치하지 않습니다.'
})

const onNext = async () => {
  const { valid } = await form.value.validate()
  if (valid) emit('next')
}
</script>