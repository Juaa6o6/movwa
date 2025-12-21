<template>
  <v-app>
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
