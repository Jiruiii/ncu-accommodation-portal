<template>
    <div v-if="show" class="modal-overlay">
      <div class="modal-content">
        <h3>修改電子郵件</h3>
        <p>修改郵箱地址後，您需要重新驗證新的郵箱地址。</p>
  
        <div class="form-group">
          <label>當前電子郵件</label>
          <div class="current-email">{{ currentEmail }}</div>
        </div>
  
        <div class="form-group">
          <label for="new-email">新電子郵件</label>
          <input
            id="new-email"
            v-model="newEmail"
            type="email"
            placeholder="請輸入新的電子郵件地址"
            required
          />
          <div v-if="emailError" class="form-error">{{ emailError }}</div>
        </div>
  
        <div class="form-group">
          <label for="password">密碼驗證</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="請輸入當前密碼"
            required
          />
          <div v-if="passwordError" class="form-error">{{ passwordError }}</div>
        </div>
  
        <div class="modal-buttons">
          <button
            @click="changeEmail"
            class="action-btn"
            :disabled="isProcessing || !newEmail || !password || !isValidEmail"
          >
            <span v-if="isProcessing" class="loading-spinner"></span>
            {{ isProcessing ? '處理中...' : '確認修改' }}
          </button>
          <button @click="cancel" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "EmailChangeModal",
    props: {
      show: {
        type: Boolean,
        default: false
      },
      currentEmail: {
        type: String,
        required: true
      }
    },
    data() {
      return {
        newEmail: "",
        password: "",
        isProcessing: false,
        emailError: "",
        passwordError: ""
      };
    },
    computed: {
      isValidEmail() {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(this.newEmail);
      }
    },
    watch: {
      newEmail() {
        this.emailError = "";
      },
      password() {
        this.passwordError = "";
      }
    },
    methods: {
      changeEmail() {
        // 基本驗證
        if (!this.newEmail) {
          this.emailError = "請輸入新電子郵件";
          return;
        }
  
        if (!this.isValidEmail) {
          this.emailError = "請輸入有效的電子郵件地址";
          return;
        }
  
        if (!this.password) {
          this.passwordError = "請輸入密碼";
          return;
        }
  
        this.isProcessing = true;
  
        this.$emit("change", {
          newEmail: this.newEmail,
          password: this.password
        })
          .then(() => {
            this.reset();
            this.$emit("close");
          })
          .catch(error => {
            if (error.type === "email") {
              this.emailError = error.message;
            } else if (error.type === "password") {
              this.passwordError = error.message;
            } else {
              this.$emit("error", error.message);
            }
          })
          .finally(() => {
            this.isProcessing = false;
          });
      },
      cancel() {
        this.reset();
        this.$emit("close");
      },
      reset() {
        this.newEmail = "";
        this.password = "";
        this.emailError = "";
        this.passwordError = "";
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
    margin-bottom: 15px;
    color: #333;
    font-size: 1.5rem;
  }
  
  p {
    margin-bottom: 20px;
    color: #555;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #444;
  }
  
  .current-email {
    padding: 8px 12px;
    background-color: #f0f0f0;
    border-radius: 4px;
    font-size: 0.9rem;
    color: #555;
  }
  
  input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: border 0.3s;
  }
  
  input:focus {
    outline: none;
    border-color: #4a90e2;
  }
  
  .form-error {
    margin-top: 6px;
    color: #e53935;
    font-size: 0.8rem;
  }
  
  .modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 30px;
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
    border-top-color: white;
    margin-right: 8px;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  </style>