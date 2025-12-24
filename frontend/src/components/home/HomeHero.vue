<template>
  <div class="hero-container cursor-pointer" @click="$emit('click-hero')">
    
    <div class="media-bg">
      <iframe
        v-if="videoUrl"
        class="video-iframe"
        :src="videoUrl"
        frameborder="0"
        allow="autoplay; encrypted-media; loop"
        allowfullscreen
      ></iframe>
      
      <div v-else class="img-bg" :style="bgStyle" />
    </div>

    <div class="overlay" />

    <div class="content pa-6 pa-md-10 d-flex flex-column justify-space-between">
      
      <div class="top-area d-flex justify-end" @click.stop>
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
        <h1 class="text-h3 text-md-h1 font-weight-black text-white mb-4 text-shadow title-clamp" style="line-height: 1;">
          {{ movie?.title }}
        </h1>

        <div class="meta-data d-flex align-center text-h6 font-weight-medium text-white opacity-90 text-shadow">
          
          <div v-if="movie?.vote_average > 0" class="d-flex align-center mr-4">
            <v-icon color="yellow-accent-4" class="mr-1">mdi-star</v-icon>
            <span>{{ movie.vote_average.toFixed(1) }}</span>
          </div>
          
          <span v-if="movie?.genres?.length" class="mr-4">
            {{ genreNames }}
          </span>
          
          <span v-if="movie?.runtime > 0">
            {{ movie.runtime }}분
          </span>
        </div>
        <p class="mt-4 text-body-1 text-grey-lighten-3 opacity-80 text-truncate-2" style="max-width: 600px;">
           {{ movie?.tagline || movie?.overview }}
        </p>
      </div>

      <div class="bottom-area d-flex align-end justify-space-between w-100" @click.stop>
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

defineEmits(["prev", "next", "save", "toggle-mute", "click-hero"]);

// 배경 이미지
const bgStyle = computed(() => {
  const path = props.movie?.backdrop_path || props.movie?.poster_path;
  const url = path ? `https://image.tmdb.org/t/p/original${path}` : "";
  return { backgroundImage: url ? `url(${url})` : "none" };
});

// 유튜브 영상 URL 생성
const videoUrl = computed(() => {
  if (!props.movie?.youtube_key) return null;
  const muteParam = props.isMuted ? '1' : '0';
  return `https://www.youtube.com/embed/${props.movie.youtube_key}?autoplay=1&mute=${muteParam}&controls=0&modestbranding=1&rel=0&loop=1&playlist=${props.movie.youtube_key}&enablejsapi=1`;
});

// 장르 이름 연결 (예: 액션 · 모험)
const genreNames = computed(() => {
  if (!props.movie?.genres?.length) return '';
  return props.movie.genres.map(g => g.name).join(' · ');
});
</script>

<style scoped lang="scss">
.hero-container {
  position: relative;
  aspect-ratio: 16 / 9;
  max-height: 900px;
  min-height: 480px;
  width: 100%;
  overflow: hidden;
  background-color: #000;
  border-radius: 10px;
  margin-top: 12px;
}

.media-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  z-index: 0;
}

.video-iframe {
  width: 100%;
  height: 100%;
  transform: none; 
  pointer-events: none;
}

.img-bg {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center top;
  transition: transform 10s ease;
  transform: scale(1.1);
}

.overlay { 
    position: absolute; inset: 0; 
    background: linear-gradient(to top, rgba(0,0,0,0.9) 10%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.6) 100%);
    z-index: 1;
}

.content { position: relative; height: 100%; z-index: 2; }
.text-shadow { text-shadow: 2px 2px 10px rgba(0,0,0,0.8); }

.hero-btn {
    border-width: 2px !important;
    height: 48px;
    padding: 0 24px;
    font-size: 1rem;
}

.glass-btn { backdrop-filter: blur(10px); background-color: rgba(255,255,255,0.1) !important; border: 1px solid rgba(255,255,255,0.2); }
.gap-2 { gap: 12px; }
.gap-3 { gap: 16px; }
.text-truncate-2 { display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }

@media (max-width: 960px) {
  .hero-container {
    height: 60vh;
    aspect-ratio: auto;
  }
}
</style>
