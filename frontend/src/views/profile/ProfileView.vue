<template>
  <v-container class="py-10" fluid>
    <div class="profile-wrapper">
      <v-card class="profile-card" elevation="0">
        <div class="profile-header">
          <v-avatar size="84" class="profile-avatar">
            <img v-if="profileImageUrl" :src="profileImageUrl" alt="profile" />
            <v-icon v-else icon="mdi-account" size="32" color="grey-darken-1"></v-icon>
          </v-avatar>
          <div class="profile-info">
            <div class="profile-name">{{ profileNickname }}</div>
            <div class="profile-username">@{{ profileUsername }}</div>
            <div class="profile-bio">{{ profileBio }}</div>
          </div>
        </div>

        <div class="profile-actions">
          <v-btn variant="tonal" class="action-btn" size="small" @click="openEditDialog">
            프로필 수정
          </v-btn>
          <v-btn variant="tonal" class="action-btn" size="small" @click="openShareDialog">
            프로필 공유
          </v-btn>
        </div>

        <div class="profile-follows">
          <div class="follow-item clickable" @click="goToFollowings">
            <div class="follow-count">{{ followingsCount }}</div>
            <div class="follow-label">팔로우</div>
          </div>
          <div class="follow-divider"></div>
          <div class="follow-item clickable" @click="goToFollowers">
            <div class="follow-count">{{ followersCount }}</div>
            <div class="follow-label">팔로워</div>
          </div>
        </div>

        <div class="profile-library">
          <div class="library-title">보관함</div>
          <div class="library-items">
            <div class="library-item clickable" @click="goToSavedLibrary">
              <div class="library-count">{{ savedCount }}</div>
              <div class="library-label">나중에 볼 영화</div>
            </div>
            <div class="library-item clickable" @click="goToRatedLibrary">
              <div class="library-count">{{ ratedCount }}</div>
              <div class="library-label">평가한 영화</div>
            </div>
            <div class="library-item clickable" @click="goToReviews">
              <div class="library-count">{{ reviewCount }}</div>
              <div class="library-label">리뷰</div>
            </div>
          </div>
        </div>
      </v-card>

      <v-card class="calendar-card" elevation="0">
        <div class="calendar-header">
          <div class="calendar-title">캘린더</div>
          <div class="calendar-controls">
            <v-btn variant="outlined" size="small" class="today-btn" @click="goToToday">오늘</v-btn>
          </div>
        </div>

        <div class="calendar-month">
          <v-btn icon="mdi-chevron-left" variant="text" size="small" @click="changeMonth(-1)"></v-btn>
          <div class="month-label">{{ monthLabel }}</div>
          <v-btn icon="mdi-chevron-right" variant="text" size="small" @click="changeMonth(1)"></v-btn>
        </div>

        <div class="calendar-weekdays">
          <div v-for="day in weekDays" :key="day" class="weekday">
            {{ day }}
          </div>
        </div>

        <div class="calendar-grid">
          <div
            v-for="cell in calendarCells"
            :key="cell.key"
            class="calendar-cell"
            :class="{ 'is-today': cell.isToday }"
          >
            <span v-if="cell.day && !cell.posterPath" class="day-number">{{ cell.day }}</span>
            <div v-if="cell.posterPath" class="calendar-poster">
              <img :src="getPosterUrl(cell.posterPath)" alt="poster" />
            </div>
          </div>
        </div>
      </v-card>
    </div>

    <v-dialog v-model="isEditDialogOpen" max-width="420">
      <v-card class="profile-edit-card">
        <div class="edit-header">
          <v-btn
            icon="mdi-close"
            variant="text"
            size="small"
            class="edit-close"
            @click="isEditDialogOpen = false"
          ></v-btn>
          <div class="edit-title">프로필 수정</div>
        </div>
        <div class="edit-avatar">
          <div class="avatar-frame">
            <v-avatar size="84" class="edit-avatar-image">
              <img v-if="editAvatarUrl" :src="editAvatarUrl" alt="profile" />
              <v-icon v-else icon="mdi-account" size="32" color="grey-darken-1"></v-icon>
            </v-avatar>
            <v-btn icon="mdi-camera" class="avatar-upload" size="x-small" @click="triggerAvatarUpload"></v-btn>
            <input
              ref="avatarInput"
              type="file"
              accept="image/*"
              class="sr-only"
              @change="handleAvatarChange"
            />
          </div>
        </div>
        <div class="edit-body">
          <div class="edit-field">
            <div class="field-label">별명</div>
            <v-text-field
              v-model="editForm.nickname"
              variant="underlined"
              density="compact"
              hide-details
              placeholder="닉네임을 입력해주세요."
              maxlength="20"
            ></v-text-field>
            <div class="field-count">{{ editForm.nickname.length }}/20</div>
          </div>
          <div class="edit-field">
            <div class="field-label">소개</div>
            <v-textarea
              v-model="editForm.bio"
              variant="underlined"
              density="compact"
              rows="2"
              hide-details
              placeholder="소개글을 입력해주세요."
              maxlength="60"
            ></v-textarea>
            <div class="field-count">{{ editForm.bio.length }}/60</div>
          </div>
          <v-btn class="edit-submit" variant="flat" block @click="submitProfileUpdate">
            확인
          </v-btn>
        </div>
      </v-card>
    </v-dialog>

    <v-dialog v-model="isShareDialogOpen" max-width="360">
      <v-card class="share-card">
        <div class="share-title">알림</div>
        <div class="share-message">프로필 링크가 복사되었습니다</div>
        <v-btn variant="text" class="share-confirm" @click="isShareDialogOpen = false">
          확인
        </v-btn>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useLibraryStore } from '@/stores/libraryStore';
import accountsApi from '@/api/accountsApi';
import reviewsApi from '@/api/reviewsApi';
import moviesApi from '@/api/moviesApi';

const weekDays = ['일', '월', '화', '수', '목', '금', '토'];
const viewDate = ref(new Date());
const ratedLogs = ref([]);

const monthLabel = computed(() => {
  const year = viewDate.value.getFullYear();
  const month = viewDate.value.getMonth() + 1;
  return `${year}.${String(month).padStart(2, '0')}`;
});

const ratedPosterByDate = computed(() => {
  const map = new Map();
  ratedLogs.value.forEach((log) => {
    if (!log?.updated_at || !log?.movie?.poster_path) return;
    const date = new Date(log.updated_at);
    const key = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
    const existing = map.get(key);
    if (!existing || new Date(log.updated_at) > new Date(existing.updated_at)) {
      map.set(key, log);
    }
  });
  return map;
});

const calendarCells = computed(() => {
  const year = viewDate.value.getFullYear();
  const monthIndex = viewDate.value.getMonth();
  const firstDay = new Date(year, monthIndex, 1).getDay();
  const daysInMonth = new Date(year, monthIndex + 1, 0).getDate();
  const totalCells = 42;
  const cells = [];
  const today = new Date();

  for (let i = 0; i < totalCells; i += 1) {
    const dayNumber = i - firstDay + 1;
    const day = dayNumber > 0 && dayNumber <= daysInMonth ? dayNumber : null;
    const key = day ? `${year}-${monthIndex + 1}-${day}` : null;
    const log = key ? ratedPosterByDate.value.get(key) : null;
    const isToday =
      day &&
      year === today.getFullYear() &&
      monthIndex === today.getMonth() &&
      day === today.getDate();

    cells.push({
      key: `cell-${i}`,
      day,
      posterPath: log?.movie?.poster_path || null,
      isToday,
    });
  }

  return cells;
});

const router = useRouter();
const isEditDialogOpen = ref(false);
const isShareDialogOpen = ref(false);
const editForm = ref({
  nickname: '',
  bio: '',
});
const authStore = useAuthStore();
const libraryStore = useLibraryStore();
const profileData = ref(null);
const reviewCount = ref(0);
const avatarInput = ref(null);
const avatarFile = ref(null);
const avatarPreview = ref('');

const profileNickname = computed(() => profileData.value?.nickname ?? authStore.user?.nickname ?? 'nickname');
const profileUsername = computed(() => profileData.value?.username ?? authStore.user?.username ?? 'username');
const profileBio = computed(() => profileData.value?.bio ?? authStore.user?.bio ?? '자기 소개');
const profileImageUrl = computed(() => profileData.value?.profile_image_url ?? authStore.user?.profile_image_url ?? null);
const editAvatarUrl = computed(() => avatarPreview.value || profileImageUrl.value || null);
const followersCount = computed(() => profileData.value?.followers_count ?? 0);
const followingsCount = computed(() => profileData.value?.following_count ?? 0);
const savedCount = computed(() => libraryStore.savedMovies.length);
const ratedCount = computed(() => libraryStore.ratedMoviesRaw.length);

const openEditDialog = () => {
  editForm.value = {
    nickname: profileNickname.value === 'nickname' ? '' : profileNickname.value,
    bio: profileBio.value === '자기 소개' ? '' : profileBio.value,
  };
  avatarFile.value = null;
  if (avatarPreview.value) {
    URL.revokeObjectURL(avatarPreview.value);
  }
  avatarPreview.value = '';
  isEditDialogOpen.value = true;
};

const openShareDialog = async () => {
  const shareUrl = `${window.location.origin}/profile`;
  try {
    await navigator.clipboard.writeText(shareUrl);
  } catch (err) {
    console.warn('프로필 링크 복사 실패:', err);
  }
  isShareDialogOpen.value = true;
};

const changeMonth = (delta) => {
  const next = new Date(viewDate.value);
  next.setMonth(next.getMonth() + delta);
  viewDate.value = next;
};

const goToToday = () => {
  viewDate.value = new Date();
};

const goToFollowings = () => {
  router.push('/profile/followings');
};

const goToFollowers = () => {
  router.push('/profile/followers');
};

const goToReviews = () => {
  router.push('/profile/reviews');
};

const triggerAvatarUpload = () => {
  avatarInput.value?.click();
};

const handleAvatarChange = (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  avatarFile.value = file;
  if (avatarPreview.value) {
    URL.revokeObjectURL(avatarPreview.value);
  }
  avatarPreview.value = URL.createObjectURL(file);
};

const submitProfileUpdate = async () => {
  try {
    const formData = new FormData();
    formData.append('nickname', editForm.value.nickname ?? '');
    formData.append('bio', editForm.value.bio ?? '');
    if (avatarFile.value) {
      formData.append('profile_image', avatarFile.value);
    }

    const res = await accountsApi.updateProfile(formData);
    profileData.value = { ...(profileData.value || {}), ...res.data };
    if (authStore.user) {
      authStore.user = { ...authStore.user, ...res.data };
    }
    await loadProfile();
    isEditDialogOpen.value = false;
  } catch (err) {
    console.error('프로필 업데이트 실패:', err);
  }
};

const goToSavedLibrary = () => {
  router.push({ path: '/library', query: { tab: 'saved' } });
};

const goToRatedLibrary = () => {
  router.push({ path: '/library', query: { tab: 'rated' } });
};

const loadProfile = async () => {
  try {
    if (!authStore.user) {
      await authStore.fetchUser();
    }
    const username = authStore.user?.username;
    if (!username) return;
    const res = await accountsApi.getUserDetail(username);
    profileData.value = res.data;
    if (authStore.user) {
      authStore.user = { ...authStore.user, ...res.data };
    }
  } catch (err) {
    console.error('프로필 정보 조회 실패:', err);
  }
};

const loadCounts = async () => {
  try {
    await Promise.all([libraryStore.fetchSavedMovies(), libraryStore.fetchRatedMovies()]);
  } catch (err) {
    console.error('보관함 데이터 조회 실패:', err);
  }

  try {
    const res = await reviewsApi.getMyReviews();
    if (Array.isArray(res.data)) {
      reviewCount.value = res.data.length;
    } else {
      reviewCount.value = res.data?.count ?? res.data?.results?.length ?? 0;
    }
  } catch (err) {
    console.error('리뷰 개수 조회 실패:', err);
  }
};

const loadRatedLogs = async () => {
  try {
    const res = await moviesApi.getRatedMovieLogs();
    ratedLogs.value = Array.isArray(res.data) ? res.data : [];
  } catch (err) {
    console.error('평가 로그 조회 실패:', err);
  }
};

const getPosterUrl = (posterPath) => {
  if (!posterPath) return '';
  if (posterPath.startsWith('http')) return posterPath;
  return `https://image.tmdb.org/t/p/w300${posterPath}`;
};

loadProfile();
loadCounts();
loadRatedLogs();
</script>

<style scoped>
.profile-wrapper {
  --side-gap: clamp(24px, 6vw, 80px);
  max-width: 760px;
  width: min(760px, calc(100% - (var(--side-gap) * 2)));
  margin: 0 auto;
  display: grid;
  gap: 24px;
}

.profile-card,
.calendar-card {
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  padding: 20px 24px;
}

.profile-header {
  display: flex;
  gap: 16px;
  align-items: center;
}

.profile-avatar {
  background: #f2f2f2;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.edit-avatar-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
}

.profile-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.profile-name {
  font-size: 1.15rem;
  font-weight: 700;
}

.profile-username,
.profile-bio {
  font-size: 0.85rem;
  color: #6b7280;
}

.profile-actions {
  margin-top: 18px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  padding: 0 6px;
}

.action-btn {
  background: #f3f4f6;
  min-height: 44px;
  font-size: medium;
  font-weight: 700;
}

.profile-follows {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  text-align: center;
  padding: 0 6px;
}

.follow-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.follow-divider {
  width: 1px;
  height: 36px;
  background: #d1d5db;
  margin: 0 12px;
}

.follow-count {
  font-weight: 700;
}

.follow-label {
  font-size: 0.8rem;
  color: #6b7280;
}

.profile-library {
  margin-top: 18px;
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.library-title {
  font-weight: 700;
  margin-bottom: 12px;
}

.library-items {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  padding: 0 6px;
}

.library-item {
  text-align: center;
}

.library-count {
  width: 56px;
  height: 56px;
  border: 2px solid #9ca3af;
  border-radius: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  margin: 0 auto 8px;
}

.library-label {
  font-size: 0.8rem;
  color: #6b7280;
  font-weight: 700;
}

.clickable {
  cursor: pointer;
}

.calendar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.calendar-title {
  font-weight: 700;
}

.calendar-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.today-btn {
  border-radius: 8px;
}

.calendar-month {
  margin-top: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-weight: 700;
}

.month-label {
  min-width: 80px;
  text-align: center;
}

.calendar-weekdays {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  text-align: center;
  color: #6b7280;
  font-size: 0.85rem;
}

.calendar-grid {
  margin-top: 8px;
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.calendar-cell {
  min-height: 140px;
  padding: 0;
  border-radius: 0;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.day-number {
  font-size: 0.9rem;
  color: #6b7280;
}

.calendar-poster {
  position: absolute;
  inset: 0;
  border-radius: 0;
  overflow: hidden;
  box-shadow: none;
}

.calendar-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.is-today .day-number {
  color: #fff;
  background: #e11d48;
  border-radius: 999px;
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.profile-edit-card {
  border-radius: 16px;
  overflow: hidden;
}

.edit-header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 14px 16px;
  border-bottom: 1px solid #f3f4f6;
  font-weight: 700;
}

.edit-close {
  position: absolute;
  left: 8px;
  top: 6px;
  color: #f43f5e;
}

.edit-title {
  font-size: 1rem;
}

.edit-avatar {
  padding: 20px 24px 0;
  display: flex;
  justify-content: center;
}

.avatar-frame {
  width: 120px;
  height: 120px;
  border-radius: 16px;
  background: #eff6ff;
  border: 1px solid #dbeafe;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

.avatar-upload {
  position: absolute;
  right: 8px;
  bottom: 8px;
  background: #fff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.edit-body {
  padding: 16px 24px 20px;
  display: grid;
  gap: 12px;
}

.edit-field {
  display: grid;
  gap: 4px;
}

.field-label {
  font-size: 0.85rem;
  font-weight: 700;
  color: #6b7280;
}

.field-count {
  text-align: right;
  font-size: 0.75rem;
  color: #9ca3af;
}

.edit-submit {
  margin-top: 4px;
  background: #e5e7eb;
  color: #6b7280;
  font-weight: 700;
  border-radius: 10px;
  text-transform: none;
}

.share-card {
  padding: 20px;
  text-align: center;
  border-radius: 16px;
}

.share-title {
  font-weight: 700;
  margin-bottom: 6px;
}

.share-message {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 12px;
}

.share-confirm {
  color: #2563eb;
  font-weight: 700;
}

.share-confirm:hover {
  background-color: rgba(37, 99, 235, 0.08);
}

.share-confirm:active {
  background-color: rgba(37, 99, 235, 0.16);
}
</style>
