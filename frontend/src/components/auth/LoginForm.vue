<template>
  <v-form @submit.prevent="onSubmit">
    <v-text-field
      v-model="email"
      label="아이디(이메일)"
      type="email"
      variant="outlined"
      density="comfortable"
      class="mb-3"
      autocomplete="email"
    />

    <v-text-field
      v-model="password"
      label="비밀번호"
      type="password"
      variant="outlined"
      density="comfortable"
      class="mb-2"
      autocomplete="current-password"
    />

    <!-- 에러 메시지 위치 (버튼 위) -->
    <v-alert v-if="auth.error" type="error" variant="tonal" class="mb-4">
      {{ auth.error }}
    </v-alert>

    <v-btn
  type="submit"
  block
  size="large"
  height="48"
  :loading="auth.loading"
  :disabled="auth.loading"
>
  로그인
</v-btn>


    <div class="links">
      <button type="button" class="link" @click="onForgot">
        비밀번호를 잊어버리셨나요?
      </button>

      <div class="join-row">
        <span class="muted">계정이 없으신가요?</span>
        <button type="button" class="link strong" @click="onSignup">
          회원가입
        </button>
      </div>
    </div>
  </v-form>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { useAuthStore } from "@/stores/authStore"

const router = useRouter()
const auth = useAuthStore()

const email = ref("")
const password = ref("")

const onSubmit = async () => {
  // 아주 기본적인 프론트 검증(UX)
  if (!email.value || !password.value) {
    auth.error = "이메일과 비밀번호를 입력해 주세요."
    return
  }

  const res = await auth.login({ email: email.value, password: password.value })
  if (res.ok) router.push("/home")
}

const onForgot = () => {
  // 나중에 /password 같은 라우트 생기면 연결
  alert("비밀번호 찾기 기능은 준비 중이에요.")
}

const onSignup = () => {
  router.push("/signup") // 나중에 SignupView 만들면 연결됨
}
</script>

<style scoped>
.links {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}
.link {
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  color: #3da5ff;
  font-size: 12px;
}
.link.strong {
  font-weight: 700;
}
.join-row {
  display: flex;
  gap: 8px;
  align-items: center;
}
.muted {
  color: #666;
  font-size: 12px;
}
</style>
