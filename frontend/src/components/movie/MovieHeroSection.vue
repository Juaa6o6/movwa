<template>
  <v-sheet color="black" height="500" class="d-flex align-center justify-center position-relative">
    <iframe
      v-if="youtubeUrl"
      width="100%" height="100%"
      :src="youtubeUrl"
      title="YouTube video player"
      frameborder="0" allowfullscreen
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      style="z-index: 1;"
    ></iframe>
    
    <v-img
      v-else
      :src="movie.backdrop_path"
      cover height="100%"
    >
      <template v-slot:placeholder>
        <div class="d-flex align-center justify-center fill-height">
          <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
        </div>
      </template>
    </v-img>

    </v-sheet>
</template>

<script setup>
defineProps({
  movie: Object,
  youtubeUrl: String
});
</script>

<style scoped>
/* 그라데이션 스타일도 더 이상 필요 없어서 삭제했습니다. */
</style>