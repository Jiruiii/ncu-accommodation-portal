<template>
  <div class="auth-callback-container">
    <div class="loading">
      <div class="spinner"></div>
      <p>驗證身份中，請稍候...</p>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import apiService from '@/services/api';

export default {
  setup() {
    const router = useRouter();
    
    onMounted(async () => {
      try {
        // 從 URL 獲取認證碼和狀態
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const storedState = localStorage.getItem('oauth_state');
        
        // 清除儲存的狀態
        localStorage.removeItem('oauth_state');
        
        // 驗證狀態是否匹配
        if (!state || state !== storedState) {
          throw new Error('無效的狀態值，可能是跨站請求偽造（CSRF）攻擊');
        }
        
        // 使用 API 服務處理回調
        const data = await apiService.auth.portal.handleCallback(code);
        
        // 存儲認證信息
        localStorage.setItem('user', JSON.stringify(data.user));
        
        // 跳轉到主頁
        router.push({
          path: '/accommodation-list',
          query: { welcome: true }
        });
        
      } catch (error) {
        console.error('SSO 登入錯誤:', error);
        
        // 跳轉回登入頁並顯示錯誤
        router.push({
          path: '/login',
          query: { error: encodeURIComponent(error.message) }
        });
      }
    });
    
    return {};
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