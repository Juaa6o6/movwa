import axios from "axios"

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const http = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json'},
  withCredentials: true,
})

let isRefreshing = false
let refreshQueue = []

const processQueue = (error, token = null) => {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  refreshQueue = []
}

http.interceptors.request.use((config) => {
  const access = localStorage.getItem("accessToken")
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status

    if (status !== 401 || originalRequest._retry) {
      return Promise.reject(error)
    }

    if (originalRequest.url?.includes("/api/v1/auth/token/refresh/")) {
      return Promise.reject(error)
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        refreshQueue.push({ resolve, reject })
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`
        return http(originalRequest)
      })
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      const refreshRes = await axios.post(
        `${API_BASE_URL}/api/v1/auth/token/refresh/`,
        {},
        { withCredentials: true }
      )
      const newAccess = refreshRes.data?.access
      if (!newAccess) {
        throw new Error("Refresh response missing access token")
      }

      localStorage.setItem("accessToken", newAccess)
      processQueue(null, newAccess)
      originalRequest.headers.Authorization = `Bearer ${newAccess}`
      return http(originalRequest)
    } catch (refreshError) {
      processQueue(refreshError, null)
      localStorage.removeItem("accessToken")
      return Promise.reject(refreshError)
    } finally {
      isRefreshing = false
    }
  }
)

export default http
