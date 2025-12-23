<template>
  <div class="actions">
    <v-btn 
      class="pill-btn" 
      variant="outlined" 
      color="grey-lighten-3" 
      prepend-icon="mdi-close"
      @click="$emit('pass')"
    >
      PASS
    </v-btn>

    <v-menu v-model="menuOpen" :close-on-content-click="false" location="top center">
      <template #activator="{ props }">
        <v-btn 
          class="pill-btn" 
          variant="outlined" 
          color="white" 
          prepend-icon="mdi-star-outline"
          v-bind="props"
        >
          RATE
        </v-btn>
      </template>

      <v-card class="pa-4 rounded-xl elevation-10" width="280" color="grey-darken-4">
        <div class="d-flex justify-space-between align-center mb-2">
          <span class="text-subtitle-2 font-weight-bold text-white">이 영화 평가하기</span>
          <span class="text-h6 text-yellow-accent-4 font-weight-bold">{{ localRating }}</span>
        </div>
        
        <div class="d-flex justify-center my-2">
          <v-rating 
            v-model="localRating" 
            color="yellow-accent-4" 
            active-color="yellow-accent-4"
            half-increments 
            hover 
            length="5" 
            size="x-large"
            density="compact"
          />
        </div>

        <v-btn 
          class="mt-3 font-weight-bold" 
          block 
          color="yellow-accent-4" 
          variant="flat"
          rounded="pill"
          @click="emitRate"
        >
          등록 완료
        </v-btn>
      </v-card>
    </v-menu>

    <v-btn 
      class="pill-btn" 
      variant="flat" 
      color="red-accent-2" 
      prepend-icon="mdi-heart"
      @click="$emit('like')"
    >
      LIKE
    </v-btn>
    
    <v-btn 
      icon="mdi-bookmark-outline" 
      variant="text" 
      color="white" 
      density="comfortable"
      @click="$emit('save')"
    >
    </v-btn>
  </div>
</template>

<script setup>
import { ref } from "vue";

const emit = defineEmits(["pass", "rate", "like", "save"]);

const localRating = ref(3.5); // 기본값 3.5 정도가 적당
const menuOpen = ref(false); // 메뉴 닫기 제어용

const emitRate = () => {
  emit("rate", localRating.value);
  menuOpen.value = false; // 확인 누르면 메뉴 닫기
};
</script>

<style scoped>
.actions {
  /* position: absolute;  <-- 제거함! 부모(Hero)가 위치를 잡아줍니다. */
  display: flex;
  align-items: center;
  gap: 12px;
}

.pill-btn {
  border-radius: 999px;
  min-width: 90px; /* 너비 조금 확보 */
  font-weight: 700;
  letter-spacing: 0.5px;
  text-transform: none; /* 대문자 강제 변환 해제 (선택사항) */
  border-width: 2px; /* 외곽선 두께 */
  backdrop-filter: blur(4px); /* 배경 살짝 흐리게 해서 가독성 확보 */
}
</style>