<template>
  <TheNavbar />

  <v-main class="bg-grey-lighten-5">
    <slot />
  </v-main>
</template>

<script setup>
import TheNavbar from '@/components/common/TheNavbar.vue';
</script>
