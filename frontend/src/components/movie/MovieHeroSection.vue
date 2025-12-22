<template>
  <v-sheet color="black" height="500" class="d-flex align-center justify-center position-relative">
    <iframe
      v-if="youtubeUrl"
      width="100%" height="100%"
      :src="youtubeUrl"
      title="YouTube video player"
      frameborder="0" allowfullscreen
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
    ></iframe>
    
    <v-img
      v-else
      :src="movie.backdrop_path"
      cover height="100%" class="opacity-60"
    >
      <template v-slot:placeholder>
        <div class="d-flex align-center justify-center fill-height">
          <v-progress-circular indeterminate color="grey-lighten-4"></v-progress-circular>
        </div>
      </template>
    </v-img>

    <div class="position-absolute bottom-0 left-0 w-100 pa-6 bg-gradient-to-t">
      <h1 class="text-h3 font-weight-bold text-white mb-2">
        {{ movie.title }}
        <span class="text-h5 text-grey-lighten-1">({{ getYear(movie.release_date) }})</span>
      </h1>
      
      <div class="d-flex align-center gap-4">
        <v-chip color="yellow-darken-2" variant="flat" class="mr-2">
          ⭐ {{ movie.vote_average?.toFixed(1) }}
        </v-chip>
        <v-chip v-for="genre in movie.genres" :key="genre.id" variant="outlined" class="mr-1 text-white">
          {{ genre.name }}
        </v-chip>
      </div>
    </div>
  </v-sheet>
</template>

<script setup>
defineProps({
  movie: Object,
  youtubeUrl: String
});

const getYear = (dateString) => {
  if (!dateString) return '';
  return dateString.split('-')[0];
};
</script>

<style scoped>
.bg-gradient-to-t {
  background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0) 100%);
}
</style>