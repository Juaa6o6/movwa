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
          v-for="(m, idx) in visibleMovies"
          :key="m.id ?? idx"
          class="thumb"
          :class="{ 
            selected: idx === clampedIndex,
            'is-rated': m.status 
          }"
          @click="$emit('select', idx)"
        >
          <img :src="posterUrl(m)" alt="poster" loading="lazy" />
          
          <div v-if="m.status" class="status-overlay">
            <v-icon v-if="m.status === 'liked'" color="red-accent-2" class="status-icon">mdi-heart</v-icon>
            <v-icon v-if="m.status === 'passed'" color="grey-lighten-1" class="status-icon">mdi-close</v-icon>
            <v-icon v-if="m.status === 'saved'" color="blue-accent-2" class="status-icon">mdi-bookmark</v-icon>
            <div v-if="m.status === 'rated'" class="d-flex flex-column align-center">
              <v-icon color="yellow-accent-4" class="status-icon">mdi-star</v-icon>
              <span class="text-body-5 font-weight-bold text-white">{{ m.rating }}</span>
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
import { ref, watch, nextTick, computed } from 'vue';

const props = defineProps({
  movies: { type: Array, default: () => [] },
  currentIndex: { type: Number, default: 0 },
});

defineEmits(["select"]);

const deckRef = ref(null);

// 최대 10개의 추천 썸네일만 노출
const visibleMovies = computed(() => props.movies.slice(0, 10));

// 현재 선택 인덱스를 썸네일 범위 내로 클램프
const clampedIndex = computed(() => {
  const maxIdx = visibleMovies.value.length - 1;
  return Math.max(0, Math.min(props.currentIndex, maxIdx));
});

const posterUrl = (m) => {
  const path = m?.poster_path;
  if (!path) return "https://via.placeholder.com/120x180?text=No+Img";
  return `https://image.tmdb.org/t/p/w342${path}`;
};

// 선택된 썸네일이 항상 보이도록 스크롤
const scrollToSelected = (index) => {
  if (!deckRef.value) return;
  const thumbs = deckRef.value.querySelectorAll('.thumb');
  const target = thumbs[index];
  if (!target) return;
  const container = deckRef.value;
  const containerRect = container.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();
  const targetCenter = targetRect.left + (targetRect.width / 2);
  const containerCenter = containerRect.left + (containerRect.width / 2);
  const delta = targetCenter - containerCenter;
  const nextLeft = container.scrollLeft + delta;
  container.scrollTo({ left: nextLeft, behavior: 'smooth' });
};

watch(
  () => clampedIndex.value,
  (val) => {
    nextTick(() => scrollToSelected(val));
  }
);

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
  overflow: visible; /* 위로 띄운 썸네일 잘림 방지 */
}

.deck-container {
  width: 100%;
  overflow-x: auto;
  overflow-y: visible; /* 위로 띄운 썸네일 잘림 방지 */
  scroll-behavior: smooth;
  padding-top: 0px;
  /* 스크롤바 숨김 */
  &::-webkit-scrollbar { display: none; }
  scrollbar-width: none;
}

.deck {
  --deck-gap: 14px;
  --thumb-width: 150px;
  display: flex;
  gap: var(--deck-gap);
  /* 위아래 패딩 조금 줘서 focus 짤림 방지 */
  padding: 24px 2px 0px; /* 상단 여유 확보 */
}

.thumb {
  position: relative;
  flex: 0 0 var(--thumb-width);
  width: var(--thumb-width);
  aspect-ratio: 2 / 3; /* 포스터 비율 유지 */
  border-radius: 8px;
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
  box-sizing: border-box;
  transform: translateY(-22px);
  box-shadow: 0 20px 32px rgba(0, 0, 0, 0.35);
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

.status-icon {
  font-size: 40px; /* 1.5x 확대 */
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
    --thumb-min: 120px;
    --thumb-max: 140px;
  }
}
</style>
