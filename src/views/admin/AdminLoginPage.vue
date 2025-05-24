<template>
  <div class="admin-login-page">
    <div class="login-container">
      <div class="login-logo">
        <h1>中央大學宿舍系統</h1>
        <h2>後台管理平台</h2>
      </div>

      <div class="login-form-container">
        <form @submit.prevent="handleLogin" class="login-form">
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>

          <div class="form-group">
            <label for="email">電子郵件</label>
            <div class="input-with-icon">
              <span class="material-symbols-outlined">mail</span>
              <input
                type="email"
                id="email"
                v-model="email"
                placeholder="請輸入管理員郵箱"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label for="password">密碼</label>
            <div class="input-with-icon">
              <span class="material-symbols-outlined">lock</span>
              <input
                :type="showPassword ? 'text' : 'password'"
                id="password"
                v-model="password"
                placeholder="請輸入密碼"
                required
              />
              <button
                type="button"
                class="toggle-password"
                @click="showPassword = !showPassword"
              >
                <span class="material-symbols-outlined">
                  {{ showPassword ? "visibility_off" : "visibility" }}
                </span>
              </button>
            </div>
          </div>

          <div class="form-options">
            <label class="remember-me">
              <input type="checkbox" v-model="rememberMe" />
              <span>記住我</span>
            </label>
          </div>

          <button type="submit" class="login-button" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span>{{ isLoading ? "登入中..." : "管理員登入" }}</span>
          </button>
        </form>
      </div>

      <div class="login-footer">
        <p>© {{ currentYear }} 中央大學資訊系統</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

export default {
  name: "AdminLogin",

  setup() {
    const router = useRouter();
    const store = useStore();
    
    const email = ref("");
    const password = ref("");
    const rememberMe = ref(false);
    const showPassword = ref(false);
    const errorMessage = ref("");

    const currentYear = computed(() => new Date().getFullYear());
    
    // 從 store 中獲取加載狀態
    const isLoading = computed(() => store.getters["user/isLoading"]);

    const handleLogin = async () => {
      try {
        errorMessage.value = "";

        // 使用 Vuex store 進行登入
        const success = await store.dispatch("user/login", {
          email: email.value,
          password: password.value,
          rememberMe: rememberMe.value
        });

        if (success) {
          const user = store.getters["user/currentUser"];
          
          // 檢查是否為管理員或超級管理員角色
          if (!["admin", "superuser"].includes(user.user_role)) {
            errorMessage.value = "只有管理員才能進入後台";
            
            // 登出非管理員用戶
            await store.dispatch("user/logout");
            return;
          }

          // 導向管理儀表板
          router.push("/admin");
        } else {
          // 從 store 獲取錯誤信息
          errorMessage.value = store.getters["user/authError"] || "登入失敗，請檢查您的憑證";
        }
      } catch (error) {
        errorMessage.value = error.message || "登入失敗，請稍後再試";
        console.error("登入錯誤:", error);
      }
    };

    return {
      email,
      password,
      rememberMe,
      showPassword,
      isLoading,
      errorMessage,
      currentYear,
      handleLogin,
    };
  },
};
</script>

<style scoped>
.admin-login-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: #f5f7f9;
}

.login-container {
  width: 100%;
  max-width: 420px;
  background-color: #ffffff;
  border-radius: 10px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.login-logo {
  padding: 40px 20px;
  text-align: center;
  background-color: #2c3e50;
  color: white;
}

.login-logo h1 {
  margin: 0;
  font-size: 22px;
  font-weight: 500;
}

.login-logo h2 {
  margin: 8px 0 0;
  font-size: 16px;
  font-weight: 400;
  opacity: 0.8;
}

.login-form-container {
  padding: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: #4a5568;
}

.input-with-icon {
  position: relative;
}

.input-with-icon .material-symbols-outlined {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #a0aec0;
}

.input-with-icon input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #e2e8f0;
  border-radius: 5px;
  font-size: 15px;
  transition: border-color 0.15s ease-in-out;
}

.input-with-icon input:focus {
  border-color: #3182ce;
  outline: none;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.toggle-password {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #a0aec0;
  cursor: pointer;
  padding: 5px;
}

.form-options {
  display: flex;
  justify-content: space-between;
  margin-bottom: 24px;
}

.remember-me {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.remember-me input {
  margin-right: 8px;
}

.remember-me span {
  font-size: 14px;
  color: #4a5568;
}

.login-button {
  width: 100%;
  padding: 12px;
  background-color: #3182ce;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.15s ease-in-out;
}

.login-button:hover:not(:disabled) {
  background-color: #2b6cb0;
}

.login-button:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
  margin-right: 10px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.login-footer {
  padding: 15px;
  text-align: center;
  border-top: 1px solid #f1f5f9;
}

.login-footer p {
  margin: 0;
  font-size: 12px;
  color: #718096;
}

.error-message {
  background-color: #fff5f5;
  color: #e53e3e;
  padding: 10px;
  border-radius: 5px;
  margin-bottom: 20px;
  font-size: 14px;
  border-left: 3px solid #e53e3e;
}
</style>
