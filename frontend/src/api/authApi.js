import http from "@/api/http"

// [U-02]
export const authApi = {
  login(payload) {
    return http.post("/api/v1/users/login/", payload)
  },
  me() {
    return http.get("/api/v1/users/me/")
  },
}
