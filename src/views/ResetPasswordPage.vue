<template>
    <div class="reset-password-page">
      <div class="reset-form-container">
        <div class="form-logo">
          <img src="@/assets/logo.png" alt="Logo" />
        </div>
        
        <h1>重設您的密碼</h1>
        
        <div v-if="!token" class="error-container">
          <div class="error-message">
            <span class="material-symbols-outlined">error</span>
            <span>無效的重設連結，請重新請求密碼重設</span>
          </div>
          <button class="back-btn" @click="goToForgotPassword">回到忘記密碼</button>
        </div>
        
        <div v-else-if="resetComplete" class="success-container">
          <div class="success-message">
            <span class="material-symbols-outlined">check_circle</span>
            <span>密碼已成功重設！</span>
          </div>
          <p>您現在可以使用新密碼登入您的帳戶。</p>
          <button class="login-btn" @click="goToLogin">前往登入</button>
        </div>
        
        <form v-else @submit.prevent="resetPassword">
          <div class="form-group">
            <label for="password">新密碼</label>
            <div class="password-input-container">
              <input
                id="password"
                :type="showPassword ? 'text' : 'password'"
                v-model="password"
                placeholder="請輸入新密碼"
                class="form-input"
              />
              <button
                type="button"
                class="toggle-password-btn"
                @click="showPassword = !showPassword"
              >
                <span class="material-symbols-outlined">
                  {{ showPassword ? "visibility_off" : "visibility" }}
                </span>
              </button>
            </div>
            <div v-if="passwordError" class="input-error">
              {{ passwordError }}
            </div>
          </div>
          
          <div class="form-group">
            <label for="confirmPassword">確認密碼</label>
            <div class="password-input-container">
              <input
                id="confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                v-model="confirmPassword"
                placeholder="請再次輸入新密碼"
                class="form-input"
              />
              <button
                type="button"
                class="toggle-password-btn"
                @click="showConfirmPassword = !showConfirmPassword"
              >
                <span class="material-symbols-outlined">
                  {{ showConfirmPassword ? "visibility_off" : "visibility" }}
                </span>
              </button>
            </div>
            <div v-if="confirmPasswordError" class="input-error">
              {{ confirmPasswordError }}
            </div>
          </div>
          
          <div class="password-strength" v-if="password">
            <div class="strength-label">密碼強度:</div>
            <div class="strength-meter">
              <div
                class="strength-value"
                :style="{ width: passwordStrength.percent + '%' }"
                :class="passwordStrength.class"
              ></div>
            </div>
            <div class="strength-text" :class="passwordStrength.class">
              {{ passwordStrength.text }}
            </div>
          </div>
          
          <div v-if="errorMessage" class="error-message">
            <span class="material-symbols-outlined">error</span>
            <span>{{ errorMessage }}</span>
          </div>
          
          <button 
            type="submit" 
            class="submit-btn" 
            :disabled="isSubmitting || !isFormValid"
          >
            <span v-if="isSubmitting" class="loading-spinner"></span>
            {{ isSubmitting ? '重設中...' : '重設密碼' }}
          </button>
        </form>
        
        <div class="form-footer">
          <p>
            記得密碼了？
            <router-link to="/login">回到登入</router-link>
          </p>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted, watch } from "vue";
  import { useRoute, useRouter } from "vue-router";
  import apiService from "@/services/api";
  
  export default {
    name: "ResetPasswordPage",
    setup() {
      const route = useRoute();
      const router = useRouter();
      
      const token = ref("");
      const password = ref("");
      const confirmPassword = ref("");
      const showPassword = ref(false);
      const showConfirmPassword = ref(false);
      const passwordError = ref("");
      const confirmPasswordError = ref("");
      const errorMessage = ref("");
      const isSubmitting = ref(false);
      const resetComplete = ref(false);
      
      const passwordRules = ref({
        length: false,
        hasLowercase: false,
        hasUppercase: false,
        hasNumber: false,
        hasSpecial: false,
      });
      
      // 從 URL 獲取令牌
      onMounted(() => {
        token.value = route.query.token || "";
      });
      
      // 計算密碼強度
      const passwordStrength = computed(() => {
        if (!password.value) {
          return { percent: 0, class: "", text: "" };
        }
        
        let strength = 0;
        let maxStrength = 5;
        
        if (passwordRules.value.length) strength++;
        if (passwordRules.value.hasLowercase) strength++;
        if (passwordRules.value.hasUppercase) strength++;
        if (passwordRules.value.hasNumber) strength++;
        if (passwordRules.value.hasSpecial) strength++;
        
        const percent = (strength / maxStrength) * 100;
        
        let strengthClass = "";
        let strengthText = "";
        
        if (percent <= 20) {
          strengthClass = "very-weak";
          strengthText = "非常弱";
        } else if (percent <= 40) {
          strengthClass = "weak";
          strengthText = "弱";
        } else if (percent <= 60) {
          strengthClass = "medium";
          strengthText = "一般";
        } else if (percent <= 80) {
          strengthClass = "strong";
          strengthText = "強";
        } else {
          strengthClass = "very-strong";
          strengthText = "非常強";
        }
        
        return { percent, class: strengthClass, text: strengthText };
      });
      
      // 驗證表單
      const isFormValid = computed(() => {
        return (
          password.value && 
          confirmPassword.value && 
          !passwordError.value && 
          !confirmPasswordError.value
        );
      });
      
      // 檢查密碼強度
      const validatePassword = () => {
        passwordError.value = "";
        
        passwordRules.value.length = password.value.length >= 8;
        passwordRules.value.hasLowercase = /[a-z]/.test(password.value);
        passwordRules.value.hasUppercase = /[A-Z]/.test(password.value);
        passwordRules.value.hasNumber = /[0-9]/.test(password.value);
        passwordRules.value.hasSpecial = /[^A-Za-z0-9]/.test(password.value);
        
        if (password.value && password.value.length < 8) {
          passwordError.value = "密碼長度至少需要 8 個字元";
        }
        
        if (confirmPassword.value) {
          validateConfirmPassword();
        }
      };
      
      // 驗證確認密碼
      const validateConfirmPassword = () => {
        confirmPasswordError.value = "";
        
        if (password.value && confirmPassword.value && password.value !== confirmPassword.value) {
          confirmPasswordError.value = "兩次輸入的密碼不一致";
        }
      };
      
      // 重設密碼
      const resetPassword = async () => {
        validatePassword();
        validateConfirmPassword();
        
        if (!isFormValid.value) return;
        
        isSubmitting.value = true;
        errorMessage.value = "";
        
        try {
          const response = await apiService.auth.resetPassword(token.value, password.value);
          
          if (response && response.success) {
            resetComplete.value = true;
          } else {
            errorMessage.value = response?.message || "重設密碼失敗，請稍後再試";
          }
        } catch (error) {
          console.error("重設密碼錯誤:", error);
          errorMessage.value = error.message || "重設密碼失敗，請稍後再試";
        } finally {
          isSubmitting.value = false;
        }
      };
      
      // 導航到登入頁面
      const goToLogin = () => {
        router.push("/login");
      };
      
      // 導航到忘記密碼頁面
      const goToForgotPassword = () => {
        router.push("/forgot-password");
      };
      
      // 監聽密碼變化
      watch(password, validatePassword);
      
      return {
        token,
        password,
        confirmPassword,
        showPassword,
        showConfirmPassword,
        passwordError,
        confirmPasswordError,
        errorMessage,
        isSubmitting,
        resetComplete,
        passwordRules,
        passwordStrength,
        isFormValid,
        resetPassword,
        goToLogin,
        goToForgotPassword,
      };
    }
  };
  </script>
  
  <style scoped>
  .reset-password-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: #f5f7fa;
    padding: 20px;
  }
  
  .reset-form-container {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
    padding: 40px;
    width: 100%;
    max-width: 500px;
  }
  
  .form-logo {
    text-align: center;
    margin-bottom: 20px;
  }
  
  .form-logo img {
    height: 60px;
  }
  
  h1 {
    text-align: center;
    font-size: 1.8rem;
    font-weight: 600;
    margin-bottom: 30px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    font-weight: 500;
    margin-bottom: 8px;
    color: #4a4a4a;
  }
  
  .password-input-container {
    position: relative;
  }
  
  .form-input {
    width: 100%;
    padding: 12px 40px 12px 15px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
    transition: border 0.3s ease;
  }
  
  .form-input:focus {
    border-color: #4a90e2;
    outline: none;
  }
  
  .toggle-password-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    cursor: pointer;
    color: #777;
  }
  
  .input-error {
    color: #e53935;
    font-size: 0.85rem;
    margin-top: 5px;
  }
  
  .password-strength {
    margin-bottom: 20px;
  }
  
  .strength-label {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 5px;
  }
  
  .strength-meter {
    height: 6px;
    background-color: #eee;
    border-radius: 3px;
    overflow: hidden;
  }
  
  .strength-value {
    height: 100%;
    border-radius: 3px;
    transition: width 0.3s ease;
  }
  
  .strength-text {
    font-size: 0.8rem;
    margin-top: 3px;
    text-align: right;
  }
  
  .very-weak {
    background-color: #ff4d4f;
    color: #ff4d4f;
  }
  
  .weak {
    background-color: #ff7a45;
    color: #ff7a45;
  }
  
  .medium {
    background-color: #ffa940;
    color: #ffa940;
  }
  
  .strong {
    background-color: #52c41a;
    color: #52c41a;
  }
  
  .very-strong {
    background-color: #389e0d;
    color: #389e0d;
  }
  
  .submit-btn {
    width: 100%;
    padding: 12px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    transition: background-color 0.3s ease;
  }
  
  .submit-btn:hover:not(:disabled) {
    background-color: #3a80d2;
  }
  
  .submit-btn:disabled {
    background-color: #a0c4f1;
    cursor: not-allowed;
  }
  
  .loading-spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    margin-right: 10px;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .error-message {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    background-color: #ffebee;
    border-left: 4px solid #f44336;
    border-radius: 4px;
    margin-bottom: 20px;
    color: #d32f2f;
  }
  
  .success-message {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    background-color: #e6f7e6;
    border-left: 4px solid #4caf50;
    border-radius: 4px;
    margin-bottom: 15px;
    color: #2e7d32;
  }
  
  .form-footer {
    margin-top: 30px;
    text-align: center;
    color: #666;
  }
  
  .form-footer a {
    color: #4a90e2;
    text-decoration: none;
  }
  
  .form-footer a:hover {
    text-decoration: underline;
  }
  
  .back-btn, .login-btn {
    width: 100%;
    padding: 12px;
    background-color: #4a90e2;
    color: white;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    font-size: 16px;
    cursor: pointer;
    margin-top: 15px;
  }
  
  .error-container, .success-container {
    text-align: center;
  }
  
  .success-container p {
    margin: 10px 0 20px;
    color: #666;
  }
  </style>