import { createRouter, createWebHistory } from "vue-router";

const HomePage = () => import("@/views/HomePage.vue");
const AccommodationList = () => import("@/views/AccommodationList.vue");
const MapSearch = () => import("@/views/MapSearch.vue");
const ProfilePage = () => import("@/views/ProfilePage.vue");
const FavoritesPage = () => import("@/views/FavoritesPage.vue");
const SubletPage = () => import("@/views/SubletPage.vue");
const LoginPage = () => import("@/views/LoginPage.vue");
const AuthCallback = () => import("@/views/AuthCallback.vue");
const AdminDashboard = () => import("@/views/admin/AdminDashboard.vue");
const TableView = () => import("@/components/admin/TableView.vue");
const UserManagement = () => import("@/components/admin/UserManagement.vue");
const AdminLoginPage = () => import("@/views/admin/AdminLoginPage.vue");
const NotFound = () => import("@/views/NotFound.vue");

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

  // 管理員登入
  {
    path: '/admin/login',
    name: 'AdminLogin',
    component: AdminLoginPage,
    meta: { requiresAuth: false }
  },
  
  // 管理後台路由
  {
    path: '/admin',
    component: () => import('@/components/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        name: 'AdminDashboard',
        component: AdminDashboard,
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: UserManagement,
      },
      {
        path: 'tables/:tableName',
        name: 'TableView',
        component: TableView,
      }
    ]
  },
  {
    path: "/:catchAll(.*)",
    name: "NotFound",
    component: NotFound,
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

export default router;
