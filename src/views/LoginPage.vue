<template>
  <div class="container">
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 新增手機版 Tab 切換區塊 -->
    <div class="mobile-tabs">
      <div class="tab" :class="{ active: !isSignUp }" @click="isSignUp = false">
        登入帳號
      </div>
      <div class="tab" :class="{ active: isSignUp }" @click="isSignUp = true">
        註冊帳號
      </div>
    </div>

    <div class="forms-container" :class="{ 'sign-up-mode': isSignUp }">
      <div class="left-panel">
        <form
          :class="{ active: !isSignUp }"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <div class="separator">
            <span>使用電子郵件登入</span>
          </div>

          <!-- 保留現有的電子郵件表單 -->
          <input type="email" v-model="email" placeholder="電子郵件" required />
          <input
            type="password"
            v-model="password"
            placeholder="密碼"
            required
          />
          <div class="login-options">
            <label>
              <input type="checkbox" v-model="rememberMe" />
              記住我
            </label>
            <a href="#" @click.prevent="showForgotPasswordForm">忘記密碼？</a>
          </div>
          <button type="submit">登入</button>

          <!-- Portal 快速登入 -->
          <div class="portal-login">
            <div class="portal-info">
              <p>已綁定 Portal 的用戶可使用快速登入</p>
              <button
                type="button"
                @click="handlePortalLogin"
                class="portal-button"
              >
                <span class="material-symbols-outlined">school</span>
                <span>Portal 快速登入</span>
              </button>
            </div>
          </div>
        </form>
        <form
          :class="{ active: isSignUp }"
          @submit.prevent="handleRegister"
          class="register-form"
        >
          <h2>註冊帳號</h2>
          <input
            type="text"
            v-model="fullName"
            placeholder="使用者名稱"
            required
          />
          <input
            type="email"
            v-model="registerEmail"
            placeholder="電子信箱"
            required
          />
          <input type="tel" v-model="phone" placeholder="手機號碼" required />
          <input
            type="password"
            v-model="registerPassword"
            placeholder="密碼"
            required
            minlength="8"
          />
          <input
            type="password"
            v-model="confirmPassword"
            placeholder="確認密碼"
            required
          />

          <!-- 綁定 Portal 選項 -->
          <div class="portal-binding-option">
            <button
              type="button"
              @click="bindPortal"
              :class="['bind-portal-btn', { bound: portalBound }]"
            >
              <span v-if="!portalBound">綁定中央大學 Portal</span>
              <span v-else class="bound-text">
                <span class="material-symbols-outlined">check_circle</span>
                已綁定 Portal
              </span>
            </button>
          </div>

          <div class="terms-agreement">
            <input type="checkbox" v-model="agreeTerms" required id="terms" />
            <label for="terms">
              我同意<a href="#" @click.prevent="showTerms = true">服務條款</a>和
              <a href="#" @click.prevent="showPrivacy = true">隱私政策</a>
            </label>
          </div>
          <button type="submit" :disabled="!agreeTerms">註冊</button>
        </form>
      </div>

      <div class="right-panel">
        <div :class="{ active: !isSignUp }" class="info-panel">
          <h2>歡迎來到中央大學校外外宿網</h2>
          <p>還沒有帳號？立即註冊開始尋找理想的住宿！</p>
          <ul class="feature-list">
            <li>✓ 學生專屬的校外租屋資訊平台</li>
            <li>✓ 學生評價與真實體驗分享</li>
            <li>✓ 輕鬆尋找周邊生活機能</li>
          </ul>
          <button @click="isSignUp = true">註冊帳號</button>
        </div>
        <div :class="{ active: isSignUp }" class="info-panel">
          <h2>已經有帳號了？</h2>
          <p>登入以使用完整功能，收藏心儀的租屋處！</p>
          <ul class="feature-list">
            <li>✓ 儲存收藏的租屋選項</li>
            <li>✓ 與房東直接聯繫</li>
            <li>✓ 分享房源與親友討論</li>
          </ul>
          <button @click="isSignUp = false">返回登入</button>
        </div>
      </div>
    </div>

    <!-- 忘記密碼對話框 -->
    <email-input-modal
      v-if="showEmailInput"
      @close="showEmailInput = false"
      @confirm="confirmEmailAndShowForgotPassword"
      :initial-email="forgotEmail"
    />

    <forgot-password-modal
      :show="showForgotPassword"
      :user-email="forgotEmail"
      @close="closeForgotPasswordModal"
    />

    <!-- 服務條款對話框 -->
    <div v-if="showTerms" class="modal-overlay">
      <div class="modal-content terms-content">
        <h3>服務條款</h3>
        <div class="terms-text">
          <p>歡迎使用中央大學校外外宿網，以下是我們的服務條款...</p>
          <!-- 條款內容 -->
        </div>
        <button @click="showTerms = false">關閉</button>
      </div>
    </div>

    <!-- 隱私政策對話框 -->
    <div v-if="showPrivacy" class="modal-overlay">
      <div class="modal-content terms-content">
        <h3>隱私政策</h3>
        <div class="terms-text">
          <p>中央大學校外外宿網重視您的隱私，以下是我們的隱私政策...</p>
          <!-- 隱私政策內容 -->
        </div>
        <button @click="showPrivacy = false">關閉</button>
      </div>
    </div>
  </div>
</template>

<!-- filepath: c:\Users\USER\Desktop\ncu-accommodation-portal\src\views\LoginPage.vue -->
<script>
  import { ref, computed } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { useStore } from "vuex";
  import apiService from "@/services/api";
  import ForgotPasswordModal from "@/components/profile/ForgotPasswordModal.vue";
  import EmailInputModal from "@/components/profile/EmailInputModal.vue";
  import MessageService from "@/services/MessageService";

  export default {
    components: {
      ForgotPasswordModal,
      EmailInputModal,
    },
    setup() {
      const route = useRoute();
      const router = useRouter();
      const store = useStore();

      // 本地表單狀態
      const isSignUp = ref(false);
      const email = ref("");
      const password = ref("");
      const rememberMe = ref(false);
      const fullName = ref("");
      const registerEmail = ref("");
      const phone = ref("");
      const registerPassword = ref("");
      const confirmPassword = ref("");
      const userRole = ref("student");
      const agreeTerms = ref(false);
      const showForgotPassword = ref(false);
      const forgotEmail = ref("");
      const showTerms = ref(false);
      const showPrivacy = ref(false);
      const showEmailInput = ref(false);

      // Portal 狀態
      const portalBound = ref(false);
      const portalInfo = ref({});

      // 消息狀態
      const message = ref("");
      const messageType = ref("error");

      // 從 store 獲取認證狀態
      const authError = computed(() => store.getters["user/authError"]);
      const isLoading = computed(() => store.getters["user/isLoading"]);

      // 檢查是否從 Portal 綁定頁面返回，且是註冊流程
      if (route.query.register === "true") {
        isSignUp.value = true;

        // 嘗試從 localStorage 獲取表單數據和 Portal 信息
        if (localStorage.getItem("portalBound") === "true") {
          portalBound.value = true;
          try {
            portalInfo.value = JSON.parse(
              localStorage.getItem("portalInfo") || "{}"
            );
          } catch (e) {
            console.error("解析 Portal 信息失敗:", e);
          }
        }

        // 嘗試恢復註冊表單數據
        try {
          const formData = JSON.parse(
            localStorage.getItem("registerFormData") || "{}"
          );
          fullName.value = formData.fullName || "";
          registerEmail.value = formData.registerEmail || "";
          phone.value = formData.phone || "";
          registerPassword.value = formData.registerPassword || "";
          confirmPassword.value = formData.confirmPassword || "";
        } catch (e) {
          console.error("解析註冊表單數據失敗:", e);
        }
      }

      // 檢查是否有錯誤訊息
      if (route.query.error) {
        message.value = decodeURIComponent(route.query.error);
        messageType.value = "error";
        router.replace({ path: route.path });
      }

      // Portal 快速登入處理
      const handlePortalLogin = () => {
        window.location.href = apiService.auth.portal.getLoginUrl();
      };

      // 登入處理
      const handleLogin = async () => {
        try {
          message.value = "";
          messageType.value = "";

          const success = await store.dispatch("user/login", {
            email: email.value,
            password: password.value,
            rememberMe: rememberMe.value,
          });

          if (success) {
            message.value = "登入成功";
            messageType.value = "success";

            // 延遲導航，讓用戶看到成功訊息
            setTimeout(() => {
              router.push("/profile");
            }, 1000);
          } else {
            message.value = store.getters["user/authError"] || "登入失敗";
            messageType.value = "error";
          }
        } catch (error) {
          console.error("登入錯誤:", error);
          message.value = error.message || "登入失敗，請稍後再試";
          messageType.value = "error";
        }
      };

      // 註冊處理
      const handleRegister = async () => {
        // 驗證密碼是否匹配
        if (registerPassword.value !== confirmPassword.value) {
          message.value = "密碼不匹配";
          messageType.value = "error";
          return;
        }

        // 檢查密碼長度（至少8位數字）
        if (registerPassword.value.length < 8) {
          message.value = "密碼至少需要8位";
          messageType.value = "error";
          return;
        }

        try {
          const registerData = {
            username: fullName.value,
            email: registerEmail.value,
            password: registerPassword.value,
            phone: phone.value,
            user_role: userRole.value,
          };

          // 如果已綁定 Portal，添加 Portal 相關資訊
          if (portalBound.value && portalInfo.value.student_id) {
            registerData.portal_id = portalInfo.value.student_id;
            if (portalInfo.value.school_email) {
              registerData.school_email = portalInfo.value.school_email;
            }
          }

          const success = await store.dispatch("user/register", registerData);

          if (success) {
            // 清除暫存數據
            localStorage.removeItem("registerFormData");
            localStorage.removeItem("bindingForRegistration");
            localStorage.removeItem("portalBound");
            localStorage.removeItem("portalInfo");

            message.value = "註冊成功，請登入";
            messageType.value = "success";
            isSignUp.value = false;

            // 清空註冊表單
            clearRegistrationForm();
            // 預填登入表單
            email.value = registerEmail.value;
          } else {
            message.value = store.getters["user/authError"] || "註冊失敗";
            messageType.value = "error";
          }
        } catch (error) {
          console.error("註冊錯誤:", error);
          message.value = "註冊時發生錯誤，請稍後再試";
          messageType.value = "error";
        }
      };

      // Portal 綁定
      const bindPortal = () => {
        // 儲存當前註冊表單資訊到 localStorage，以便綁定後能返回並繼續註冊流程
        localStorage.setItem(
          "registerFormData",
          JSON.stringify({
            fullName: fullName.value,
            registerEmail: registerEmail.value,
            phone: phone.value,
            registerPassword: registerPassword.value,
            confirmPassword: confirmPassword.value,
          })
        );

        // 標記為註冊時綁定，用於回調時識別
        localStorage.setItem("bindingForRegistration", "true");

        // 導向 Portal 授權頁面
        window.location.href = apiService.auth.portal.getInfoUrl();
      };

      // 顯示忘記密碼表單
      const showForgotPasswordForm = () => {
        // 如果輸入框已有值，直接顯示忘記密碼模態框
        if (email.value && validateEmail(email.value)) {
          forgotEmail.value = email.value;
          showForgotPassword.value = true;
        } else {
          // 否則先顯示郵箱輸入模態框
          showEmailInput.value = true;
        }
      };

      // 驗證郵箱格式
      const validateEmail = (email) => {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      };

      // 確認郵箱並顯示忘記密碼模態框
      const confirmEmailAndShowForgotPassword = (email) => {
        forgotEmail.value = email;
        showEmailInput.value = false;
        showForgotPassword.value = true;
      };

      // 關閉忘記密碼模態框
      const closeForgotPasswordModal = () => {
        showForgotPassword.value = false;
        forgotEmail.value = "";
      };

      // 清空註冊表單
      const clearRegistrationForm = () => {
        fullName.value = "";
        registerEmail.value = "";
        phone.value = "";
        registerPassword.value = "";
        confirmPassword.value = "";
        portalBound.value = false;
        portalInfo.value = {};
        userRole.value = "student";
        agreeTerms.value = false;
      };

      // 組件卸載時的清理函數
      const beforeUnmount = () => {
        // 如果不是在註冊頁面，或者不是從 Portal 綁定回來的，清理存儲的數據
        if (!isSignUp.value || route.query.register !== "true") {
          localStorage.removeItem("registerFormData");
          localStorage.removeItem("bindingForRegistration");
          localStorage.removeItem("portalBound");
          localStorage.removeItem("portalInfo");
        }
      };

      return {
        isSignUp,
        email,
        password,
        rememberMe,
        fullName,
        registerEmail,
        phone,
        registerPassword,
        confirmPassword,
        userRole,
        agreeTerms,
        portalBound,
        portalInfo,
        message,
        messageType,
        showForgotPassword,
        forgotEmail,
        showTerms,
        showPrivacy,
        showEmailInput,
        isLoading,
        handleLogin,
        handleRegister,
        bindPortal,
        handlePortalLogin,
        showForgotPasswordForm,
        confirmEmailAndShowForgotPassword,
        closeForgotPasswordModal,
        clearRegistrationForm,
        beforeUnmount,
      };
    },
    beforeUnmount() {
      this.beforeUnmount();
    },
  };
</script>

<style scoped>
  .message {
    position: absolute;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 24px;
    border-radius: 4px;
    font-size: 14px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    z-index: 1000;
    animation: fadeIn 0.3s ease;
  }

  .error {
    background-color: #ff6b6b;
    color: white;
  }

  .success {
    background-color: #4caf50;
    color: white;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translate(-50%, -10px);
    }
    to {
      opacity: 1;
      transform: translate(-50%, 0);
    }
  }

  .container {
    height: 100vh;
    position: relative;
    width: 100%;
    min-height: calc(100vh - 60px);
    background: #272727;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .forms-container {
    position: relative;
    width: 900px;
    height: 600px;
    background: #f0f0f0;
    border-radius: 10px;
    box-shadow: 0 14px 28px rgba(0, 0, 0, 0.25);
    display: flex;
    overflow: hidden;
  }

  .left-panel,
  .right-panel {
    position: absolute;
    top: 0;
    height: 100%;
    width: 50%;
    transition: transform 0.6s ease-in-out;
  }

  .left-panel {
    left: 0;
    background: #5b5b5b;
    color: white;
    z-index: 2;
  }

  .right-panel {
    left: 50%;
    background: #66b3ff;
    color: white;
  }

  /* 滑動效果 */
  .forms-container.sign-up-mode .left-panel {
    transform: translateX(100%);
  }

  .forms-container.sign-up-mode .right-panel {
    transform: translateX(-100%);
  }

  /* 表單切換動畫 */
  form,
  .info-panel {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 20px;
    opacity: 0;
    visibility: hidden;
    transition: opacity 0.8s ease, visibility 0.8s ease;
  }

  form.active,
  .info-panel.active {
    opacity: 1;
    visibility: visible;
  }

  /* 按鈕樣式 */
  button {
    width: 130px;
    padding: 12px;
    border: none;
    border-radius: 25px;
    background: #66b3ff;
    color: #fff;
    font-size: 14px;
    cursor: pointer;
    transition: transform 0.3s ease;
  }

  .right-panel button {
    background: transparent;
    border: 2px solid #fff;
  }

  button:hover {
    transform: scale(1.05);
  }

  input {
    width: 100%;
    max-width: 300px;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 25px;
    outline: none;
    font-size: 14px;
    background-color: #f0f0f0;
    margin-bottom: 0px;
  }

  input:focus {
    border: 2px solid #66b3ff;
  }

  h2 {
    margin-bottom: 10px;
    color: inherit;
  }

  p {
    text-align: center;
    margin-bottom: 20px;
  }

  .login-options {
    display: flex;
    justify-content: space-between;
    width: 100%;
    max-width: 300px;
    margin-top: -10px;
    font-size: 14px;
  }

  .login-options a {
    color: #ffffff;
    text-decoration: underline;
  }

  .login-options label {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .login-options input[type="checkbox"] {
    width: auto;
    max-width: unset;
    margin: 0;
    padding: 0;
  }

  .role-selection {
    display: flex;
    gap: 20px;
    margin-bottom: 10px;
  }

  .terms-agreement {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 14px;
    width: 100%;
    max-width: 300px;
  }

  .terms-agreement a {
    color: #ffffff;
    text-decoration: underline;
  }

  .terms-agreement input[type="checkbox"] {
    width: auto;
    max-width: unset;
    margin: 3px 0 0 0; /* 稍微向下移動以對齊文字的第一行 */
    padding: 0;
  }

  .terms-agreement label {
    flex: 1;
    line-height: 1.4;
  }

  .portal-login {
    margin-top: 20px;
    text-align: center;
    width: 100%;
    max-width: 300px;
  }

  .portal-login p {
    margin-bottom: 10px;
    font-size: 14px;
  }

  .portal-button {
    width: 100%;
    background: #ffffff;
    color: #4a90e2;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }

  .feature-list {
    display: flex;
    text-align: left;
    flex-direction: column;
    align-items: center;
    margin: 0 0 20px;
    padding: 0;
    list-style: none;
    width: 80%;
  }

  .feature-list li {
    margin-bottom: 8px;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    padding: 30px;
    border-radius: 10px;
    width: 90%;
    max-width: 500px;
    color: #333;
  }

  .modal-content h3 {
    margin-top: 0;
    color: #4a90e2;
  }

  .modal-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 20px;
  }

  .cancel-btn {
    background: #f0f0f0;
    color: #333;
  }

  .terms-content {
    max-height: 70vh;
    overflow-y: auto;
  }

  .terms-text {
    margin: 20px 0;
    text-align: left;
    max-height: 50vh;
    overflow-y: auto;
  }

  .register-form {
    padding-top: 40px;
    padding-bottom: 40px;
  }

  .portal-binding-option {
    width: 100%;
    max-width: 300px;
    margin: 5px 0;
  }

  .bind-portal-btn {
    width: 100%;
    padding: 10px;
    border: 2px solid #66b3ff;
    border-radius: 25px;
    background: transparent;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .bind-portal-btn.bound {
    background: #4caf50;
    border-color: #4caf50;
  }

  .bound-text {
    display: flex;
    align-items: center;
    gap: 5px;
  }

  .bound-text .material-symbols-outlined {
    color: white;
  }

  /* 手機版 Tab 樣式 */
  .mobile-tabs {
    display: none;
    width: 100%;
    background: #333333;
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 10;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }

  .mobile-tabs .tab {
    flex: 1;
    text-align: center;
    color: #fff;
    padding: 15px 0;
    cursor: pointer;
    position: relative;
    font-size: 16px;
    font-weight: 500;
  }

  .mobile-tabs .tab.active {
    background-color: #5b5b5b;
  }

  .mobile-tabs .tab.active::after {
    content: "";
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 3px;
    background: #fff;
  }

  /* 響應式設計調整 */
  @media screen and (max-width: 767px) {
    /* 強制整個頁面可滾動 */
    html,
    body {
      overflow-y: auto !important;
      height: 100% !important;
      position: relative !important;
      margin: 0;
      padding: 0;
      background: #5b5b5b; /* 手機版保持灰色背景 */
    }

    /* 確保容器允許滾動 */
    .container {
      position: relative !important;
      min-height: 100vh;
      height: auto !important;
      padding: 0;
      background: #5b5b5b; /* 手機版保持灰色背景 */
      flex-direction: column;
      align-items: stretch;
      justify-content: flex-start;
      overflow-y: visible !important;
      overflow-x: hidden;
      display: block !important;
      touch-action: pan-y !important; /* 允許觸控滑動 */
    }

    /* 修改頂部 Tab 背景色，確保與整體一致 */
    .mobile-tabs {
      display: flex !important;
      justify-content: space-around;
      position: sticky;
      top: 0;
      z-index: 10;
      background: #4a4a4a; /* 稍微深一點的灰色來區分標籤和內容 */
    }

    .forms-container {
      position: relative !important; /* 從 static 改為 relative */
      width: 100%;
      height: auto !important;
      min-height: unset !important; /* 移除最小高度限制 */
      max-height: none !important; /* 確保沒有高度限制 */
      border-radius: 0;
      background: #5b5b5b;
      overflow: visible !important;
      box-shadow: none;
      display: block;
    }

    /* 左側面板調整 */
    .left-panel {
      position: relative !important; /* 從 static 改為 relative */
      width: 100%;
      height: auto !important;
      min-height: auto;
      transform: none !important;
      overflow-y: visible !important;
      display: block;
      z-index: 5;
    }

    /* 表單基本樣式調整 */
    form {
      position: relative !important; /* 從 static 改為 relative */
      height: auto !important;
      padding: 20px 20px 100px;
      transform: none !important;
      overflow-y: visible !important;
      display: none; /* 默認隱藏 */
    }

    /* 活動表單樣式調整 */
    form.active {
      position: relative !important;
      justify-content: flex-start;
      padding-top: 30px;
      padding-bottom: 120px;
      display: flex !important; /* 強制顯示活動表單 */
      flex-direction: column;
      align-items: center;
      opacity: 1;
      visibility: visible;
      gap: 10px;
    }

    /* 縮小表單元素間距 */
    .login-form input,
    .register-form input,
    .portal-binding-option,
    .terms-agreement {
      margin-bottom: 10px; /* 從15px減少到10px */
    }

    /* 減小註冊表單的內邊距，讓按鈕更容易看到 */
    .register-form.active {
      padding-bottom: 80px !important;
    }

    /* 調整Portal登入區塊的間距 */
    .portal-login {
      margin-top: 15px; /* 從25px減少到15px */
    }

    /* 確保模態框使用固定定位 */
    .modal-overlay {
      position: fixed !important;
      z-index: 2000;
    }

    /* 移除可能影響滾動的樣式 */
    body.no-scroll {
      overflow: auto !important;
    }

    /* 處理滾動問題修復 */
    .js-focus-visible :focus:not(.focus-visible) {
      outline: none !important;
    }

    /* 添加頁腳間距，確保所有內容可見 */
    .register-form::after {
      content: "";
      display: block;
      height: 100px;
      width: 100%;
    }

    /* 解決iOS滾動問題 */
    * {
      -webkit-overflow-scrolling: touch !important;
    }

    /* 徹底隱藏右側面板及其內容 */
    .right-panel {
      display: none !important;
      visibility: hidden !important;
      opacity: 0 !important;
      width: 0 !important;
      height: 0 !important;
      position: absolute !important;
      left: -9999px !important;
      overflow: hidden !important;
      z-index: -1 !important;
    }

    /* 確保左側面板占滿整個寬度 */
    .left-panel {
      position: relative !important;
      width: 100% !important;
      height: auto !important;
      min-height: auto;
      transform: none !important;
      overflow-y: visible !important;
      display: block;
      z-index: 5;
      left: 0 !important;
    }

    /* 覆蓋任何可能的轉換效果 */
    .forms-container.sign-up-mode .left-panel,
    .forms-container.sign-up-mode .right-panel {
      transform: none !important;
    }

    /* 確保頁面底部不會出現空白或其他顏色 */
    .forms-container::after {
      content: "";
      display: block;
      height: 20px;
      background: #5b5b5b;
    }
  }

  /* 保持桌面版固定高度不可滾動 */
  @media screen and (min-width: 768px) {
    .container {
      background: #272727; /* 再次確認桌面版保持黑色背景 */
      height: 100vh;
      overflow: hidden;
      position: relative;
    }

    .forms-container {
      overflow: hidden;
      position: relative;
    }

    form,
    .info-panel {
      position: absolute;
      height: 100%;
    }

    .mobile-tabs {
      display: none;
    }
  }
</style>
