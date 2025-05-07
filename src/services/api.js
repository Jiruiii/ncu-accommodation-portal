// src/services/api.js

const API_BASE_URL = process.env.VUE_APP_API_BASE_URL || "http://localhost:5000";

export const apiService = {
  // 通用 API 方法
  async get(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async post(endpoint, data) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async put(endpoint, data) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async delete(endpoint) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "DELETE",
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  // 身份驗證相關 API
  auth: {
    login: (credentials) => apiService.post('/api/auth/login', credentials),
    register: (userData) => apiService.post('/api/auth/register', userData),
    logout: () => apiService.post('/api/auth/logout'),
    refreshToken: (refreshToken) => apiService.post('/api/auth/refresh', { refresh_token: refreshToken }),
    forgotPassword: (email) => apiService.post('/api/auth/forgot-password', { email }),
    resetPassword: (token, newPassword) => apiService.post('/api/auth/reset-password', { token, password: newPassword }),
    
    // NCU Portal OAuth 相關
    portal: {
      // 獲取 Portal 登入 URL
      getLoginUrl: () => {
        const clientId = "20250507153856UyZ8gD4BXoY5";
        const redirectUri = encodeURIComponent(`${window.location.origin}/auth/callback`);
        const scopes = encodeURIComponent('id identifier chinese-name student-id academy-records email mobile-phone');
        const state = generateRandomState();
        
        // 保存 state 到 localStorage
        localStorage.setItem('oauth_state', state);
        
        return `https://portal.ncu.edu.tw/oauth2/authorization?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=${state}`;
      },
      
      // 處理 OAuth 回調
      handleCallback: (code) => apiService.post('/api/auth/portal-callback', { code }),
    }
  },
  
  // 住宿相關 API
  accommodations: {
    getAll: (params = {}) => {
      const queryString = new URLSearchParams(params).toString();
      return apiService.get(`/api/accommodations?${queryString}`);
    },
    getById: (id) => apiService.get(`/api/accommodations/${id}`),
    create: (data) => apiService.post('/api/accommodations', data),
    update: (id, data) => apiService.put(`/api/accommodations/${id}`, data),
    delete: (id) => apiService.delete(`/api/accommodations/${id}`),
    getFavorites: () => apiService.get('/api/accommodations/favorites'),
    toggleFavorite: (id) => apiService.post(`/api/accommodations/${id}/favorite`),
  },
  
  // 評價相關 API
  reviews: {
    getByAccommodationId: (id) => apiService.get(`/api/reviews/accommodation/${id}`),
    create: (data) => apiService.post('/api/reviews', data),
    update: (id, data) => apiService.put(`/api/reviews/${id}`, data),
    delete: (id) => apiService.delete(`/api/reviews/${id}`),
  },
  
  // 用戶相關 API
  users: {
    getProfile: () => apiService.get('/api/users/profile'),
    updateProfile: (data) => apiService.put('/api/users/profile', data),
    changePassword: (data) => apiService.post('/api/users/change-password', data),
    verifyStudent: (data) => apiService.post('/api/users/verify-student', data),
  },
  
  // 維修請求相關 API
  maintenance: {
    getAll: () => apiService.get('/api/maintenance'),
    getById: (id) => apiService.get(`/api/maintenance/${id}`),
    create: (data) => apiService.post('/api/maintenance', data),
    update: (id, data) => apiService.put(`/api/maintenance/${id}`, data),
    resolve: (id, data) => apiService.post(`/api/maintenance/${id}/resolve`, data),
  },
};

// 生成隨機狀態碼防止CSRF攻擊
function generateRandomState() {
  return Math.random().toString(36).substring(2, 15) + 
         Math.random().toString(36).substring(2, 15);
}

export default apiService;