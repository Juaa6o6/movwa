import { defineStore } from "pinia"
import authApi from "@/api/authApi"
import accountsApi from "@/api/accountsApi"

const USE_MOCK_LOGIN = false 

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
    // src/stores/authStore.js 내부 actions의 login 부분

    async login(payload) {
      this.loading = true
      this.error = null
      
      // 👇 어떤 데이터를 보내는지 확인
      console.log("🚀 [전송] 로그인 요청 데이터:", payload)

      try {
        if (USE_MOCK_LOGIN) {
           // ... (Mock 코드는 생략)
           return { ok: true }
        }

        const res = await authApi.login(payload)
        
        // 👇 백엔드가 뭘 줬는지 확인 (이게 제일 중요함!)
        console.log("🔥 [응답] 백엔드 응답 전체:", res)
        console.log("📦 [데이터] res.data 내용:", res.data)

        // 구조 분해 시도
        const { access, refresh, user } = res.data

        // 토큰이 잘 왔는지 확인
        if (!access) {
            console.warn("⚠️ 경고: access 토큰이 응답에 없습니다! 백엔드 설정을 확인하세요.")
            console.warn("현재 응답된 키 목록:", Object.keys(res.data))
        }

        if (access) localStorage.setItem("accessToken", access)
        
        if (user) {
          this.user = user
        } else {
          await this.fetchUser()
        }

        return { ok: true }

      } catch (e) {
        // 👇 에러가 나면 여기에 자세히 찍힘
        console.error("❌ [에러] 로그인 실패:", e)
        
        // 에러 응답이 있다면 그 내용을 보여줌
        if (e.response) {
            console.log("응답 상태 코드:", e.response.status)
            console.log("응답 데이터:", e.response.data)
            console.log("non_field_errors:", e.response.data?.non_field_errors)
        }

        const msg = e?.response?.data?.detail || 
                    e?.response?.data?.non_field_errors?.[0] || 
                    "로그인 실패 (콘솔 확인 필요)"
        this.error = msg
        return { ok: false, message: msg }
      } finally {
        this.loading = false
      }
    },
    async fetchUser() {
      try {
        const res = await authApi.getUser()
        this.user = res.data

        if (this.user?.username) {
          try {
            const detailRes = await accountsApi.getUserDetail(this.user.username)
            this.user = { ...this.user, ...detailRes.data }
          } catch (detailErr) {
            console.error("유저 상세 정보 조회 실패:", detailErr)
          }
        }
      } catch (e) {
        console.error("유저 정보 조회 실패:", e)
      }
    },

    async logout() {
      try {
        await authApi.logout()
      } catch (e) {
        console.error("로그아웃 실패:", e)
      } finally {
        localStorage.removeItem("accessToken")
        this.user = null
      }
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
