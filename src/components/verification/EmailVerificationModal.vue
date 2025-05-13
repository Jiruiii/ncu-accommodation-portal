<template>
    <div v-if="show" class="modal-overlay">
      <div class="modal-content">
        <h3>驗證您的電子郵件</h3>
        <div v-if="!codeSent">
          <p>我們將發送驗證碼到您的電子郵件：{{ email }}</p>
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
        timer: null
      };
    },
    methods: {
      sendCode() {
        this.isProcessing = true;
        
        // 發送驗證碼 API 調用
        this.$emit('send', this.email)
          .then(() => {
            this.codeSent = true;
            this.startCountdown();
          })
          .catch(() => {
            // 錯誤處理由父組件負責
          })
          .finally(() => {
            this.isProcessing = false;
          });
      },
      verify() {
        if (!this.verificationCode) return;
        
        this.isVerifying = true;
        
        // 驗證碼驗證 API 調用
        this.$emit('verify', this.verificationCode)
          .then(() => {
            this.reset();
            this.$emit('close');
          })
          .catch(() => {
            // 錯誤處理由父組件負責
          })
          .finally(() => {
            this.isVerifying = false;
          });
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