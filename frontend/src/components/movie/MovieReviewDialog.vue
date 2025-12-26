<template>
  <v-dialog v-model="internalShow" max-width="500px">
    <v-card class="pa-4 rounded-xl">
      <v-card-title class="d-flex justify-space-between align-center">
        <span class="text-h6 font-weight-bold">{{ dialogTitle }}</span>
        <v-btn icon="mdi-close" variant="text" @click="close"></v-btn>
      </v-card-title>

      <v-card-text class="text-center pt-2">
        <div class="text-h3 font-weight-bold mb-2">{{ rating.toFixed(1) }}</div>
        <v-rating
          v-model="rating"
          color="amber"
          active-color="amber"
          half-increments
          hover
          size="x-large"
          class="mb-6"
        ></v-rating>

        <v-textarea
          v-model="reviewContent"
          placeholder="이 영화에 대한 감상평을 남겨주세요."
          variant="filled"
          bg-color="grey-lighten-4"
          rows="8"
          no-resize
          hide-details
          class="rounded-lg mb-6"
        ></v-textarea>

        <v-btn
          block
          color="blue"
          size="x-large"
          rounded="lg"
          variant="flat"
          class="font-weight-bold text-white"
          @click="submitReview"
        >
          {{ submitLabel }}
        </v-btn>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch, computed } from 'vue';

const props = defineProps({
  show: Boolean,
  initialRating: {
    type: Number,
    default: 5.0
  },
  initialContent: {
    type: String,
    default: ''
  },
  isEdit: {
    type: Boolean,
    default: false
  }
});
const emit = defineEmits(['update:show', 'submit']);

const internalShow = ref(props.show);
const rating = ref(props.initialRating);
const reviewContent = ref(props.initialContent);

const dialogTitle = computed(() => (props.isEdit ? '감상평 수정하기' : '감상평 작성하기'));
const submitLabel = computed(() => (props.isEdit ? '수정하기' : '등록하기'));

// 부모의 show 상태 감시
watch(() => props.show, (newVal) => {
  internalShow.value = newVal;
  if (newVal) {
    rating.value = props.initialRating;
    reviewContent.value = props.initialContent;
  }
});

// 내부 팝업 상태 변화를 부모에게 전달
watch(internalShow, (newVal) => {
  emit('update:show', newVal);
});

const close = () => {
  internalShow.value = false;
};

const submitReview = () => {
  if (!reviewContent.value.trim()) {
    alert('리뷰 내용을 입력해주세요!');
    return;
  }
  
  emit('submit', {
    rating: rating.value,
    content: reviewContent.value
  });
  
  // 초기화 후 닫기
  reviewContent.value = props.initialContent;
  rating.value = props.initialRating;
  close();
};
</script>
