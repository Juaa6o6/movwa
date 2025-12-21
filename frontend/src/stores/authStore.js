import { defineStore } from "pinia"
import { authApi } from "@/api/authApi"

const USE_MOCK_LOGIN = true // 여기

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    loading: false,
    error: null,
  }),
  actions: {
    async login(payload) {
      this.loading = true
      this.error = null
      try {
        // 여기
        if (USE_MOCK_LOGIN) {
          await new Promise((r) => setTimeout(r, 500))
          localStorage.setItem("accessToken", "temp-token")
          localStorage.setItem("refreshToken", "temp-refresh")
          this.user = { email: payload.email }
          return { ok: true }
        }

        const res = await authApi.login(payload)
        const { access, refresh, user } = res.data

        localStorage.setItem("accessToken", access)
        localStorage.setItem("refreshToken", refresh)
        this.user = user

        return { ok: true }
      } catch (e) {
        const msg = e?.response?.data?.detail || "로그인 실패"
        this.error = msg
        return { ok: false, message: msg }
      } finally {
        this.loading = false
      }
    },
    logout() {
      localStorage.removeItem("accessToken")
      localStorage.removeItem("refreshToken")
      this.user = null
    },
  },
})
