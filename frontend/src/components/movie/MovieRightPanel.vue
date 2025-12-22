<template>
  <v-card variant="flat" class="fill-height bg-transparent">
    <v-tabs
      v-model="tab"
      color="primary"
      align-tabs="center"
      class="mb-4"
    >
      <v-tab :value="1">리뷰</v-tab>
      <v-tab :value="2">추천 영화</v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item :value="1">
        <v-btn 
          block 
          color="grey-darken-3" 
          class="mb-4 py-6"
          elevation="0"
        >
          리뷰 작성하기
        </v-btn>

        <div class="d-flex align-center justify-space-between mb-4 px-2">
          <span class="text-h6 font-weight-bold">평균 별점</span>
          <div class="text-yellow-darken-2">
            <v-icon icon="mdi-star"></v-icon>
            <span class="text-h6 font-weight-bold ml-1">{{ movie.vote_average }}</span>
          </div>
        </div>

        <v-list lines="two" bg-color="transparent">
          <v-list-item
            v-for="review in movie.reviews"
            :key="review.id"
            class="mb-3 rounded-lg bg-grey-lighten-4"
            elevation="0"
          >
            <template v-slot:prepend>
              <v-avatar color="grey-darken-1" size="32">
                <v-icon icon="mdi-account" color="white" size="20"></v-icon>
              </v-avatar>
            </template>

            <v-list-item-title class="font-weight-bold text-body-2 mb-1">
              {{ review.user }}
              <span class="text-caption text-grey ml-2">{{ review.date }}</span>
            </v-list-item-title>
            
            <div class="d-flex align-center mb-1">
              <v-rating
                :model-value="review.rating"
                color="yellow-darken-3"
                density="compact"
                size="small"
                readonly
                half-increments
              ></v-rating>
            </div>

            <p class="text-body-2 text-grey-darken-3">
              {{ review.content }}
            </p>
          </v-list-item>
        </v-list>
      </v-window-item>

      <v-window-item :value="2">
        <v-row dense>
          <v-col cols="6" v-for="n in 6" :key="n">
            <v-card height="150" color="grey-lighten-2" class="d-flex align-center justify-center">
              <span class="text-caption text-grey">추천 영화 {{ n }}</span>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>
    </v-window>
  </v-card>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  movie: Object
});

const tab = ref(1); // 기본값 1 (리뷰 탭)
</script>

<style scoped>
/* 스크롤바 커스텀 (선택사항) */
.v-list {
  max-height: 600px;
  overflow-y: auto;
}
</style>