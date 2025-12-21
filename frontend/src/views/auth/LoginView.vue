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

      <!-- 폼 카드 -->
      <v-card class="form-card" rounded="xl" elevation="2">
        <LoginForm />
      </v-card>
    </div>

    <!-- Footer -->
    <div class="footer">Footer</div>
  </div>
</template>

<script setup>
import LoginForm from "@/components/auth/LoginForm.vue"
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
  width: 180px;   /* 필요하면 조절 */
  height: auto;
}
.headline {
  margin: 0 0 24px;
  font-size: 28px;
  font-weight: 800;
  text-align: center;
}
.form-card {
  width: 100%;
  max-width: 420px;
  padding: 24px;
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
