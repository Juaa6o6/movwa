<template>
  <div class="d-flex flex-column fill-height bg-white text-black">
    
    <v-tabs
      v-model="tab"
      color="black"
      align-tabs="center"
      bg-color="grey-lighten-4"
      class="border-b"
    >
      <v-tab :value="1" class="text-body-1 font-weight-bold">리뷰</v-tab>
      <v-tab :value="2" class="text-body-1 font-weight-bold">추천 콘텐츠</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="flex-grow-1" style="overflow-y: auto;">
      
      <v-window-item :value="1" class="pa-4">
        <v-btn block color="primary" class="mb-4" size="large" variant="flat" elevation="0">
          <v-icon start>mdi-pencil</v-icon>
          리뷰 남기기
        </v-btn>

        <div v-if="movie?.reviews?.length > 0">
          <v-card
            v-for="review in movie.reviews"
            :key="review.id"
            color="white" 
            class="mb-3 pa-3 border"
            variant="flat"
          >
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="d-flex align-center">
                <v-avatar color="grey-lighten-2" size="24" class="mr-2"> 
                  <v-icon size="16" color="grey-darken-2">mdi-account</v-icon>
                </v-avatar>
                <span class="font-weight-bold text-subtitle-2 text-black">{{ review.user }}</span>
              </div>
              <v-rating
                :model-value="review.rating"
                color="amber"
                density="compact"
                size="x-small"
                readonly
                half-increments
              ></v-rating>
            </div>
            <p class="text-body-2 text-grey-darken-3">{{ review.content }}</p>
            <div class="text-caption text-grey mt-1 text-right">{{ review.date }}</div>
          </v-card>
        </div>

        <div v-else class="text-center py-10 text-grey">
          <v-icon size="40" class="mb-2 text-grey-lighten-1">mdi-comment-outline</v-icon>
          <p>아직 작성된 리뷰가 없습니다.<br>첫 번째 리뷰를 남겨보세요!</p>
        </div>
      </v-window-item>

      <v-window-item :value="2" class="pa-4">
        <v-row dense>
          <v-col cols="6" v-for="n in 6" :key="n">
            <v-card 
              height="200" 
              color="grey-lighten-4" 
              class="d-flex align-center justify-center position-relative border"
              hover
              flat
            >
              <span class="text-caption text-grey">이미지 없음</span>
            </v-card>
          </v-col>
        </v-row>
      </v-window-item>

    </v-window>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  movie: Object
});

const tab = ref(1);
</script>

<style scoped>
/* ✨ 스크롤바 디자인: 화이트 테마에 맞게 밝은 회색으로 변경 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #f1f1f1; /* 트랙 밝게 */
}
::-webkit-scrollbar-thumb {
  background: #c1c1c1; /* 핸들(잡는 부분) 밝은 회색 */
  border-radius: 3px;
}
</style>