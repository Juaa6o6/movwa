<template>
  <div class="hero">
    <div class="bg" :style="bgStyle" />
    <div class="overlay" />

    <div class="content">
      <div class="info-area">
        <div class="title">{{ movie?.title }}</div>
        <div class="overview text-truncate-3">{{ movie?.overview }}</div>
      </div>

      <div class="action-area mt-auto d-flex align-end justify-space-between w-100">
        <div class="nav-group">
           <v-btn icon="mdi-chevron-left" variant="text" color="white" @click="$emit('prev')" />
           <v-btn icon="mdi-chevron-right" variant="text" color="white" @click="$emit('next')" />
        </div>

        <div class="slot-actions">
           <slot /> 
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from "vue";

const props = defineProps({
  movie: { type: Object, default: null },
});

defineEmits(["prev", "next"]);

const bgStyle = computed(() => {
  const path = props.movie?.backdrop_path || props.movie?.poster_path;
  const url = path ? `https://image.tmdb.org/t/p/original${path}` : "";
  return {
    backgroundImage: url ? `url(${url})` : "none",
  };
});

watch(
  () => props.movie,
  (v) => console.log("HomeHero movie:", v),
  { immediate: true }
);
</script>

<style scoped>
.hero {
  position: relative;
  height: 360px;
  border-radius: 16px;
  overflow: hidden;
}
.bg {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  transform: scale(1.03);
}
.overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(0,0,0,0.65), rgba(0,0,0,0.15));
}
.content {
  position: relative;
  height: 100%;
  padding: 28px;
  color: white;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 720px;
}
.title {
  font-size: 36px;
  line-height: 1.1;
}
.subtitle {
  font-size: 14px;
  opacity: 0.9;
}
.overview {
  margin-top: 10px;
  font-size: 15px;
  opacity: 0.95;
  max-width: 620px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.nav {
  margin-top: auto;
  display: flex;
  gap: 10px;
}
</style>
