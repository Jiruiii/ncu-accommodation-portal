<template>
  <div class="container">
    <div v-if="message" :class="['message', messageType]">
      {{ message }}
    </div>

    <!-- 訪客模式按鈕 -->
    <div class="guest-access">
      <button class="guest-button" @click="accessAsGuest">
        <span>訪客瀏覽</span>
        <span class="material-symbols-outlined">travel_explore</span>
      </button>
    </div>

    <div class="forms-container" :class="{ 'sign-up-mode': isSignUp }">
      <div class="left-panel">
        <form
          :class="{ active: !isSignUp }"
          @submit.prevent="handleLogin"
          class="login-form"
        >
          <h2>登入中央大學校外外宿網</h2>
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
            <a href="#" @click.prevent="showForgotPassword = true"
              >忘記密碼？</a
            >
          </div>
          <button type="submit">登入</button>
          <div class="sso-login">
            <p>或使用以下方式登入</p>
            <button type="button" @click="handleSSOLogin" class="sso-button">
              <span>中央大學 Portal 登入</span>
              <span class="material-symbols-outlined">school</span>
            </button>
          </div>
        </form>
        <form
          :class="{ active: isSignUp }"
          @submit.prevent="handleRegister"
          class="register-form"
        >
          <h2>註冊帳號</h2>
          <!-- <div class="role-selection">
            <label>
              <input type="radio" v-model="userRole" value="student" checked />
              學生
            </label>
            <label>
              <input type="radio" v-model="userRole" value="landlord" />
              房東
            </label>
          </div> -->
          <input type="text" v-model="fullName" placeholder="姓名" required />
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
    <div v-if="showForgotPassword" class="modal-overlay">
      <div class="modal-content">
        <h3>重設密碼</h3>
        <p>請輸入您的電子郵件，我們將發送重設密碼連結給您</p>
        <input type="email" v-model="forgotEmail" placeholder="電子郵件" />
        <div class="modal-buttons">
          <button @click="handleForgotPassword">送出</button>
          <button @click="showForgotPassword = false" class="cancel-btn">
            取消
          </button>
        </div>
      </div>
    </div>

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

  export default {
    setup() {
      const route = useRoute();
      const router = useRouter();

      if (route.query.error) {
        const message = ref(decodeURIComponent(route.query.error));
        const messageType = ref("error");

        // 清除 URL 參數
        router.replace({ path: route.path });

        return {
          // ...其他返回值
          message,
          messageType,
        };
      }

      const handleSSOLogin = () => {
        // 使用 API 服務獲取 Portal 登入 URL
        window.location.href = apiService.auth.portal.getLoginUrl();
      };

      return {
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
        message: ref(""),
        messageType: ref("error"),
        showForgotPassword: ref(false),
        forgotEmail: ref(""),
        showTerms: ref(false),
        showPrivacy: ref(false),
        handleSSOLogin,
      };
    },
    methods: {
      async accessAsGuest() {
        clearAuthData();
        localStorage.setItem("guestMode", "true");
        this.$router.push("/accommodation-list");
      },

      async handleLogin() {
        try {
          // 清除之前的錯誤訊息
          this.message = "";

          const response = await fetch("http://localhost:5000/api/auth/login", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              email: this.email,
              password: this.password,
            }),
          });

          const data = await response.json();

          if (response.ok) {
            // 清除舊的認證資料
            clearAuthData();

            // 儲存用戶資訊
            localStorage.setItem("user", JSON.stringify(data.user));

            this.message = "登入成功";
            this.messageType = "success";

            // 延遲導航，讓用戶看到成功訊息
            setTimeout(() => {
              this.$router.push("/accommodation-list");
            }, 1000);
          } else {
            this.message = data.message || "登入失敗";
            this.messageType = "error";
          }
        } catch (error) {
          console.error("登入錯誤:", error);
          this.message = "登入時發生錯誤，請稍後再試";
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
          const response = await fetch(
            "http://localhost:5000/api/auth/register",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                username: this.fullName,
                email: this.registerEmail,
                password: this.registerPassword,
                phone: this.phone,
                user_role: this.userRole,
              }),
            }
          );

          const data = await response.json();

          if (response.ok) {
            this.message = "註冊成功，請登入";
            this.messageType = "success";
            this.isSignUp = false;

            // 清空註冊表單
            this.fullName = "";
            this.registerEmail = "";
            this.phone = "";
            this.registerPassword = "";
            this.confirmPassword = "";
            this.userRole = "student";
            this.agreeTerms = false;

            // 預填登入表單
            this.email = this.registerEmail;
          } else {
            this.message = data.message || "註冊失敗";
            this.messageType = "error";
          }
        } catch (error) {
          console.error("註冊錯誤:", error);
          this.message = "註冊時發生錯誤，請稍後再試";
          this.messageType = "error";
        }
      },

      async handleForgotPassword() {
        if (!this.forgotEmail) {
          this.message = "請輸入電子郵件";
          this.messageType = "error";
          return;
        }

        try {
          const response = await fetch(
            "http://localhost:5000/api/auth/forgot-password",
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify({
                email: this.forgotEmail,
              }),
            }
          );

          const data = await response.json();

          if (response.ok) {
            this.message = "密碼重設連結已發送至您的信箱";
            this.messageType = "success";
            this.showForgotPassword = false;
            this.forgotEmail = "";
          } else {
            this.message = data.message || "無法處理密碼重設請求";
            this.messageType = "error";
          }
        } catch (error) {
          console.error("密碼重設錯誤:", error);
          this.message = "發送重設連結時發生錯誤";
          this.messageType = "error";
        }
      },
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

  .guest-access {
    position: absolute;
    top: 20px;
    right: 20px;
    z-index: 100;
  }

  .guest-button {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 16px;
    background: #f8f9fa;
    border: 2px solid #4a90e2;
    color: #4a90e2;
    border-radius: 25px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  }

  .guest-button:hover {
    background: #4a90e2;
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .guest-button i {
    transition: transform 0.3s ease;
  }

  .guest-button:hover i {
    transform: translateX(5px);
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
    height: 500px;
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
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 25px;
    outline: none;
    font-size: 14px;
    background-color: #f0f0f0;
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

  .sso-login {
    margin-top: 20px;
    text-align: center;
    width: 100%;
    max-width: 300px;
  }

  .sso-login p {
    margin-bottom: 10px;
    font-size: 14px;
  }

  .sso-button {
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
</style>
