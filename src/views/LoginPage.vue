 <template>
  <div class="container">
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

        <!-- 新增手機版 Tab 切換區塊 -->
    <div class="mobile-tabs">
      <div 
        class="tab" 
        :class="{ active: !isSignUp }"
        @click="isSignUp = false"
      >
        登入帳號
      </div>
      <div 
        class="tab" 
        :class="{ active: isSignUp }"
        @click="isSignUp = true"
      >
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
            <a href="#" @click.prevent="showForgotPasswordForm"
              >忘記密碼？</a
            >
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

<script>
  import { ref } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import { clearAuthData } from "@/utils/auth";
  import apiService from "@/services/api";
  import ForgotPasswordModal from "@/components/profile/ForgotPasswordModal.vue";
  import EmailInputModal from "@/components/profile/EmailInputModal.vue";

  export default {
    components: {
      ForgotPasswordModal,
      EmailInputModal,
    },
    setup() {
      const route = useRoute();
      const router = useRouter();

      // Portal 狀態
      const portalBound = ref(false);
      const portalInfo = ref({});

      // 檢查是否從 Portal 綁定頁面返回，且是註冊流程
      if (route.query.register === "true") {
        const isSignUp = ref(true);

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
        let formData = {};
        try {
          formData = JSON.parse(
            localStorage.getItem("registerFormData") || "{}"
          );
        } catch (e) {
          console.error("解析註冊表單數據失敗:", e);
        }

        return {
          isSignUp,
          portalBound,
          portalInfo,
          fullName: ref(formData.fullName || ""),
          registerEmail: ref(formData.registerEmail || ""),
          phone: ref(formData.phone || ""),
          registerPassword: ref(formData.registerPassword || ""),
          confirmPassword: ref(formData.confirmPassword || ""),
          userRole: ref("student"),
          agreeTerms: ref(false),
          message: ref(""),
          messageType: ref(""),
          showForgotPassword: ref(false),
          showEmailInput: ref(false),
          forgotEmail: ref(""),
          showTerms: ref(false),
          showPrivacy: ref(false),
          handlePortalLogin: () => {
            window.location.href = apiService.auth.portal.getLoginUrl();
          },
        };
      }

      // 檢查是否有錯誤訊息
      if (route.query.error) {
        const message = ref(decodeURIComponent(route.query.error));
        const messageType = ref("error");
        router.replace({ path: route.path });

        return {
          message,
          messageType,
          portalBound,
          portalInfo,
          isSignUp: ref(false),
          email: ref(""),
          password: ref(""),
          rememberMe: ref(false),
          fullName: ref(""),
          registerEmail: ref(""),
          phone: ref(""),
          registerPassword: ref(""),
          confirmPassword: ref(""),
          userRole: ref("student"),
          agreeTerms: ref(false),
          showForgotPassword: ref(false),
          showEmailInput: ref(false),
          forgotEmail: ref(""),
          showTerms: ref(false),
          showPrivacy: ref(false),
          handlePortalLogin: () => {
            window.location.href = apiService.auth.portal.getLoginUrl();
          },
        };
      }

      // Portal 快速登入處理
      const handlePortalLogin = () => {
        window.location.href = apiService.auth.portal.getLoginUrl();
      };

      return {
        // 登入相關
        isSignUp: ref(false),
        email: ref(""),
        password: ref(""),
        rememberMe: ref(false),

        // 註冊相關
        fullName: ref(""),
        registerEmail: ref(""),
        phone: ref(""),
        registerPassword: ref(""),
        confirmPassword: ref(""),
        userRole: ref("student"),
        agreeTerms: ref(false),

        // Portal 相關
        portalBound,
        portalInfo,

        // 信息相關
        message: ref(""),
        messageType: ref("error"),

        // 對話框控制
        showForgotPassword: ref(false),
        forgotEmail: ref(""),
        showTerms: ref(false),
        showPrivacy: ref(false),
        showEmailInput: ref(false),

        handlePortalLogin,
      };
    },
    methods: {
      async handleLogin() {
        try {
          // 清除之前的錯誤訊息
          this.message = "";

          const response = await apiService.auth.login({
            email: this.email,
            password: this.password,
          });

          // const data = await response.json();

          if (
            response.success ||
            (response.message && response.message === "登入成功")
          ) {
            // 清除舊的認證資料
            clearAuthData();

            // 儲存用戶資訊
            if (this.rememberMe) {
              // 長期記住用戶（瀏覽器關閉後仍然有效）
              localStorage.setItem("user", JSON.stringify(response.user));
            } else {
              // 僅在當前會話中記住用戶（瀏覽器關閉後失效）
              sessionStorage.setItem("user", JSON.stringify(response.user));
            }

            this.message = "登入成功";
            this.messageType = "success";

            // 延遲導航，讓用戶看到成功訊息
            setTimeout(() => {
              this.$router.push("/profile");
              this.$store.commit("SET_CURRENTROUTE", "profile");
            }, 1000);
          } else {
            this.message = "登入失敗";
            this.messageType = "error";
          }
        } catch (error) {
          console.error("登入錯誤:", error);
          this.message = error.message || "登入失敗，請稍後再試";
          this.messageType = "error";
        }
      },

      async handleRegister() {
        // 驗證密碼是否匹配
        if (this.registerPassword !== this.confirmPassword) {
          this.message = "密碼不匹配";
          this.messageType = "error";
          return;
        }

        // 檢查密碼強度（至少8位，包含字母和數字）
        const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        if (!passwordPattern.test(this.registerPassword)) {
          this.message = "密碼至少需要8位，且包含字母和數字";
          this.messageType = "error";
          return;
        }

        try {
          const registerData = {
            username: this.fullName,
            email: this.registerEmail,
            password: this.registerPassword,
            phone: this.phone,
            user_role: this.userRole,
          };

          // 如果已綁定 Portal，添加 Portal 相關資訊
          if (this.portalBound && this.portalInfo.student_id) {
            registerData.portal_id = this.portalInfo.student_id;
            if (this.portalInfo.school_email) {
              registerData.school_email = this.portalInfo.school_email;
            }
          }

          const response = await apiService.auth.register(registerData);

          if (
            response.success ||
            (response.message && response.message === "註冊成功")
          ) {
            // 清除暫存數據
            localStorage.removeItem("registerFormData");
            localStorage.removeItem("bindingForRegistration");
            localStorage.removeItem("portalBound");
            localStorage.removeItem("portalInfo");

            this.message = "註冊成功，請登入";
            this.messageType = "success";
            this.isSignUp = false;

            // 清空註冊表單
            this.clearRegistrationForm();
            // 預填登入表單
            this.email = this.registerEmail;
          } else {
            this.message = response.message || "註冊失敗";
            this.messageType = "error";
          }
        } catch (error) {
          console.error("註冊錯誤:", error);
          this.message = "註冊時發生錯誤，請稍後再試";
          this.messageType = "error";
        }
      },

      bindPortal() {
        // 儲存當前註冊表單資訊到 localStorage，以便綁定後能返回並繼續註冊流程
        localStorage.setItem(
          "registerFormData",
          JSON.stringify({
            fullName: this.fullName,
            registerEmail: this.registerEmail,
            phone: this.phone,
            registerPassword: this.registerPassword,
            confirmPassword: this.confirmPassword,
          })
        );

        // 標記為註冊時綁定，用於回調時識別
        localStorage.setItem("bindingForRegistration", "true");

        // 導向 Portal 授權頁面
        window.location.href = apiService.auth.portal.getInfoUrl();
      },

      showForgotPasswordForm() {
        // 如果輸入框已有值，直接顯示忘記密碼模態框
        if (this.email && this.validateEmail(this.email)) {
          this.forgotEmail = this.email;
          this.showForgotPassword = true;
        } else {
          // 否則先顯示郵箱輸入模態框
          this.showEmailInput = true;
        }
      },

      validateEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
      },

      // 確認郵箱並顯示忘記密碼模態框
      confirmEmailAndShowForgotPassword(email) {
        this.forgotEmail = email;
        this.showEmailInput = false;
        this.showForgotPassword = true;
      },

      // 關閉忘記密碼模態框
      closeForgotPasswordModal() {
        this.showForgotPassword = false;
        this.forgotEmail = "";
      },

      // 清空註冊表單
      clearRegistrationForm() {
        this.fullName = "";
        this.registerEmail = "";
        this.phone = "";
        this.registerPassword = "";
        this.confirmPassword = "";
        this.portalBound = false;
        this.portalInfo = {};
        this.userRole = "student";
        this.agreeTerms = false;
      },
    },

    // 組件卸載時清理，但保留註冊過程中的數據
    beforeUnmount() {
      // 如果不是在註冊頁面，或者不是從 Portal 綁定回來的，清理存儲的數據
      if (!this.isSignUp || this.$route.query.register !== "true") {
        localStorage.removeItem("registerFormData");
        localStorage.removeItem("bindingForRegistration");
        localStorage.removeItem("portalBound");
        localStorage.removeItem("portalInfo");
      }
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
    background: #272727; /* 恢復桌面版為黑色背景 */
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .forms-container {
    position: relative;
    width: 900px;
    height: 600px;
    background: #5b5b5b;
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
    transition: opacity 0.5s ease, visibility 0.5s ease;
  }

  form.active,
  .info-panel.active {
    opacity: 1;
    visibility: visible;
    z-index: 5;
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
    content: '';
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
    html, body {
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

    form, .info-panel {
      position: absolute;
      height: 100%;
    }
    
    .mobile-tabs {
      display: none;
    }
  }
</style>