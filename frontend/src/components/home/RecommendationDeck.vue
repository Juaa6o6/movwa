<template>
  <div class="deck-wrapper">
    <v-btn 
      icon="mdi-chevron-left" 
      size="small" 
      class="scroll-btn left-btn elevation-3"
      @click="scroll('left')"
    />

    <div class="deck-container" ref="deckRef">
      <div class="deck">
        <div
          v-for="(m, idx) in movies"
          :key="m.id ?? idx"
          class="thumb"
          :class="{ 
            selected: idx === currentIndex,
            'is-rated': m.status 
          }"
          @click="$emit('select', idx)"
        >
          <img :src="posterUrl(m)" alt="poster" loading="lazy" />
          
          <div v-if="m.status" class="status-overlay">
            <v-icon v-if="m.status === 'liked'" color="red-accent-2" size="large">mdi-heart</v-icon>
            <v-icon v-if="m.status === 'passed'" color="grey-lighten-1" size="large">mdi-close</v-icon>
            <div v-if="m.status === 'rated'" class="d-flex flex-column align-center">
              <v-icon color="yellow-accent-4" size="large">mdi-star</v-icon>
              <span class="text-caption font-weight-bold text-white">{{ m.rating }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <v-btn 
      icon="mdi-chevron-right" 
      size="small" 
      class="scroll-btn right-btn elevation-3" 
      @click="scroll('right')"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  movies: { type: Array, default: () => [] },
  currentIndex: { type: Number, default: 0 },
});

defineEmits(["select"]);

const deckRef = ref(null);

const posterUrl = (m) => {
  const path = m?.poster_path;
  if (!path) return "https://via.placeholder.com/120x180?text=No+Img";
  return `https://image.tmdb.org/t/p/w342${path}`;
};

// 스크롤 로직
const scroll = (direction) => {
  if (!deckRef.value) return;
  const scrollAmount = 300; // 한 번에 스크롤할 양
  if (direction === 'left') {
    deckRef.value.scrollBy({ left: -scrollAmount, behavior: 'smooth' });
  } else {
    deckRef.value.scrollBy({ left: scrollAmount, behavior: 'smooth' });
  }
};
</script>

<style scoped>
.deck-wrapper {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
}

.deck-container {
  width: 100%;
  overflow-x: auto;
  scroll-behavior: smooth;
  /* 스크롤바 숨김 */
  &::-webkit-scrollbar { display: none; }
  scrollbar-width: none;
}

.deck {
  display: flex;
  gap: 12px;
  /* 위아래 패딩 조금 줘서 focus 짤림 방지 */
  padding: 4px 2px;
}

.thumb {
  position: relative;
  /* 너비 고정 또는 반응형 (min-width 사용) */
  min-width: 120px; 
  height: 180px;
  border-radius: 0; /* 각지게 */
  overflow: hidden;
  opacity: 0.6;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent; /* 레이아웃 흔들림 방지 */
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 선택된 썸네일 */
.thumb.selected {
  opacity: 1;
  border: 3px solid #000; /* 검은 테두리로 강조 */
  box-sizing: border-box;
}

.status-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
  z-index: 1;
}

/* 스크롤 화살표 버튼 */
.scroll-btn {
  position: absolute;
  z-index: 10;
  background-color: rgba(255, 255, 255, 0.9) !important;
  color: #000 !important;
  opacity: 0; /* 평소엔 숨김 */
  transition: opacity 0.3s;
}

/* Wrapper에 마우스 올리면 버튼 보이기 */
.deck-wrapper:hover .scroll-btn {
  opacity: 1;
}

.left-btn { left: -20px; }
.right-btn { right: -20px; }

/* 모바일 등 작은 화면에서는 버튼 위치 조정 */
@media (max-width: 1320px) {
  .left-btn { left: 10px; }
  .right-btn { right: 10px; }
}

@media (max-width: 600px) {
  .thumb {
    min-width: 90px;
    height: 135px;
  }
}
</style>