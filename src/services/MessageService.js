import { reactive } from 'vue';

// 創建一個響應式狀態對象來存儲消息
const state = reactive({
  message: '',
  type: 'info',
  visible: false,
  duration: 3000,
  showCloseButton: true
});

// 消息服務方法
export default {
  // 顯示成功消息
  success(message, options = {}) {
    this.show(message, { type: 'success', ...options });
  },
  
  // 顯示錯誤消息
  error(message, options = {}) {
    this.show(message, { type: 'error', ...options });
  },
  
  // 顯示資訊消息
  info(message, options = {}) {
    this.show(message, { type: 'info', ...options });
  },
  
  // 顯示警告消息
  warning(message, options = {}) {
    this.show(message, { type: 'warning', ...options });
  },
  
  // 顯示消息的主要方法
  show(message, options = {}) {
    // 如果已有消息顯示，先關閉它
    if (state.visible) {
      this.close();
      // 等待一小段時間再顯示新消息，避免動畫衝突
      setTimeout(() => {
        this._showMessage(message, options);
      }, 300);
    } else {
      this._showMessage(message, options);
    }
  },
  
  // 內部方法：設置消息內容並顯示
  _showMessage(message, options) {
    state.message = message;
    state.type = options.type || 'info';
    state.duration = options.duration !== undefined ? options.duration : 3000;
    state.showCloseButton = options.showCloseButton !== undefined ? options.showCloseButton : true;
    state.visible = true;
  },
  
  // 關閉消息
  close() {
    state.visible = false;
  },
  
  // 獲取當前狀態
  getState() {
    return state;
  }
};