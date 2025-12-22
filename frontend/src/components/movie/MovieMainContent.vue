<template>
  <div>
    <h2 class="text-h5 font-weight-bold mb-4">줄거리</h2>
    <p class="text-body-1 mb-8">{{ movie?.overview }}</p>

    <h2 class="text-h5 font-weight-bold mb-4">출연진</h2>
    <div class="d-flex flex-wrap gap-2 mb-8">
      <v-chip v-for="(actor, index) in castList?.slice(0, 5)" :key="index">
        {{ actor.name }}
      </v-chip>
    </div>

    <h2 class="text-h5 font-weight-bold mb-4">관련 영상</h2>
    <v-row>
      <v-col cols="6" md="3" v-for="n in 4" :key="n">
        <v-card color="teal-lighten-4" height="100"></v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
// 부모(DetailView)로부터 영화 정보와 출연진 리스트를 받아옴
defineProps({
  movie: Object,
  castList: Array
});
</script>