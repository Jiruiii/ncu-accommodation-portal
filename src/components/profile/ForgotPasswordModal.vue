<template>
    <div v-if="show" class="modal-overlay" @click.self="cancel">
      <div class="modal-content">
        <h3>忘記密碼</h3>
        
        <div v-if="step === 'sendEmail'" class="modal-form">
          <p class="description">請輸入您的電子郵件地址，我們將發送密碼重置連結至您的信箱</p>
          
          <div class="form-group">
            <label for="email">電子郵件</label>
            <input
              id="email"
              type="email"
              v-model="email"
              placeholder="請輸入您註冊的電子郵件"
              class="form-input"
            />
            <div v-if="emailError" class="input-error">
              {{ emailError }}
            </div>
          </div>
          
          <!-- 錯誤訊息 -->
          <div v-if="errorMessage" class="error-message">
            <i class="error-icon">⚠️</i>
            <span>{{ errorMessage }}</span>
          </div>
  
          <div class="modal-buttons">
            <button
              @click="sendResetEmail"
              :disabled="isSending || !email"
              class="action-btn"
            >
              <span v-if="isSending" class="loading-spinner"></span>
              {{ isSending ? '發送中...' : '發送重置連結' }}
            </button>
            <button @click="cancel" class="cancel-btn">取消</button>
          </div>
        </div>
  
        <div v-else-if="step === 'emailSent'" class="modal-form">
          <div class="success-message">
            <i class="success-icon">✓</i>
            <span>重置連結已發送！請檢查您的電子郵件。</span>
          </div>
          
          <div class="email-sent-info">
            <p>我們已將密碼重置連結發送至：</p>
            <div class="sent-email">{{ email }}</div>
            <p>如果您沒有收到郵件，請檢查垃圾郵件資料夾，或在下面重試。</p>
          </div>
  
          <div class="countdown" v-if="countdown > 0">
            {{ countdown }} 秒後可重新發送
          </div>
  
          <div class="modal-buttons">
            <button
              @click="sendResetEmail"
              :disabled="isSending || countdown > 0"
              class="action-btn"
            >
              <span v-if="isSending" class="loading-spinner"></span>
              {{ isSending ? '發送中...' : '重新發送' }}
            </button>
            <button @click="cancel" class="cancel-btn">關閉</button>
          </div>
          
          <div class="return-to-login">
            <a href="#" @click.prevent="goToLogin">返回登入</a>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { apiService } from "@/services/api.js";
  
  export default {
    name: "ForgotPasswordModal",
    props: {
      show: {
        type: Boolean,
        default: false
      }
    },
    data() {
      return {
        step: "sendEmail", // sendEmail, emailSent
        email: "",
        emailError: "",
        errorMessage: "",
        isSending: false,
        countdown: 0,
        timer: null
      };
    },
    methods: {
      async sendResetEmail() {
        // 重置錯誤訊息
        this.emailError = "";
        this.errorMessage = "";
        
        // 驗證電子郵件
        if (!this.email) {
          this.emailError = "請輸入電子郵件";
          return;
        }
  
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {
          this.emailError = "請輸入有效的電子郵件地址";
          return;
        }
  
        this.isSending = true;
  
        try {
          // 調用重置密碼 API
          const response = await apiService.auth.forgotPassword(this.email);
          
          console.log('密碼重置請求回應:', response);
          
          if (response && response.success) {
            // 切換到已發送郵件狀態
            this.step = "emailSent";
            this.startCountdown();
          } else {
            this.errorMessage = response?.message || "發送重置連結失敗，請稍後再試";
          }
        } catch (error) {
          console.error("請求密碼重置錯誤:", error);
          
          if (error.message === "User not found") {
            this.emailError = "找不到使用此郵箱的帳戶";
          } else if (error.message === "Too many requests") {
            this.errorMessage = "請求過於頻繁，請稍後再試";
          } else {
            this.errorMessage = error.message || "發送重置連結失敗，請稍後再試";
          }
        } finally {
          this.isSending = false;
        }
      },
      startCountdown() {
        this.countdown = 60;
        clearInterval(this.timer);
        this.timer = setInterval(() => {
          this.countdown--;
          if (this.countdown <= 0) {
            clearInterval(this.timer);
          }
        }, 1000);
      },
      goToLogin() {
        this.$emit("go-to-login");
        this.$emit("close");
      },
      cancel() {
        this.reset();
        this.$emit("close");
      },
      reset() {
        this.step = "sendEmail";
        this.email = "";
        this.emailError = "";
        this.errorMessage = "";
        clearInterval(this.timer);
        this.countdown = 0;
      }
    },
    beforeUnmount() {
      clearInterval(this.timer);
    }
  };
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background-color: white;
    padding: 30px;
    border-radius: 12px;
    max-width: 500px;
    width: 100%;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }
  
  h3 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #333;
    font-size: 1.5rem;
  }
  
  .description {
    color: #666;
    margin-bottom: 20px;
  }
  
  .modal-form {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  label {
    font-weight: 500;
    color: #555;
  }
  
  .form-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
  }
  
  .input-error {
    color: #dc3545;
    font-size: 0.85rem;
    margin-top: 5px;
  }
  
  .error-message, .success-message {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    border-radius: 4px;
    margin: 10px 0;
  }
  
  .error-message {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
  }
  
  .success-message {
    background-color: #e6f7e6;
    border-left: 4px solid #4caf50;
  }
  
  .error-icon, .success-icon {
    font-size: 1.2rem;
  }
  
  .modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
  
  button {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .action-btn {
    background-color: #4a90e2;
    color: white;
  }
  
  .action-btn:hover:not(:disabled) {
    background-color: #3a80d2;
  }
  
  .cancel-btn {
    background-color: transparent;
    color: #666;
    border: 1px solid #ddd;
  }
  
  .cancel-btn:hover {
    background-color: #f5f5f5;
  }
  
  .loading-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: currentColor;
    margin-right: 8px;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .email-sent-info {
    background-color: #f9f9f9;
    padding: 15px;
    border-radius: 8px;
    margin: 15px 0;
  }
  
  .sent-email {
    font-weight: 600;
    color: #4a90e2;
    padding: 10px 0;
    text-align: center;
  }
  
  .countdown {
    color: #666;
    font-size: 14px;
    text-align: center;
    margin: 10px 0;
  }
  
  .return-to-login {
    text-align: center;
    margin-top: 15px;
  }
  
  .return-to-login a {
    color: #4a90e2;
    text-decoration: none;
  }
  
  .return-to-login a:hover {
    text-decoration: underline;
  }
  </style>