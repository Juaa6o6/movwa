<template>
  <div class="hero-container">
    <div class="bg" :style="bgStyle" />
    <div class="overlay" />

    <div class="content pa-6 pa-md-10 d-flex flex-column justify-space-between">
      
      <div class="top-area d-flex justify-end">
        <div class="top-actions d-flex gap-3">
          <v-btn
            rounded="pill"
            :variant="isMuted ? 'outlined' : 'flat'"
            :color="isMuted ? 'white' : 'grey-lighten-2'"
            class="hero-btn font-weight-bold"
            @click="$emit('toggle-mute')"
          >
            <v-icon start>{{ isMuted ? 'mdi-volume-off' : 'mdi-volume-high' }}</v-icon>
            {{ isMuted ? '음소거' : '소리 켬' }}
          </v-btn>

          <v-btn
            rounded="pill"
            :variant="movie?.status === 'saved' ? 'flat' : 'outlined'"
            :color="movie?.status === 'saved' ? 'blue-accent-3' : 'white'"
            class="hero-btn font-weight-bold"
            @click="$emit('save')"
          >
            <v-icon start>{{ movie?.status === 'saved' ? 'mdi-bookmark' : 'mdi-bookmark-outline' }}</v-icon>
            SAVE
          </v-btn>
        </div>
      </div>

      <div class="center-area d-flex flex-column align-start justify-center flex-grow-1 my-auto">
        
        <h1 class="text-h3 text-md-h1 font-weight-black text-white mb-4 text-shadow" style="line-height: 1;">
          {{ movie?.title }}
        </h1>

        <div class="meta-data d-flex align-center text-h6 font-weight-medium text-white opacity-90 text-shadow">
          <v-icon color="yellow-accent-4" class="mr-1">mdi-star</v-icon>
          <span class="mr-4">{{ movie?.vote_average?.toFixed(1) || '0.0' }}</span>
          
          <span class="mr-4">{{ genreNames }}</span>
          
          <span>{{ movie?.runtime ? `${movie.runtime}분` : '' }}</span>
        </div>
        
        <p class="mt-4 text-body-1 text-grey-lighten-3 opacity-80" style="max-width: 600px;">
           {{ movie?.tagline || movie?.overview }}
        </p>
      </div>

      <div class="bottom-area d-flex align-end justify-space-between w-100">
        <div class="nav-group d-flex gap-2">
           <v-btn icon="mdi-chevron-left" variant="tonal" color="white" class="glass-btn" @click="$emit('prev')" />
           <v-btn icon="mdi-chevron-right" variant="tonal" color="white" class="glass-btn" @click="$emit('next')" />
        </div>

        <div class="slot-actions">
           <slot /> 
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  movie: { type: Object, default: null },
  isMuted: { type: Boolean, default: true },
});

defineEmits(["prev", "next", "save", "toggle-mute"]);

const bgStyle = computed(() => {
  const path = props.movie?.backdrop_path || props.movie?.poster_path;
  const url = path ? `https://image.tmdb.org/t/p/original${path}` : "";
  return { backgroundImage: url ? `url(${url})` : "none", backgroundColor: "#000" };
});

const genreNames = computed(() => {
  if (!props.movie?.genres?.length) return '장르 정보 없음';
  return props.movie.genres.map(g => g.name).join(' · ');
});
</script>

<style scoped lang="scss">
.hero-container {
  position: relative;
  aspect-ratio: 16 / 9;
  max-height: 700px;
  min-height: 550px;
  overflow: hidden;
  background-color: #000;
}

.bg { position: absolute; inset: 0; background-size: cover; background-position: center top; transition: all 0.5s ease; transform: scale(1.02); }
.overlay { 
    position: absolute; inset: 0; 
    background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.4) 50%, rgba(0,0,0,0.6) 100%);
}
.content { position: relative; height: 100%; z-index: 2; }
.text-shadow { text-shadow: 2px 2px 10px rgba(0,0,0,0.7); }
.hero-btn {
    border-width: 2px !important;
    height: 48px;
    padding: 0 24px;
    font-size: 1rem;
}
.glass-btn { backdrop-filter: blur(10px); background-color: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.2); }
.gap-2 { gap: 12px; }
.gap-3 { gap: 16px; }
</style>