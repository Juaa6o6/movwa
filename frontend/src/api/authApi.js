import api from '@/api/http'

export default {
  // [회원가입]
  // Django: path('api/v1/auth/registration/', ...)
  signup(payload) {
    return api.post('/api/v1/auth/registration/', payload)
  },

  // [로그인]
  // Django: path('api/v1/auth/', ...) 내부의 /login/
  login(payload) {
    return api.post('/api/v1/auth/login/', payload)
  }
}