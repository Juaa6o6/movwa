<template>
  <v-container v-if="home.isLoading" class="fill-height justify-center">
    <v-progress-circular indeterminate color="teal-accent-3" size="64" />
  </v-container>

  <div v-else class="home-view-bg">
    <div class="main-content-wrapper">
      
      <HomeHero
        :movie="home.currentMovie"
        :is-muted="home.isMuted"
        @prev="home.prev"
        @next="home.next"
        @save="home.saveCurrentMovie"
        @toggle-mute="home.toggleMute"
      >
        <MovieActions
          :status="home.currentMovie?.status"
          @pass="home.passCurrentMovie"
          @like="home.likeCurrentMovie"
          @rate="home.rateCurrentMovie"
        />
      </HomeHero>

      <div class="mt-8 mb-4 px-4">
         <h3 class="text-h6 font-weight-bold text-black mb-3">추천 영화 목록</h3>
         <RecommendationDeck
           :movies="home.recList"
           :currentIndex="home.currentIndex"
           @select="home.selectIndex"
         />
      </div>

      <v-divider class="my-8 mx-4" />

      <div class="px-4">
        <h3 class="text-h5 font-weight-bold text-black mb-4">오늘의 픽 영화</h3>
        <TodaysPick :movies="home.todaysPicks" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useHomeStore } from "@/stores/homeStore";

import HomeHero from "@/components/home/HomeHero.vue";
import RecommendationDeck from "@/components/home/RecommendationDeck.vue";
import MovieActions from "@/components/movie/MovieActions.vue";
import TodaysPick from "@/components/home/TodaysPick.vue";

const home = useHomeStore();

onMounted(() => {
  home.initHome();
});
</script>

<style scoped>
.home-view-bg {
  background-color: #ffffff; /* 배경을 흰색으로 변경 */
  min-height: 100vh;
  padding-bottom: 60px;
  color: #000000; /* 기본 텍스트 색상 검은색으로 */
}

.main-content-wrapper {
  max-width: 1280px;
  margin: 0 auto;
  /* padding-top을 제거하여 Hero가 상단에 딱 붙게 함 */
}
</style>