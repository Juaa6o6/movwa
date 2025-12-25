<template>
  <v-sheet color="white" class="movie-hero d-flex align-center justify-center position-relative">
    <div class="movie-hero__inner">
      <iframe
        v-if="youtubeUrl"
        :src="youtubeUrl"
        title="YouTube video player"
        frameborder="0"
        allowfullscreen
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        class="movie-hero__media movie-hero__media--video"
      ></iframe>

      <v-img
        v-else
        :src="movie.backdrop_path"
        class="movie-hero__media movie-hero__media--image"
        cover
      >
        <template v-slot:placeholder>
          <div class="d-flex align-center justify-center fill-height">
            <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
          </div>
        </template>
      </v-img>
    </div>
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
  height: 72vh;
  min-height: 690px;
  max-height: 900px;
  position: relative;
  border-radius: 0;
  overflow: hidden;
  background: #000;
}

.movie-hero__inner {
  position: absolute;
  inset: 0;
  overflow: hidden;
  background: #000;
}

.movie-hero__media {
  width: 100%;
  height: 100%;
  display: block;
}

.movie-hero__media--video {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 105%;
  height: 105%;
  transform: translate(-50%, -50%);
}
</style>
