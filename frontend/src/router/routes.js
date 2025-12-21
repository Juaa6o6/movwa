export const routes = [
  {
    path: "/",
    name: "LandingView",
    component: () => import("@/views/auth/LandingView.vue"),
    meta: { layout: "auth" },
  },
  {
    path: "/login",
    name: "LoginView",
    component: () => import("@/views/auth/LoginView.vue"),
    meta: { layout: "auth" },
  },
  {
    path: "/home",
    name: "HomeView",
    component: () => import("@/views/home/HomeView.vue"),
    meta: { layout: "default", requiresAuth: true },
  },
  {
  path: "/signup",
  name: "SignupView",
  component: () => import("@/views/auth/SignupView.vue"),
  meta: { layout: "auth" },
},

]
