<template>
  <div class="text-black">
    
    <h3 class="text-h5 font-weight-bold mb-3">줄거리</h3>
    <p class="text-body-1 text-grey-darken-3 mb-8" style="line-height: 1.6;">
      {{ movie.overview || '줄거리 정보가 없습니다.' }}
    </p>

    <div v-if="director" class="mb-8">
      <h3 class="text-h5 font-weight-bold mb-4">감독</h3>
      <div class="d-flex align-center">
        <v-avatar size="80" class="mb-2 elevation-2 mr-4">
          <v-img 
            :src="director.profile_path ? `https://image.tmdb.org/t/p/w185${director.profile_path}` : 'https://via.placeholder.com/100x100?text=No+Image'" 
            cover
          ></v-img>
        </v-avatar>
        <div>
          <div class="text-subtitle-1 font-weight-bold">{{ director.name }}</div>
          <div class="text-caption text-grey-darken-1">Director</div>
        </div>
      </div>
    </div>

    <h3 class="text-h5 font-weight-bold mb-4">출연진</h3>
    
    <v-row v-if="castList && castList.length > 0">
      <v-col 
        cols="6" sm="4" md="3" lg="2" 
        v-for="person in castList.slice(0, 6)" 
        :key="person.id"
        class="text-center"
      >
        <v-avatar size="80" class="mb-2 elevation-2">
          <v-img 
            :src="person.profile_path ? `https://image.tmdb.org/t/p/w185${person.profile_path}` : 'https://via.placeholder.com/100x100?text=No+Image'" 
            cover
          ></v-img>
        </v-avatar>
        <div class="text-subtitle-2 font-weight-bold text-truncate">{{ person.name }}</div>
        <div class="text-caption text-grey-darken-1 text-truncate">{{ person.character }}</div>
      </v-col>
    </v-row>
    <div v-else class="text-grey text-body-2">출연진 정보가 없습니다.</div>

  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  movie: Object,
  castList: Array,
  crewList: Array // ✨ 제작진 리스트 받기
});

// ✨ crewList에서 직업이 'Director'인 사람 찾기
const director = computed(() => {
  if (!props.crewList) return null;
  return props.crewList.find(person => person.job === 'Director');
});
</script>