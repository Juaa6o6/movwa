import { defineStore } from "pinia"
import authApi from "@/api/authApi"
import router from "@/router"

const USE_MOCK_LOGIN = true 

export const useAuthStore = defineStore("auth", {
  state: () => ({
    user: null,
    loading: false,
    error: null,
    
    // 회원가입용 입력 데이터
    signupForm: {
      email: '',
      password: '',
      username: '',
      nickname: '',
      genres: []
    },
    
    tempRegisteredUser: null 
  }),

  actions: {
    async login(payload) {
      this.loading = true
      this.error = null
      try {
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
        const msg = e?.response?.data?.detail || "Login failed"
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

    // ... (login, logout은 기존 코드 유지)

    // ✅ [최종 수정] 회원가입 로직
    async signup() {
      this.loading = true
      try {
        // 💡 dj-rest-auth 요구사항에 딱 맞춘 Payload
        const payload = {
          email: this.signupForm.email,
          username: this.signupForm.username,
          
          // 옵션이지만 CustomRegisterSerializer에서 처리하므로 보냄
          nickname: this.signupForm.nickname,

          // 🔑 핵심 수정: dj-rest-auth 표준 필드명
          password1: this.signupForm.password,  // 이것이 password 1
          password2: this.signupForm.password, // 이것이 password 2 (확인용)
        }

        console.log("회원가입 요청 Payload:", payload)

        if (USE_MOCK_LOGIN) {
          await new Promise((r) => setTimeout(r, 1000))
          
          this.tempRegisteredUser = payload 
          alert(`[Mock] 회원가입 완료!\nID: ${payload.email}\nPW: ${payload.password1}`)
          
          this.signupForm = { email: '', password: '', username: '', nickname: '', genres: [] }
          return true
        }

        // 실제 API 호출 (이제 400 에러 없이 잘 들어갈 겁니다)
        await authApi.signup(payload)
        
        alert("회원가입이 완료되었습니다!")
        this.signupForm = { email: '', password: '', username: '', nickname: '', genres: [] }
        return true

      } catch (e) {
        console.error("회원가입 실패:", e)
        const msg = e.response?.data ? JSON.stringify(e.response.data) : "회원가입 중 오류가 발생했습니다."
        alert(msg)
        return false
      } finally {
        this.loading = false
      }
    }
    // ...
  },
})