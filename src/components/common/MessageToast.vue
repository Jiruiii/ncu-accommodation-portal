<template>
    <Transition name="toast">
      <div v-if="visible" :class="['message-toast', type]">
        <span class="toast-text">{{ message }}</span>
        <button v-if="showCloseButton" @click="close" class="close-btn">
          <span class="material-icons">close</span>
        </button>
      </div>
    </Transition>
  </template>
  
  <script>
  export default {
    name: "MessageToast",
    props: {
      message: {
        type: String,
        default: ""
      },
      type: {
        type: String,
        default: "info",
        validator: (value) => ["success", "error", "info", "warning"].includes(value)
      },
      duration: {
        type: Number,
        default: 3000 // 預設顯示3秒
      },
      visible: {
        type: Boolean,
        default: false
      },
      showCloseButton: {
        type: Boolean,
        default: true
      }
    },
    emits: ["close"],
    watch: {
      visible(newVal) {
        if (newVal && this.duration > 0) {
          this.startTimer();
        }
      }
    },
    methods: {
      startTimer() {
        if (this.timer) {
          clearTimeout(this.timer);
        }
        this.timer = setTimeout(() => {
          this.close();
        }, this.duration);
      },
      close() {
        if (this.timer) {
          clearTimeout(this.timer);
        }
        this.$emit("close");
      }
    },
    data() {
      return {
        timer: null
      };
    },
    beforeUnmount() {
      if (this.timer) {
        clearTimeout(this.timer);
      }
    }
  };
  </script>
  
  <style scoped>
  .message-toast {
    position: fixed;
    top: 20px;
    left: 50%;
    transform: translateX(-50%);
    padding: 12px 20px;
    border-radius: 8px;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    z-index: 9999;
    min-width: 250px;
    max-width: 90%;
  }
  
  .toast-text {
    flex: 1;
  }
  
  .success {
    background-color: #4caf50;
    color: white;
  }
  
  .error {
    background-color: #ff6b6b;
    color: white;
  }
  
  .info {
    background-color: #2196f3;
    color: white;
  }
  
  .warning {
    background-color: #ff9800;
    color: white;
  }
  
  .close-btn {
    background: transparent;
    border: none;
    color: inherit;
    opacity: 0.7;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    margin: 0;
    font-size: 16px;
  }
  
  .close-btn:hover {
    opacity: 1;
  }
  
  .toast-enter-active,
  .toast-leave-active {
    transition: all 0.3s ease;
  }
  
  .toast-enter-from {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  
  .toast-leave-to {
    opacity: 0;
    transform: translate(-50%, -20px);
  }
  </style>