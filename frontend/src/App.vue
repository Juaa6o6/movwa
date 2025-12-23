<template>
  <v-app >
    <component :is="layout">
      <router-view />
    </component>
  </v-app>
</template>

<script setup>
import { computed } from "vue"
import { useRoute } from "vue-router"
import AuthLayout from "@/layouts/AuthLayout.vue"
import DefaultLayout from "@/layouts/DefaultLayout.vue"

const route = useRoute()

const layout = computed(() => {
  return route.meta?.layout === "auth" ? AuthLayout : DefaultLayout
})
</script>

<style>
/* 🔥 화이트 테마용 스크롤바 디자인 수정 */
::-webkit-scrollbar {
  width: 10px; /* 두께 살짝 키움 (터치/클릭 편하게) */
}
::-webkit-scrollbar-track {
  background: #f1f1f1; /* 완전 흰색보다는 아주 연한 회색이 눈이 편함 */
}
::-webkit-scrollbar-thumb {
  background: #c1c1c1; /* 너무 진한 #424242 대신 부드러운 회색 사용 */
  border-radius: 5px;
}
::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8; /* 마우스 올렸을 때 살짝 진해짐 */
}
</style>