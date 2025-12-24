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
        @click-hero="goToDetail"
      >
        <MovieActions
          :status="home.currentMovie?.status"
          @pass="home.passCurrentMovie"
          @like="home.likeCurrentMovie"
          @rate="home.rateCurrentMovie"
        />
      </HomeHero>

      <div class="deck-wrapper">
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
import { useRouter } from "vue-router";
import { useHomeStore } from "@/stores/homeStore";

import HomeHero from "@/components/home/HomeHero.vue";
import RecommendationDeck from "@/components/home/RecommendationDeck.vue";
import MovieActions from "@/components/movie/MovieActions.vue";
import TodaysPick from "@/components/home/TodaysPick.vue";

const home = useHomeStore();
const router = useRouter();

onMounted(() => {
  home.initHome();
});

// 히어로 클릭 시 상세 페이지 이동
const goToDetail = () => {
  if (home.currentMovie?.id) {
    router.push(`/movie/${home.currentMovie.id}`);
  }
};
</script>

<style scoped>
.home-view-bg {
  background-color: #ffffff;
  min-height: 100vh;
  padding-bottom: 60px;
  color: #000000;
}

.main-content-wrapper {
  max-width: 1280px; /* 전체 최대 너비 */
  margin: 0 auto;    /* 중앙 정렬 */
  padding-bottom: 20px;
}

/* 덱(Deck) 영역 스타일 */
.deck-wrapper {
  /* Hero와 너비를 맞추기 위해 별도 패딩 없음 (RecommendationDeck 내부에서 처리) */
  margin-top: 10px; /* Hero와 살짝 띄우기 (완전히 붙이고 싶으면 0으로) */
}
</style>