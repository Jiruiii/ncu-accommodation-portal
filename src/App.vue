<template>
  <div class="app-container">
    <PageTransition />

    <CircleNavigation v-if="isLoggedIn" />
  </div>
</template>

<script>
  import { ref, onMounted, watch, onUnmounted } from "vue";
  import { useStore } from "vuex";
  import { useRoute } from "vue-router";
  import CircleNavigation from "@/components/CircleNavigation.vue";
  import PageTransition from "@/components/PageTransition.vue";

  export default {
    name: "App",
    components: {
      CircleNavigation,
      PageTransition,
    },
    setup() {
      const store = useStore();
      const route = useRoute();
      const isLoggedIn = ref(false);

      // 檢查用戶是否已登入
      const checkLoginStatus = () => {
        // 檢查 localStorage 或 sessionStorage 中是否有用戶資料
        const userFromLocal = localStorage.getItem("user");
        const userFromSession = sessionStorage.getItem("user");

        isLoggedIn.value = !!(userFromLocal || userFromSession);
      };

      // 初始化數據
      onMounted(() => {
        checkLoginStatus();
        store.dispatch("initializeApp");

        // 監聽 localStorage 變化
        window.addEventListener("storage", (e) => {
          if (e.key === "user") {
            checkLoginStatus();
          }
        });
      });

      // 監聽路由變化，可能會在登入/登出後更新
      watch(
        () => route.path,
        () => {
          checkLoginStatus();
        }
      );

      // 設置一個定期檢查，以防其他方式更新了 localStorage
      const intervalId = setInterval(checkLoginStatus, 5000);

      // 組件卸載時清除定時器
      onUnmounted(() => {
        clearInterval(intervalId);
        window.removeEventListener("storage", checkLoginStatus);
      });

      return {
        isLoggedIn,
      };
    },
  };
</script>

<style>
  @import url("https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@300;400;500;700&display=swap");

  :root {
    --primary-color: #007bff;
    --secondary-color: #00c6ff;
    --accent-color: #ff6b6b;
    --text-color: #333;
    --light-gray: #f8f9fa;
    --card-shadow: 0 8px 30px rgba(0, 0, 0, 0.07);
  }

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: "Noto Sans TC", sans-serif;
    color: var(--text-color);
    background-color: #fafafa;
    overflow-x: hidden;
  }

  .app-container {
    width: 100%;
    height: 100vh;
    position: relative;
  }

  /* 通用按鈕樣式 */
  .btn {
    padding: 10px 20px;
    border: none;
    border-radius: 30px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
  }

  .btn-primary {
    background: linear-gradient(
      135deg,
      var(--primary-color),
      var(--secondary-color)
    );
    color: white;
    box-shadow: 0 4px 15px rgba(0, 123, 255, 0.3);
  }

  .btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 123, 255, 0.4);
  }

  /* 卡片樣式 */
  .card {
    background-color: white;
    border-radius: 16px;
    box-shadow: var(--card-shadow);
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  }
</style>
