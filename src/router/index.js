import { createRouter, createWebHistory } from "vue-router";
import { useStore } from "vuex";

const HomePage = () => import("@/views/HomePage.vue");
const AccommodationList = () => import("@/views/AccommodationList.vue");
const MapSearch = () => import("@/views/MapSearch.vue");
const ProfilePage = () => import("@/views/ProfilePage.vue");
const FavoritesPage = () => import("@/views/FavoritesPage.vue");
const SubletPage = () => import("@/views/SubletPage.vue");
const LoginPage = () => import("@/views/LoginPage.vue");
const AuthCallback = () => import("@/views/AuthCallback.vue");
const ResetPasswordPage = () => import("@/views/ResetPasswordPage.vue");
const ChatRoom = () => import("@/components/ChatRoom.vue");

const AdminLayout = () => import("@/components/admin/AdminLayout.vue");
const AdminDashboard = () => import("@/views/admin/AdminDashboard.vue");
const TableView = () => import("@/components/admin/TableView.vue");
const UserManagement = () =>
  import("@/components/admin/UserManagementPage.vue");
const AdminLoginPage = () => import("@/views/admin/AdminLoginPage.vue");
const ReportsManagementPage = () =>
  import("@/components/admin/ReportsManagementPage.vue");
const CommentManagementPage = () =>
  import("@/components/admin/CommentManagementPage.vue");
const AdminSettingsPage = () => import("@/views/admin/AdminSettingsPage.vue");

const LandLordVerificationPage = () =>
  import("@/views/landlord/LandlordVerificationPage.vue");

const NotFound = () => import("@/views/NotFound.vue");

const routes = [
  {
    path: "/",
    name: "home",
    component: HomePage,
    meta: { transition: "fade", requiresAuth: false },
  },
  {
    path: "/login",
    name: "login",
    component: LoginPage,
    meta: { transition: "fade", requiresAuth: false },
  },
  {
    path: "/accommodation-list",
    name: "accommodation-list",
    component: AccommodationList,
    meta: { transition: "fade", requiresAuth: true },
  },
  {
    path: "/map-search",
    name: "map-search",
    component: MapSearch,
    meta: { transition: "fade", requiresAuth: true },
  },
  {
    path: "/profile",
    name: "profile",
    component: ProfilePage,
    meta: { transition: "fade", requiresAuth: true },
  },
  {
    path: "/favorites",
    name: "favorites",
    component: FavoritesPage,
    meta: { transition: "fade", requiresAuth: true },
  },
  {
    path: "/sublet",
    name: "sublet",
    component: SubletPage,
    meta: { transition: "fade", requiresAuth: true },
  },
  {
    path: "/auth/callback",
    name: "AuthCallback",
    component: AuthCallback,
    meta: { requiresAuth: false },
  },
  {
    path: "/reset-password",
    name: "ResetPassword",
    component: ResetPasswordPage,
    meta: { title: "重設密碼", requiresAuth: false },
  },

  // 管理員登入
  {
    path: "/admin/login",
    name: "AdminLogin",
    component: AdminLoginPage,
    meta: { requiresAuth: false, requiresAdmin: false },
  },

  {
    path: "/chatroom",
    name: "ChatRoom",
    component: ChatRoom,
    meta: {
      requiresAuth: true,
    },
  },

  // 管理後台路由
  {
    path: "/admin",
    component: AdminLayout,
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: "",
        name: "AdminDashboard",
        component: AdminDashboard,
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: "users",
        name: "UserManagement",
        component: UserManagement,
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: "tables/:tableName",
        name: "TableView",
        component: TableView,
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: "reports",
        name: "ReportsManagement",
        component: ReportsManagementPage,
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: "settings",
        name: "AdminSettings",
        component: AdminSettingsPage,
        meta: { requiresAuth: true, requiresAdmin: true },
      },
      {
        path: "comments",
        name: "CommentManagement",
        component: CommentManagementPage,
        meta: { requiresAuth: true, requiresAdmin: true },
      },
    ],
  },
  {
    path: "/landlord",
    name: "LandlordVerification",
    component: LandLordVerificationPage,
    meta: { requiresAuth: false, requiresAdmin: false },
  },
  {
    path: "/:catchAll(.*)",
    name: "NotFound",
    component: NotFound,
    meta: { requiresAuth: false },
  },
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const userStr = localStorage.getItem("user") || sessionStorage.getItem("user");
  const isLoggedIn = !!userStr;

  // 探查是否已登入
  let isAdmin = false;
  if (isLoggedIn) {
    try {
      const user = JSON.parse(userStr);
      isAdmin = ["admin", "superuser"].includes(user.user_role);
    } catch (error) {
      console.error("解析用戶資料時發生錯誤:", error);
    }
  }

  // 如果路由需要管理員權限
  if (to.meta.requiresAdmin) {
    if (!isLoggedIn) {
      next("/admin/login");
      return;
    }

    if (!isAdmin) {
      // 如果不是管理員，嘗試從後端獲取狀態
      try {
        const response = await fetch(
          `${
            process.env.VUE_APP_API_BASE_URL || "http://localhost:5000"
          }/api/auth/status`,
          {
            credentials: "include",
          }
        );

        if (response.ok) {
          const data = await response.json();
          if (
            data.authenticated &&
            ["admin", "superuser"].includes(data.user.user_role)
          ) {
            isAdmin = true;
          }
        }
      } catch (apiError) {
        console.error("獲取用戶狀態時出錯:", apiError);
      }

      if (!isAdmin) {
        // 確認非管理員，重定向到管理員登入頁面
        localStorage.removeItem("user");
        sessionStorage.removeItem("user");
        next("/admin/login");
        return;
      }
    }

    // 是管理員，允許訪問
    next();
    return;
  }

  // 處理需要普通用戶認證的路由
  if (to.meta.requiresAuth && !isLoggedIn) {
    // 用戶未登入但嘗試訪問需要認證的頁面
    // 重定向到登入頁面，並將目標頁面作為查詢參數
    next({
      path: "/login",
      query: { redirect: to.fullPath },
    });
  } else {
    // 用戶已登入或頁面不需要認證
    next();
  }
});

router.afterEach((to) => {
  // 根據路由名稱映射到 CircleNavigation 使用的標識符
  const routeMapping = {
    home: "home",
    "accommodation-list": "accommodation-list",
    "map-search": "map-search",
    profile: "profile",
    favorites: "favorites",
    sublet: "sublet",
  };

  // 獲取當前路由名稱，轉為小寫以避免大小寫問題
  const routeName = to.name ? to.name.toLowerCase() : "";

  // 如果是主要導航路由，更新 store 中的當前路由
  if (routeMapping[routeName]) {
    const store = useStore();
    if (store) {
      store.commit("SET_CURRENTROUTE", routeMapping[routeName]);
    }
  }
});

export default router;
