<template>
  <div class="login-page">
    <div class="content">
      <!-- 로고 -->
      <div class="logo-wrap">
        <img
          src="@/assets/logo/movwa_logo.png"
          alt="movwa logo"
          class="logo-image"
        />
      </div>

      <!-- 문구 -->
      <h1 class="headline">너 오늘 모바?, 나 모바!</h1>

      <!-- 버튼 -->
      <v-btn
        class="start-btn"
        size="large"
        height="48"
        @click="goLogin"
      >
        지금 시작하기
      </v-btn>
    </div>

    <div class="footer">Footer</div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router"
const router = useRouter()

const goLogin = () => {
  router.push("/login")
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
.content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
}
.logo-wrap {
  margin-bottom: 24px;
}
.logo-image {
  width: 180px;
  height: auto;
}
.headline {
  margin: 0 0 24px;
  font-size: 28px;
  font-weight: 800;
  text-align: center;
}
.start-btn {
  width: 220px;
}
.footer {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-top: 1px solid #eee;
  color: #777;
  font-size: 12px;
}
</style>
