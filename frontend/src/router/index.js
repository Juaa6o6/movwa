import { createRouter, createWebHistory } from "vue-router"
import { routes } from "./routes"

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta?.requiresAuth) {
    const token = localStorage.getItem("accessToken")
    if (!token) return "/"
  }
})

export default router
