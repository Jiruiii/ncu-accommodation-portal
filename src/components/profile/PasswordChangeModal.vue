<!-- filepath: c:\Users\USER\Desktop\ncu-accommodation-portal\src\components\profile\PasswordChangeModal.vue -->
<template>
  <div v-if="show" class="modal-overlay" @click.self="cancel">
    <div class="modal-content">
      <h3>修改密碼</h3>

      <div class="modal-form">
        <!-- 現在密碼 -->
        <div class="form-group">
          <label for="current-password">現在密碼</label>
          <div class="password-input-container">
            <input
              id="current-password"
              :type="showCurrentPassword ? 'text' : 'password'"
              v-model="currentPassword"
              placeholder="請輸入現在密碼"
              class="password-input"
            />
            <button
              type="button"
              class="toggle-password-btn"
              @click="showCurrentPassword = !showCurrentPassword"
            >
              <span class="material-symbols-outlined">
                {{ showCurrentPassword ? "visibility_off" : "visibility" }}
              </span>
            </button>
          </div>
          <div v-if="currentPasswordError" class="input-error">
            {{ currentPasswordError }}
          </div>
        </div>

        <!-- 新密碼 -->
        <div class="form-group">
          <label for="new-password">新密碼</label>
          <div class="password-input-container">
            <input
              id="new-password"
              :type="showNewPassword ? 'text' : 'password'"
              v-model="newPassword"
              placeholder="請輸入新密碼"
              class="password-input"
              @input="validateNewPassword"
            />
            <button
              type="button"
              class="toggle-password-btn"
              @click="showNewPassword = !showNewPassword"
            >
              <span class="material-symbols-outlined">
                {{ showNewPassword ? "visibility_off" : "visibility" }}
              </span>
            </button>
          </div>
          <div v-if="newPasswordError" class="input-error">
            {{ newPasswordError }}
          </div>
          <div class="password-strength" v-if="newPassword">
            <div class="strength-label">密碼強度:</div>
            <div class="strength-meter">
              <div
                class="strength-value"
                :style="{ width: passwordStrength.percent + '%' }"
                :class="passwordStrength.class"
              ></div>
            </div>
          </div>
        </div>

        <!-- 確認密碼 -->
        <div class="form-group">
          <label for="confirm-password">確認密碼</label>
          <div class="password-input-container">
            <input
              id="confirm-password"
              type="password"
              v-model="confirmPassword"
              placeholder="請再次輸入新密碼"
              class="password-input"
              @input="validateConfirmPassword"
            />
          </div>
          <div v-if="confirmPasswordError" class="input-error">
            {{ confirmPasswordError }}
          </div>
        </div>

        <!-- 密碼規則提示 -->
        <div class="password-rules">
          <h4>密碼須符合以下條件:</h4>
          <ul>
            <li :class="{ 'rule-met': passwordRules.length }">至少 8 個字元</li>
          </ul>
        </div>

        <!-- 忘記密碼 -->
        <div class="forgot-password">
          <a href="#" @click.prevent="forgotPassword">忘記密碼？</a>
        </div>

        <!-- 錯誤訊息 -->
        <div v-if="errorMessage" class="error-message">
          <span class="material-symbols-outlined error-icon"> warning </span>
          <span>{{ errorMessage }}</span>
        </div>

        <!-- 成功訊息 -->
        <div v-if="successMessage" class="success-message">
          <span class="material-symbols-outlined success-icon"> check_circle </span>
          <span>{{ successMessage }}</span>
        </div>

        <!-- 操作按鈕 -->
        <div class="modal-buttons">
          <button
            @click="changePassword"
            :disabled="isChanging || !isFormValid"
            class="action-btn"
          >
            <span v-if="isChanging" class="loading-spinner"></span>
            {{ isChanging ? "更改中..." : "更改密碼" }}
          </button>
          <button @click="cancel" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { apiService } from "@/services/api.js";

  export default {
    name: "PasswordChangeModal",
    props: {
      show: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
        isChanging: false,
        errorMessage: "",
        successMessage: "",
        currentPasswordError: "",
        newPasswordError: "",
        confirmPasswordError: "",
        showCurrentPassword: false,
        showNewPassword: false,
        passwordRules: {
          length: false,
          hasLowercase: false,
          hasUppercase: false,
          hasNumber: false,
          hasSpecial: false,
        },
      };
    },
    computed: {
      isFormValid() {
        return (
          this.currentPassword &&
          this.newPassword &&
          this.confirmPassword &&
          !this.currentPasswordError &&
          !this.confirmPasswordError &&
          this.newPassword.length >= 8 &&
          this.newPassword.length < 128
        );
      },
      passwordStrength() {
        if (!this.newPassword) {
          return { percent: 0, class: "", text: "" };
        }

        let strength = 0;
        let maxStrength = 5; // 5 條件：長度、小寫、大寫、數字、特殊字符

        if (this.passwordRules.length) strength++;
        if (this.passwordRules.hasLowercase) strength++;
        if (this.passwordRules.hasUppercase) strength++;
        if (this.passwordRules.hasNumber) strength++;
        if (this.passwordRules.hasSpecial) strength++;

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
      },
    },
    watch: {
      newPassword() {
        this.validateNewPassword();
      },
    },
    methods: {
      validateNewPassword() {
        // 重置錯誤訊息
        this.newPasswordError = "";

        // 檢查密碼條件
        this.passwordRules.length = this.newPassword.length >= 8;
        this.passwordRules.hasLowercase = /[a-z]/.test(this.newPassword);
        this.passwordRules.hasUppercase = /[A-Z]/.test(this.newPassword);
        this.passwordRules.hasNumber = /[0-9]/.test(this.newPassword);
        this.passwordRules.hasSpecial = /[^A-Za-z0-9]/.test(this.newPassword);

        // 基本長度驗證
        if (this.newPassword && this.newPassword.length < 8) {
          this.newPasswordError = "密碼長度至少需要 8 個字元";
        }

        // 驗證密碼強度
        // if (this.newPassword && this.passwordStrength.percent < 60) {
        //   this.newPasswordError = "密碼強度不足，請設置更安全的密碼";
        // }

        // 如果確認密碼已填寫，則同時驗證確認密碼
        if (this.confirmPassword) {
          this.validateConfirmPassword();
        }
      },
      validateConfirmPassword() {
        this.confirmPasswordError = "";
        if (
          this.newPassword &&
          this.confirmPassword &&
          this.newPassword !== this.confirmPassword
        ) {
          this.confirmPasswordError = "兩次輸入的密碼不一致";
        }
      },
      async changePassword() {
        // 重置訊息
        this.errorMessage = "";
        this.successMessage = "";

        // 表單驗證
        if (!this.currentPassword) {
          this.currentPasswordError = "請輸入現在密碼";
          return;
        }

        if (!this.newPassword) {
          this.newPasswordError = "請輸入新密碼";
          return;
        }

        if (!this.confirmPassword) {
          this.confirmPasswordError = "請確認新密碼";
          return;
        }

        if (this.newPassword !== this.confirmPassword) {
          this.confirmPasswordError = "兩次輸入的密碼不一致";
          return;
        }

        // 不允許新密碼和舊密碼相同
        if (this.currentPassword === this.newPassword) {
          this.newPasswordError = "新密碼不能與現在密碼相同";
          return;
        }

        this.isChanging = true;

        try {
          const response = await apiService.users.changePassword({
            current_password: this.currentPassword,
            new_password: this.newPassword,
          });

          console.log("修改密碼回應:", response);

          if (response && response.success) {
            this.successMessage = "密碼已成功修改";

            // 延遲關閉彈窗，讓用戶看到成功消息
            setTimeout(() => {
              this.reset();
              this.$emit("success");
              this.$emit("close");
            }, 1500);
          } else {
            this.errorMessage = response?.message || "密碼修改失敗，請稍後再試";
          }
        } catch (error) {
          console.error("修改密碼錯誤:", error);

          // 根據不同的錯誤類型設置不同的錯誤訊息
          if (error.message === "Current password is incorrect") {
            this.currentPasswordError = "現在密碼輸入錯誤";
          } else if (
            error.message === "New password does not meet requirements"
          ) {
            this.newPasswordError = "新密碼不符合安全要求";
          } else {
            this.errorMessage = error.message || "修改密碼失敗，請稍後再試";
          }
        } finally {
          this.isChanging = false;
        }
      },
      forgotPassword() {
        // 關閉當前彈窗，轉而打開忘記密碼彈窗或導航到忘記密碼頁面
        this.$emit("forgot-password");
        this.$emit("close");
      },
      cancel() {
        this.reset();
        this.$emit("close");
      },
      reset() {
        this.currentPassword = "";
        this.newPassword = "";
        this.confirmPassword = "";
        this.errorMessage = "";
        this.successMessage = "";
        this.currentPasswordError = "";
        this.newPasswordError = "";
        this.confirmPasswordError = "";
        this.showCurrentPassword = false;
        this.showNewPassword = false;
      },
    },
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

  .password-input-container {
    position: relative;
    display: flex;
    align-items: center;
  }

  .password-input {
    width: 100%;
    padding: 10px 40px 10px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 16px;
  }

  .toggle-password-btn {
    position: absolute;
    right: 10px;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 14px;
    color: #777;
  }

  .input-error {
    color: #dc3545;
    font-size: 0.85rem;
    margin-top: 5px;
  }

  .error-message,
  .success-message {
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

  .error-icon,
  .success-icon {
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
  }

  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .action-btn {
    background-color: #4a90e2;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
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

  .password-strength {
    margin-top: 8px;
  }

  .strength-label {
    font-size: 0.8rem;
    color: #666;
    margin-bottom: 3px;
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

  .password-rules {
    background-color: #f9f9f9;
    padding: 10px 15px;
    border-radius: 6px;
    margin-top: 5px;
  }

  .password-rules h4 {
    font-size: 0.9rem;
    margin: 0 0 8px 0;
    color: #555;
  }

  .password-rules ul {
    margin: 0;
    padding-left: 20px;
  }

  .password-rules li {
    font-size: 0.85rem;
    color: #666;
    margin-bottom: 3px;
  }

  .rule-met {
    color: #52c41a;
  }

  .forgot-password {
    text-align: right;
    margin-top: 5px;
  }

  .forgot-password a {
    color: #4a90e2;
    text-decoration: none;
    font-size: 0.85rem;
  }

  .forgot-password a:hover {
    text-decoration: underline;
  }
</style>
