import { createRouter, createWebHistory } from 'vue-router'

// 1. 컴포넌트들을 상단에서 미리 가져옵니다. (가독성 UP)
import LandingView from '@/views/auth/LandingView.vue'
import LoginView from '@/views/auth/LoginView.vue'
import SignupView from '@/views/auth/SignupView.vue'
import HomeView from '@/views/home/HomeView.vue'
import MovieDetailView from '@/views/movie_detail/MovieDetailView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'LandingView',
      component: LandingView,
      meta: { layout: 'auth' },
    },
    {
      path: '/login',
      name: 'LoginView',
      component: LoginView,
      meta: { layout: 'auth' },
    },
    {
      path: '/signup',
      name: 'SignupView',
      component: SignupView,
      meta: { layout: 'auth' },
    },
    {
      path: '/home',
      name: 'HomeView',
      component: HomeView,
      meta: { layout: 'default', requiresAuth: true },
    },
    {
      // 1. 주소 변경: 에러 났던 주소랑 똑같이 맞춤
      path: '/movie/:id', 
      name: 'MovieDetail',
      component: MovieDetailView,
      props: true,
      // 2. 메타 추가: 헤더도 나오고, 로그인 검사도 하게 설정
      meta: { layout: 'default', requiresAuth: true }, 
    },
  ],
})

// 2. 네비게이션 가드 (로그인 체크 로직)
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('accessToken')

    if (!token) {
      return next('/')
    }
  }

  next()
})

export default router