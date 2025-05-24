<template>
  <div class="admin-layout">
    <header class="admin-header">
      <div class="logo">
        <h1>中央宿舍管理系統</h1>
      </div>
      <div class="user-menu">
        <span class="username">{{ currentUser.username }}</span>
        <button class="logout-btn" @click="logout">登出</button>
      </div>
    </header>

    <div class="admin-container">
      <nav class="admin-sidebar">
        <ul class="nav-links">
          <li>
            <router-link to="/admin">
              <span class="material-symbols-outlined">dashboard</span>
              儀表板
            </router-link>
          </li>

          <li class="nav-section">
            <div class="section-title">用戶管理</div>
            <ul class="sub-menu">
              <li>
                <router-link to="/admin/users">
                  <span class="material-symbols-outlined">person</span>
                  用戶列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/verification_codes">
                  <span class="material-symbols-outlined">verified</span>
                  驗證碼
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/password_resets">
                  <span class="material-symbols-outlined">lock_reset</span>
                  密碼重置
                </router-link>
              </li>
            </ul>
          </li>

          <li class="nav-section">
            <div class="section-title">住宿管理</div>
            <ul class="sub-menu">
              <li>
                <router-link to="/admin/tables/accommodations">
                  <span class="material-symbols-outlined">home</span>
                  住所列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/accommodation_images">
                  <span class="material-symbols-outlined">image</span>
                  住所圖片
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/amenities">
                  <span class="material-symbols-outlined">bathroom</span>
                  設施列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/favorites">
                  <span class="material-symbols-outlined">favorite</span>
                  收藏記錄
                </router-link>
              </li>
            </ul>
          </li>

          <li class="nav-section">
            <div class="section-title">評論管理</div>
            <ul class="sub-menu">
              <li>
                <router-link to="/admin/comments">
                  <span class="material-symbols-outlined">comment</span>
                  評論管理
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/comments">
                  <span class="material-symbols-outlined">chat</span>
                  評論列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/replies">
                  <span class="material-symbols-outlined">reply</span>
                  回覆列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/reports">
                  <span class="material-symbols-outlined">flag</span>
                  舉報管理
                </router-link>
              </li>
            </ul>
          </li>

          <li class="nav-section">
            <div class="section-title">交易管理</div>
            <ul class="sub-menu">
              <li>
                <router-link to="/admin/tables/sublets">
                  <span class="material-symbols-outlined">swap_horiz</span>
                  轉租列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/leases">
                  <span class="material-symbols-outlined">description</span>
                  租約列表
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/maintenance">
                  <span class="material-symbols-outlined">build</span>
                  維修請求
                </router-link>
              </li>
            </ul>
          </li>

          <li class="nav-section">
            <div class="section-title">訊息系統</div>
            <ul class="sub-menu">
              <li>
                <router-link to="/admin/tables/chat_message">
                  <span class="material-symbols-outlined">chat</span>
                  聊天訊息
                </router-link>
              </li>
              <li>
                <router-link to="/admin/tables/notifications">
                  <span class="material-symbols-outlined">notifications</span>
                  系統通知
                </router-link>
              </li>
            </ul>
          </li>

          <li>
            <router-link to="/admin/settings">
              <span class="material-symbols-outlined">settings</span>
              系統設置
            </router-link>
          </li>
        </ul>
      </nav>

      <main class="admin-content">
        <div class="breadcrumb">
          <router-link to="/admin">首頁</router-link>
          <span class="separator">/</span>
          <span class="current-page">{{ getCurrentPageName() }}</span>
        </div>

        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted, computed } from "vue";
  import { useRouter, useRoute } from "vue-router";
  import apiService from "@/services/api";

  export default {
    setup() {
      const router = useRouter();
      const route = useRoute();
      const currentUser = ref({
        username: "管理員",
        user_role: "",
      });

      // 根據當前路由獲取頁面名稱
      const getCurrentPageName = () => {
        // 根據路由路徑返回對應的頁面名稱
        const path = route.path;

        if (path === "/admin") return "儀表板";
        if (path === "/admin/users") return "用戶管理";
        if (path === "/admin/reports") return "舉報管理";
        if (path === "/admin/settings") return "系統設置";

        // 解析表格路由
        if (path.startsWith("/admin/tables/")) {
          const tableName = path.split("/").pop();

          // 映射表格名稱到中文
          const tableNameMap = {
            users: "用戶列表",
            verification_codes: "驗證碼",
            password_resets: "密碼重置",
            accommodations: "住所列表",
            accommodation_images: "住所圖片",
            amenities: "設施列表",
            accommodation_amenities: "住所設施",
            favorites: "收藏記錄",
            comments: "評論列表",
            replies: "回覆列表",
            comment_likes: "評論點讚",
            reports: "舉報記錄",
            sublets: "轉租列表",
            leases: "租約列表",
            maintenance: "維修請求",
            chat_message: "聊天訊息",
            notifications: "系統通知",
          };

          return tableNameMap[tableName] || tableName;
        }

        return "管理後台";
      };

      onMounted(async () => {
        try {
          // 從本地存儲獲取用戶資訊
          const userStr =
            localStorage.getItem("user") || sessionStorage.getItem("user");
          if (userStr) {
            currentUser.value = JSON.parse(userStr);
          } else {
            // 如果本地沒有，從服務器獲取
            const response = await fetch("/api/auth/status", {
              credentials: "include",
            });
            const data = await response.json();

            if (data.authenticated) {
              currentUser.value = data.user;
            } else {
              // 未登入，重定向到登入頁面
              router.push("/admin/login");
            }
          }
        } catch (error) {
          console.error("獲取用戶信息失敗:", error);
        }
      });

      const logout = async () => {
        try {
          await apiService.auth.logout();

          // 清除本地存儲的用戶資訊
          localStorage.removeItem("user");
          sessionStorage.removeItem("user");

          // 重定向到登入頁面
          router.push("/admin/login");
        } catch (error) {
          console.error("登出失敗:", error);
        }
      };

      return {
        currentUser,
        logout,
        getCurrentPageName,
      };
    },
  };
</script>

<style scoped>
  .admin-layout {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  .admin-header {
    background-color: #2c3e50;
    color: white;
    padding: 0 20px;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 10;
  }

  .logo h1 {
    margin: 0;
    font-size: 18px;
    font-weight: 500;
  }

  .user-menu {
    display: flex;
    align-items: center;
    gap: 15px;
  }

  .username {
    font-size: 14px;
  }

  .logout-btn {
    background: none;
    border: 1px solid rgba(255, 255, 255, 0.3);
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    transition: background-color 0.2s;
  }

  .logout-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
  }

  .admin-container {
    display: flex;
    flex: 1;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

  .admin-sidebar {
    width: 260px;
    background-color: #f5f7f9;
    border-right: 1px solid #e2e8f0;
    position: sticky;
    top: 60px;
    height: 100%;
    overflow-y: auto;
    flex-shrink: 0;
  }

  .nav-links {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .nav-links > li > a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 20px;
    color: #4a5568;
    text-decoration: none;
    transition: background-color 0.2s;
    font-weight: 500;
  }

  .nav-links > li > a:hover {
    background-color: #e2e8f0;
  }

  .nav-links > li > a.router-link-active {
    background-color: #e2e8f0;
    color: #3182ce;
    font-weight: 500;
  }

  .nav-section {
    margin: 10px 0;
  }

  .section-title {
    padding: 10px 20px;
    font-size: 14px;
    color: #718096;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .sub-menu {
    list-style: none;
    padding: 0;
    margin: 0;
  }

  .sub-menu li a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 20px 10px 40px;
    color: #4a5568;
    text-decoration: none;
    transition: background-color 0.2s;
    font-size: 14px;
  }

  .sub-menu li a:hover {
    background-color: #e2e8f0;
  }

  .sub-menu li a.router-link-active {
    background-color: #e2e8f0;
    color: #3182ce;
    font-weight: 500;
  }

  .admin-content {
    flex: 1;
    padding: 20px;
    background-color: #f8fafc;
    overflow-y: auto;
    height: 100%;
    position: relative;
  }

  .breadcrumb {
    margin-bottom: 20px;
    padding: 10px 0;
    color: #718096;
    font-size: 14px;
  }

  .breadcrumb a {
    color: #3182ce;
    text-decoration: none;
  }

  .breadcrumb a:hover {
    text-decoration: underline;
  }

  .separator {
    margin: 0 8px;
  }

  .current-page {
    font-weight: 500;
    color: #4a5568;
  }

  .material-symbols-outlined {
    font-size: 20px;
  }
</style>
