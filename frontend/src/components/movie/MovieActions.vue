<template>
  <div class="actions d-flex align-center gap-3">
    
    <v-btn 
      rounded="pill" 
      :variant="status === 'passed' ? 'flat' : 'outlined'"
      :color="status === 'passed' ? 'grey-darken-3' : 'white'"
      class="action-btn"
      @click="$emit('pass')"
    >
      <v-icon start>mdi-close</v-icon>
      PASS
    </v-btn>

    <v-menu 
        v-model="menuOpen" 
        :close-on-content-click="false" 
        location="top center" 
        offset="10"
    >
      <template #activator="{ props }">
        <v-btn 
          rounded="pill" 
          :variant="status === 'rated' ? 'flat' : 'outlined'"
          :color="status === 'rated' ? 'yellow-accent-4' : 'white'"
          :class="['action-btn', {'text-black': status === 'rated'}]"
          v-bind="props"
        >
          <v-icon start>{{ status === 'rated' ? 'mdi-star' : 'mdi-star-outline' }}</v-icon>
          {{ status === 'rated' ? 'RATED' : 'RATE' }}
        </v-btn>
      </template>

      <v-card class="rating-card pa-4 rounded-xl elevation-10 bg-grey-darken-4" min-width="360">
        <div class="text-center mb-2 font-weight-bold text-white">별점을 선택하세요</div>
        <div class="rating-row d-flex justify-center">
          <v-rating 
            v-model="ratingValue"
            color="yellow-accent-4" 
            active-color="yellow-accent-4"
            half-increments 
            hover 
            size="large"
            @update:model-value="onRate" 
          />
        </div>
      </v-card>
    </v-menu>

    <v-btn 
      rounded="pill" 
      :variant="status === 'liked' ? 'flat' : 'outlined'"
      :color="status === 'liked' ? 'red-accent-2' : 'white'"
      class="action-btn"
      @click="$emit('like')"
    >
      <v-icon start>{{ status === 'liked' ? 'mdi-heart' : 'mdi-heart-outline' }}</v-icon>
      LIKE
    </v-btn>

  </div>
</template>

<script setup>
import { ref, watch } from "vue";

const props = defineProps({
    // 부모로부터 현재 영화의 상태를 받음 (liked, passed, rated, null)
    status: { type: String, default: null } 
});

const emit = defineEmits(["pass", "rate", "like"]);

const menuOpen = ref(false);
const ratingValue = ref(0);

// 별점 클릭 시 자동 동작 (확인 버튼 없음)
const onRate = (value) => {
    emit('rate', value); // 즉시 부모에게 알림
    menuOpen.value = false; // 메뉴 닫기
    ratingValue.value = 0; // 초기화 (옵션)
};
</script>

<style scoped>
.gap-3 { gap: 16px; }

.action-btn {
  border-width: 2px !important;
  height: 48px;
  font-weight: 800;
  padding: 0 28px;
  font-size: 1rem;
  backdrop-filter: blur(4px);
}

.rating-card {
  overflow-x: hidden;
  max-width: 100%;
}

.rating-row {
  max-width: 100%;
}

.rating-row :deep(.v-rating) {
  max-width: 100%;
  --v-rating-gap: 0px;
}

.rating-row :deep(.v-rating__wrapper) {
  gap: 0;
}

.rating-row :deep(.v-rating__item) {
  margin-inline: 0;
  padding-inline: 0;
}
</style>
