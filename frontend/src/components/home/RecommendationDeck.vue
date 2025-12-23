<template>
  <div class="deck-container">
    <div class="deck">
      <div
        v-for="(m, idx) in movies"
        :key="m.id ?? idx"
        class="thumb"
        :class="{ 
          selected: idx === currentIndex,
          'is-rated': m.status // 평가된 영화 스타일 처리
        }"
        @click="$emit('select', idx)"
      >
        <img :src="posterUrl(m)" alt="movie poster" loading="lazy" />
        
        <div v-if="m.status" class="status-overlay">
          <v-icon v-if="m.status === 'liked'" color="red-accent-2" size="large">
            mdi-heart
          </v-icon>
          <v-icon v-if="m.status === 'passed'" color="grey-lighten-1" size="large">
            mdi-close
          </v-icon>
          <div v-if="m.status === 'rated'" class="d-flex flex-column align-center">
            <v-icon color="yellow-accent-4" size="large">mdi-star</v-icon>
            <span class="text-caption font-weight-bold text-white">{{ m.rating }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Props
const props = defineProps({
  movies: { type: Array, default: () => [] },
  currentIndex: { type: Number, default: 0 },
});

// Emits
defineEmits(["select"]);

// Methods
const posterUrl = (m) => {
  const path = m?.poster_path;
  if (!path) return "https://via.placeholder.com/120x180?text=No+Img";
  return `https://image.tmdb.org/t/p/w342${path}`;
};
</script>

<style scoped>
.deck-container {
  width: 100%;
  overflow: hidden; /* 컨테이너 밖으로 스크롤바 안 보이게 */
}

.deck {
  margin-top: 14px;
  display: flex;
  gap: 12px;
  padding: 10px 20px 20px 20px; /* 하단 패딩 여유 있게 */
  overflow-x: auto;
  scroll-behavior: smooth;
  
  /* 스크롤바 숨기기 (크롬, 사파리, 엣지) */
  &::-webkit-scrollbar {
    display: none;
  }
  /* 스크롤바 숨기기 (파이어폭스) */
  scrollbar-width: none;
}

.thumb {
  position: relative; /* 오버레이 위치 잡기 위해 필수 */
  width: 100px;       /* 크기 살짝 키움 */
  height: 150px;
  border-radius: 12px;
  overflow: hidden;
  opacity: 0.6;
  flex: 0 0 auto;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;
}

/* 선택된 상태 */
.thumb.selected {
  opacity: 1;
  transform: translateY(-12px) scale(1.05); /* 위로 올라오면서 살짝 커짐 */
  box-shadow: 0 10px 20px rgba(0,0,0,0.5); /* 그림자 강조 */
  border: 2px solid white; /* 테두리 명확하게 */
  z-index: 2;
}

/* REC-03: 상태 오버레이 디자인 */
.status-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7); /* 배경 어둡게 */
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px); /* 블러 처리로 고급스럽게 */
  z-index: 1;
}
</style>