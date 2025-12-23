<template>
  <v-sheet color="black" class="movie-hero d-flex align-center justify-center position-relative">
    <iframe
      v-if="youtubeUrl"
      width="100%" height="100%"
      :src="youtubeUrl"
      title="YouTube video player"
      frameborder="0" allowfullscreen
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
      class="movie-hero__media movie-hero__media--video"
      style="z-index: 1;"
    ></iframe>
    
    <v-img
      v-else
      :src="movie.backdrop_path"
      class="movie-hero__media movie-hero__media--image"
      contain height="100%"
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
.movie-hero {
  width: 100%;
  aspect-ratio: 16 / 9;
  height: auto;
  overflow: hidden;
  position: relative;
}

.movie-hero__media {
  width: 100%;
  height: 100%;
  display: block;
}

.movie-hero__media--video {
  position: static;
}
</style>
