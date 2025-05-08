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
              資料庫儀表板
            </router-link>
          </li>
          <li>
            <router-link to="/admin/users">
              <span class="material-symbols-outlined">people</span>
              用戶管理
            </router-link>
          </li>
          <!-- 其他菜單項 -->
        </ul>
      </nav>

      <main class="admin-content">
        <router-view></router-view>
      </main>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted } from "vue";
  import { useRouter } from "vue-router";
  import apiService from "@/services/api";

  export default {
    setup() {
      const router = useRouter();
      const currentUser = ref({
        username: "管理員",
        user_role: "",
      });

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
  }

  .admin-sidebar {
    width: 240px;
    background-color: #f5f7f9;
    border-right: 1px solid #e2e8f0;
  }

  .nav-links {
    list-style: none;
    padding: 0;
    margin: 20px 0;
  }

  .nav-links li a {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 20px;
    color: #4a5568;
    text-decoration: none;
    transition: background-color 0.2s;
  }

  .nav-links li a:hover {
    background-color: #e2e8f0;
  }

  .nav-links li a.router-link-active {
    background-color: #e2e8f0;
    color: #3182ce;
    font-weight: 500;
  }

  .admin-content {
    flex: 1;
    padding: 20px;
    background-color: #f8fafc;
  }

  .material-symbols-outlined {
    font-variation-settings: "FILL" 0, "wght" 400, "GRAD" 0, "opsz" 24;
  }
</style>
