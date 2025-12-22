<template>
  <div class="d-flex flex-column fill-height bg-grey-darken-4">
    <v-tabs
      v-model="tab"
      color="primary"
      align-tabs="center"
      bg-color="grey-darken-4"
      class="border-b-thin border-opacity-25"
    >
      <v-tab :value="1" class="text-body-1">리뷰</v-tab>
      <v-tab :value="2" class="text-body-1">추천 콘텐츠</v-tab>
    </v-tabs>

    <v-window v-model="tab" class="flex-grow-1" style="overflow-y: auto;">
      
      <v-window-item :value="1" class="pa-4">
        <v-btn block color="primary" class="mb-4" size="large" variant="flat">
          <v-icon start>mdi-pencil</v-icon>
          리뷰 남기기
        </v-btn>

        <div v-if="movie?.reviews?.length > 0">
          <v-card
            v-for="review in movie.reviews"
            :key="review.id"
            color="grey-darken-3"
            class="mb-3 pa-3"
            variant="flat"
          >
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="d-flex align-center">
                <v-avatar color="grey" size="24" class="mr-2">
                  <v-icon size="16">mdi-account</v-icon>
                </v-avatar>
                <span class="font-weight-bold text-subtitle-2">{{ review.user }}</span>
              </div>
              <v-rating
                :model-value="review.rating"
                color="yellow-darken-2"
                density="compact"
                size="x-small"
                readonly
                half-increments
              ></v-rating>
            </div>
            <p class="text-body-2 text-grey-lighten-1">{{ review.content }}</p>
            <div class="text-caption text-grey mt-1 text-right">{{ review.date }}</div>
          </v-card>
        </div>

        <div v-else class="text-center py-10 text-grey">
          <v-icon size="40" class="mb-2">mdi-comment-off-outline</v-icon>
          <p>아직 작성된 리뷰가 없습니다.<br>첫 번째 리뷰를 남겨보세요!</p>
        </div>
      </v-window-item>

      <v-window-item :value="2" class="pa-4">
        <v-row dense>
          <v-col cols="6" v-for="n in 6" :key="n">
            <v-card 
              height="200" 
              color="grey-darken-3" 
              class="d-flex align-center justify-center position-relative"
              hover
            >
              <v-img
                src="https://via.placeholder.com/150x225?text=Poster"
                cover
                class="align-end"
                gradient="to bottom, rgba(0,0,0,0) 0%, rgba(0,0,0,0.8) 100%"
              >
                <v-card-title class="text-white text-body-2 font-weight-bold px-2 pb-2">
                  비슷한 영화 {{ n }}
                </v-card-title>
              </v-img>
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
/* 스크롤바 디자인 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: #212121;
}
::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 3px;
}
</style>