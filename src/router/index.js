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
const ChatRoom = () => import("@/views/admin/ChatRoom.vue");
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
    path: "/admin/login",
    name: "AdminLogin",
    component: AdminLoginPage,
    meta: { requiresAdmin: false },
  },

  {
    path: "/chatroom",
    name: "ChatRoom",
    component: ChatRoom,
    meta: {
      requiresAuth: false,
    },
  },

  // 管理後台路由
  {
    path: "/admin",
    component: () => import("@/components/admin/AdminLayout.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: "",
        name: "AdminDashboard",
        component: AdminDashboard,
        meta: { requiresAdmin: true },
      },
      {
        path: "users",
        name: "UserManagement",
        component: UserManagement,
        meta: { requiresAdmin: true },
      },
      {
        path: "tables/:tableName",
        name: "TableView",
        component: TableView,
        meta: { requiresAdmin: true },
      },
    ],
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

router.beforeEach(async (to, from, next) => {
  // 如果路由需要管理員權限
  if (to.meta.requiresAdmin) {
    try {
      // 檢查用戶是否登入以及是否有管理員權限
      const userStr =
        localStorage.getItem("user") || sessionStorage.getItem("user");
      let isAdmin = false;

      if (userStr) {
        const user = JSON.parse(userStr);
        isAdmin = ["admin", "superuser"].includes(user.user_role);
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
          // 確認非管理員，清除本地存儲並重定向
          localStorage.removeItem("user");
          sessionStorage.removeItem("user");
          next("/admin/login");
          return; // 確保函數結束
        }
      }

      // 是管理員，允許訪問
      next();
    } catch (error) {
      console.error("檢查管理員權限時發生錯誤:", error);
      next("/admin/login");
      return; 
    }
  } else {
    // 非管理員頁面，正常繼續
    next();
  }
});

export default router;
