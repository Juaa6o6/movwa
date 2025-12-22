import axios from "axios"

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  headers: { 'Content-Type': 'application/json'}
})

http.interceptors.request.use((config) => {
  const access = localStorage.getItem("accessToken")
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

export default http
