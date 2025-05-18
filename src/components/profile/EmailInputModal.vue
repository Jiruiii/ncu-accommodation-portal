// filepath: c:\Users\USER\Desktop\ncu-accommodation-portal\src\components\profile\EmailInputModal.vue
<template>
  <div class="modal-overlay" @click.self="cancel">
    <div class="modal-content">
      <h3>重設密碼</h3>
      <p>請輸入您的電子郵件，我們將發送重設密碼連結給您</p>
      
      <div class="form-group">
        <input 
          type="email" 
          v-model="email" 
          placeholder="電子郵件" 
          class="form-input"
          @keyup.enter="confirm"
        />
        <div v-if="errorMessage" class="input-error">{{ errorMessage }}</div>
      </div>

      <div class="modal-buttons">
        <button @click="confirm" class="action-btn">
          <span v-if="isProcessing" class="loading-spinner"></span>
          {{ isProcessing ? '處理中...' : '繼續' }}
        </button>
        <button @click="cancel" class="cancel-btn">取消</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "EmailInputModal",
  props: {
    initialEmail: {
      type: String,
      default: ""
    }
  },
  data() {
    return {
      email: this.initialEmail,
      errorMessage: "",
      isProcessing: false
    };
  },
  methods: {
    confirm() {
      // 驗證電子郵件
      if (!this.email) {
        this.errorMessage = "請輸入電子郵件地址";
        return;
      }
      
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email)) {
        this.errorMessage = "請輸入有效的電子郵件地址";
        return;
      }
      
      this.isProcessing = true;
      
      // 確認電子郵件有效後，發出確認事件
      setTimeout(() => {
        this.isProcessing = false;
        this.$emit("confirm", this.email);
      }, 500);
    },
    cancel() {
      this.$emit("close");
    }
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
  color: #666;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
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

.modal-buttons {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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

.action-btn {
  background-color: #4a90e2;
  color: white;
}

.action-btn:hover {
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
</style>