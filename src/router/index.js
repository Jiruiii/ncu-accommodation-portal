import { createRouter, createWebHistory } from "vue-router";

const HomePage = () => import("@/views/HomePage.vue");
const AccommodationList = () => import("@/views/AccommodationList.vue");
const MapSearch = () => import("@/views/MapSearch.vue");
const ProfilePage = () => import("@/views/ProfilePage.vue");
const FavoritesPage = () => import("@/views/FavoritesPage.vue");
const SubletPage = () => import("@/views/SubletPage.vue");
const LoginPage = () => import("@/views/LoginPage.vue");
const AuthCallback = () => import("@/views/AuthCallback.vue");

const routes = [
  {
    path: "/",
    name: "home",
    component: HomePage,
    meta: { transition: "fade" },
  },
  {
    path: "/login",
    name: "login",
    component: LoginPage,
    meta: { transition: "fade" },
  },
  {
    path: "/accommodation-list",
    name: "accommodation-list",
    component: AccommodationList,
    meta: { transition: "fade" },
  },
  {
    path: "/map-search",
    name: "map-search",
    component: MapSearch,
    meta: { transition: "fade" },
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfilePage,
    meta: { transition: "fade" },
  },
  {
    path: "/favorites",
    name: "favorites",
    component: FavoritesPage,
    meta: { transition: "fade" },
  },
  {
    path: "/sublet",
    name: "sublet",
    component: SubletPage,
    meta: { transition: "fade" },
  },
  {
    path: "/auth/callback",
    name: "AuthCallback",
    component: AuthCallback,
    meta: {
      requiresAuth: false,
    },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
