<template>
  <div class="deck-container">
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
        <img :src="posterUrl(m)" alt="movie poster" loading="lazy" />
        
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
</template>

<script setup>
// Script 부분은 기존과 동일
const props = defineProps({ movies: { type: Array, default: () => [] }, currentIndex: { type: Number, default: 0 } });
defineEmits(["select"]);
const posterUrl = (m) => { const path = m?.poster_path; if (!path) return "https://via.placeholder.com/120x180?text=No+Img"; return `https://image.tmdb.org/t/p/w342${path}`; };
</script>

<style scoped>
.deck-container {
  width: 100%;
  overflow: hidden;
}

.deck {
  margin-top: 14px;
  display: flex;
  gap: 12px;
  /* 위로 올라오는 효과를 없앴으므로 상단 패딩을 줄임 */
  padding: 4px 20px 20px 20px; 
  overflow-x: auto;
  scroll-behavior: smooth;
  &::-webkit-scrollbar { display: none; }
  scrollbar-width: none;
}

.thumb {
  position: relative;
  width: 100px;
  height: 150px;
  /* 라운드 제거 -> 각지게 표현 */
  border-radius: 0; 
  overflow: hidden;
  opacity: 0.6;
  flex: 0 0 auto;
  cursor: pointer;
  transition: all 0.2s ease; /* 속도 조절 */
  /* 그림자 제거 */
  box-shadow: none; 
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* 이미지 확대 효과도 제거 (원하시면 다시 넣어도 됩니다) */
  /* transition: transform 0.3s; */
}

/* 선택된 상태 */
.thumb.selected {
  opacity: 1;
  /* transform: translateY(-12px) scale(1.05); <- 이 줄을 제거하여 위로 올라오지 않게 함 */
  /* 그림자 제거 */
  box-shadow: none;
  /* 배경이 흰색이므로 테두리를 검은색으로 변경하여 강조 */
  outline: 3px solid #000000; 
  z-index: 2;
}

.status-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(2px);
  z-index: 1;
}
</style>