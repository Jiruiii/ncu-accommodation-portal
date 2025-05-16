<template>
  <div class="auth-callback-container">
    <div class="loading">
      <div class="spinner"></div>
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
import apiService from '@/services/api';

export default {
  setup() {
    const router = useRouter();
    const store = useStore();
    const message = ref('驗證身份中，請稍候...');
    
    onMounted(async () => {
      try {
        // 從 URL 獲取認證碼和狀態
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const storedState = localStorage.getItem('oauth_state');
        const actionType = localStorage.getItem('oauth_action');
        
        // 清除儲存的狀態
        localStorage.removeItem('oauth_state');
        
        // 驗證狀態是否匹配以防止 CSRF 攻擊
        if (!state || state !== storedState) {
          throw new Error('無效的狀態值，可能是跨站請求偽造（CSRF）攻擊');
        }
        
        // 使用 API 服務處理回調
        const response = await apiService.auth.portal.handleCallback(code, actionType);
        
        // 根據操作類型處理結果
        switch (actionType) {
          case 'login':
            // 處理登入
            handleLoginResponse(response);
            break;
          case 'binding':
            // 處理綁定
            handleBindingResponse(response);
            break;
          case 'getinfo':
            // 處理獲取資訊
            handleGetInfoResponse(response);
            break;
          default:
            throw new Error(`未知的操作類型: ${actionType}`);
        }
      } catch (error) {
        console.error('Portal 處理錯誤:', error);
        message.value = `處理失敗: ${error.message}`;
        setTimeout(() => {
          router.push({
            path: '/login',
            query: { error: encodeURIComponent(message.value) }
          });
        }, 2000);
      }
    });
    
    // 處理登入回應
    const handleLoginResponse = (response) => {
      if (response.success) {
        // 登入成功
        localStorage.removeItem('oauth_action');
        
        // 存儲用戶資訊
        localStorage.setItem('user', JSON.stringify(response.user));
        
        message.value = 'Portal 快速登入成功，正在跳轉...';
        setTimeout(() => {
          router.push('/profile');
          store.commit('SET_CURRENTROUTE', 'profile');
        }, 1000);
      } else {
        // 登入失敗
        message.value = response.message || 'Portal 登入失敗';
        setTimeout(() => {
          router.push({
            path: '/login',
            query: { error: encodeURIComponent(message.value) }
          });
        }, 2000);
      }
    };
    
    // 處理綁定回應
    const handleBindingResponse = (response) => {
      if (response.success) {
        message.value = 'Portal 綁定成功！';
        setTimeout(() => {
          router.push('/profile');
        }, 1500);
      } else {
        message.value = response.message || 'Portal 綁定失敗';
        setTimeout(() => {
          router.push({
            path: '/profile',
            query: { error: encodeURIComponent(message.value) }
          });
        }, 2000);
      }
    };
    
    // 處理獲取資訊回應
    const handleGetInfoResponse = (response) => {
      if (response.success) {
        // 儲存 Portal 資訊用於後續註冊
        localStorage.setItem('portalBound', 'true');
        localStorage.setItem('portalInfo', JSON.stringify(response.portal_data));
        
        message.value = 'Portal 資訊獲取成功，返回註冊流程...';
        setTimeout(() => {
          router.push({
            path: '/login',
            query: { register: 'true' }
          });
        }, 1500);
      } else {
        // 獲取資訊失敗
        message.value = response.message || 'Portal 資訊獲取失敗';
        setTimeout(() => {
          router.push({
            path: '/login',
            query: { error: encodeURIComponent(message.value) }
          });
        }, 2000);
      }
    };
    
    return {
      message
    };
  }
}
</script>

<style scoped>
.auth-callback-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #272727;
  color: white;
}

.loading {
  text-align: center;
}

.spinner {
  width: 50px;
  height: 50px;
  margin: 0 auto 20px;
  border: 4px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  border-top-color: #66b3ff;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>