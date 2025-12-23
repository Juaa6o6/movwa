<template>
  <v-container v-if="home.isLoading" class="fill-height justify-center">
    <v-progress-circular indeterminate color="teal-accent-3" size="64" />
  </v-container>

  <div v-else class="home-view bg-black">
    <HomeHero
      :movie="home.currentMovie"
      @prev="home.prev"
      @next="home.next"
    >
      <MovieActions
        @pass="home.passCurrentMovie"
        @like="home.likeCurrentMovie"
        @rate="home.rateCurrentMovie"
        @save="home.saveCurrentMovie"
      />
    </HomeHero>

    <RecommendationDeck
      :movies="home.recList"
      :currentIndex="home.currentIndex"
      @select="home.selectIndex"
    />

    <v-divider class="my-6 border-opacity-25" />

    <TodaysPick :movies="home.todaysPicks" />
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { useHomeStore } from "@/stores/homeStore";

import HomeHero from "@/components/home/HomeHero.vue";
import RecommendationDeck from "@/components/home/RecommendationDeck.vue";
import MovieActions from "@/components/movie/MovieActions.vue"; // 새로 생성 필요
import TodaysPick from "@/components/home/TodaysPick.vue";     // 새로 생성 필요

const home = useHomeStore();

onMounted(() => {
  home.initHome();
});
</script>