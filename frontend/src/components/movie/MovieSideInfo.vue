<template>
  <v-card variant="tonal" class="pa-4">
    <h3 class="text-h6 mb-2">상세 정보</h3>
    <v-divider class="mb-2"></v-divider>
    
    <div class="d-flex justify-space-between mb-1">
      <span>개봉일</span>
      <span>{{ movie?.release_date }}</span>
    </div>
    <div class="d-flex justify-space-between mb-1">
      <span>상영 시간</span>
      <span>{{ movie?.runtime }}분</span>
    </div>
  </v-card>
</template>

<script setup>
defineProps({
  movie: Object
});
</script>