import axios from "axios"

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

http.interceptors.request.use((config) => {
  const access = localStorage.getItem("accessToken")
  if (access) config.headers.Authorization = `Bearer ${access}`
  return config
})

export default http
