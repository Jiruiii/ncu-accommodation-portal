<template>
  <div class="app-container">
    <PageTransition />

    <CircleNavigation v-if="isLoggedIn" class="desktop-nav" />
    <MobileNavBar v-if="isLoggedIn" class="mobile-nav" />

    <MessageToast
      :message="messageState.message"
      :type="messageState.type"
      :visible="messageState.visible"
      :duration="messageState.duration"
      :show-close-button="messageState.showCloseButton"
      @close="closeMessage"
    />
  </div>
</template>

<script>
import { computed, onMounted, watch, onUnmounted } from "vue";
import { useStore } from "vuex";
import { useRoute } from "vue-router";
import CircleNavigation from "@/components/CircleNavigation.vue";
import PageTransition from "@/components/PageTransition.vue";
import MobileNavBar from "@/components/MobileNavBar.vue";
import MessageToast from "@/components/common/MessageToast.vue";
import MessageService from "@/services/MessageService";

export default {
  name: "App",
  components: {
    CircleNavigation,
    PageTransition,
    MobileNavBar,
    MessageToast,
  },
  setup() {
    const store = useStore();
    const route = useRoute();

    // 使用 store 中的 isLoggedIn getter
    const isLoggedIn = computed(() => store.getters["user/isLoggedIn"]);
    const messageState = MessageService.getState();

    const closeMessage = () => {
      MessageService.close();
    };

    // 初始化數據
    onMounted(async () => {
      // 初始化應用
      store.dispatch("initializeApp");
      
      // 驗證用戶認證狀態
      if (isLoggedIn.value) {
        await store.dispatch("user/verifyAuth");
      }
    });

    // 監聽路由變化
    watch(
      () => route.path,
      () => {
        // 當路由變化時，若有必要可以再次驗證用戶
        if (route.meta.requiresAuth && isLoggedIn.value) {
          store.dispatch("user/verifyAuth");
        }
      }
    );

    // 定期驗證登入狀態，確保安全性
    const intervalId = setInterval(() => {
      if (isLoggedIn.value) {
        store.dispatch("user/verifyAuth");
      }
    }, 300000); // 每5分鐘驗證一次

    // 組件卸載時清除定時器
    onUnmounted(() => {
      clearInterval(intervalId);
    });

    return {
      isLoggedIn,
      messageState,
      closeMessage,
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

/* Add these styles for MobileNavBar*/
.desktop-nav {
  display: none;
}

@media screen and (min-width: 768px) {
  .desktop-nav {
    display: block;
  }

  .mobile-nav {
    display: none;
  }
}

/* Add padding to prevent content from being hidden behind the mobile nav bar */
@media screen and (max-width: 767px) {
  .app-container {
    padding-bottom: 60px;
  }
}
</style>