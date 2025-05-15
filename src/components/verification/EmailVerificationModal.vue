<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal-content">
      <h3>驗證您的電子郵件</h3>
      <div v-if="!codeSent">
        <p>我們將發送驗證碼到您的電子郵件：{{ email }}</p>
        <div v-if="errorMessage" class="error-message">
          <i class="error-icon">⚠️</i>
          <span>{{ errorMessage }}</span>
        </div>
        <div class="modal-buttons">
          <button @click="sendCode" :disabled="isProcessing" class="action-btn">
            <span v-if="isProcessing" class="loading-spinner"></span>
            {{ isProcessing ? '發送中...' : '發送驗證碼' }}
          </button>
          <button @click="cancel" class="cancel-btn">取消</button>
        </div>
      </div>
      <div v-else>
        <p>驗證碼已發送到您的電子郵件，請查收並在下方輸入：</p>
        <verification-code-input v-model="verificationCode" placeholder="請輸入6位數驗證碼" />
        <div class="countdown" v-if="countdown > 0">{{ countdown }}秒後可重新發送</div>
        <div v-if="successMessage" class="success-message">
          <span class="material-symbols-outlined success-icon"> check_circle </span>
          <span>{{ successMessage }}</span>
        </div>
        <div v-if="errorMessage" class="error-message">
          <span class="material-symbols-outlined error-icon"> warning </span>
          <span>{{ errorMessage }}</span>
        </div>
        <div class="modal-buttons">
          <button v-if="countdown === 0" @click="sendCode" :disabled="isProcessing" class="secondary-btn">
            <span v-if="isProcessing" class="loading-spinner"></span>
            重新發送
          </button>
          <button @click="verify" :disabled="!verificationCode || isVerifying" class="action-btn">
            <span v-if="isVerifying" class="loading-spinner"></span>
            {{ isVerifying ? '驗證中...' : '驗證' }}
          </button>
          <button @click="cancel" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import VerificationCodeInput from '@/components/common/VerificationCodeInput.vue';
import { apiService } from "@/services/api.js";

export default {
  name: 'EmailVerificationModal',
  components: {
    VerificationCodeInput
  },
  props: {
    show: {
      type: Boolean,
      default: false
    },
    email: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      codeSent: false,
      verificationCode: '',
      isProcessing: false,
      isVerifying: false,
      countdown: 0,
      timer: null,
      errorMessage: '',
      successMessage: ''
    };
  },
  methods: {
    async sendCode() {
      this.isProcessing = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const response = await apiService.verification.sendEmailVerification(this.email);
        
        if (response && response.success) {
          this.successMessage = '驗證碼已發送，請查收您的郵箱';
          this.codeSent = true;
          this.startCountdown();
        } else {
          this.errorMessage = response?.message || '發送驗證碼失敗，請稍後再試';
        }
      } catch (error) {
        console.error('發送驗證碼錯誤:', error);
        this.errorMessage = error.message || '發送過程中出現錯誤，請稍後再試';
      } finally {
        this.isProcessing = false;
      }
    },
    
    async verify() {
      if (!this.verificationCode) return;
      
      this.isVerifying = true;
      this.errorMessage = '';
      this.successMessage = '';
      
      try {
        const response = await apiService.verification.verifyEmail(this.verificationCode);
        
        if (response && response.success) {
          this.successMessage = '驗證成功！';
          
          // 更新用戶資訊（通過父組件的事件）
          this.$emit('verification-success');
          
          // 延遲關閉彈窗，讓用戶看到成功消息
          setTimeout(() => {
            this.reset();
            this.$emit('close');
          }, 1500);
        } else {
          this.errorMessage = response?.message || '驗證失敗，請確認驗證碼是否正確';
        }
      } catch (error) {
        console.error('驗證碼驗證錯誤:', error);
        this.errorMessage = error.message || '驗證過程中出現錯誤，請稍後再試';
      } finally {
        this.isVerifying = false;
      }
    },
    
    cancel() {
      this.reset();
      this.$emit('close');
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
    
    reset() {
      this.codeSent = false;
      this.verificationCode = '';
      this.errorMessage = '';
      this.successMessage = '';
      this.countdown = 0;
      clearInterval(this.timer);
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

p {
  margin-bottom: 20px;
  color: #555;
}

.countdown {
  color: #666;
  font-size: 14px;
  margin: 10px 0;
}

/* 添加錯誤和成功訊息樣式 */
.error-message, .success-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 4px;
  margin: 15px 0;
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

.secondary-btn {
  background-color: #f0f0f0;
  color: #333;
}

.secondary-btn:hover:not(:disabled) {
  background-color: #e0e0e0;
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
</style>