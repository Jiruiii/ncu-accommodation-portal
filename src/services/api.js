const API_BASE_URL = "";

export const apiService = {
  // 通用 API 方法
  async get(endpoint, requireAuth = false) {
    try {
      const headers = {
        "Content-Type": "application/json",
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: headers,
        credentials: "include",
      });

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage =
            errorData.message || `HTTP error! status: ${response.status}`;
        } catch (e) {
          errorMessage = `HTTP error! status: ${response.status}`;
        }

        if (response.status === 401) {
          console.error("認證錯誤:", errorMessage);
          if (requireAuth) {
            window.location.href = "/admin/login";
            throw new Error("請先登入");
          }
        }

        throw new Error(errorMessage);
      }

      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async post(endpoint, data, requireAuth = false) {
    try {
      const headers = {
        "Content-Type": "application/json",
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "POST",
        headers: headers,
        credentials: "include", // 發送 cookies
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage =
            errorData.message || `HTTP error! status: ${response.status}`;
        } catch (e) {
          errorMessage = `HTTP error! status: ${response.status}`;
        }

        if (response.status === 401 && requireAuth) {
          window.location.href = "/admin/login";
          throw new Error("請先登入");
        }

        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async put(endpoint, data, requireAuth = false) {
    try {
      const headers = {
        "Content-Type": "application/json",
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "PUT",
        headers: headers,
        credentials: "include", // 發送 cookies
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage =
            errorData.message || `HTTP error! status: ${response.status}`;
        } catch (e) {
          errorMessage = `HTTP error! status: ${response.status}`;
        }

        if (response.status === 401 && requireAuth) {
          window.location.href = "/admin/login";
          throw new Error("請先登入");
        }

        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  async delete(endpoint, requireAuth = false) {
    try {
      const headers = {
        "Content-Type": "application/json",
      };

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: "DELETE",
        headers: headers,
        credentials: "include", // 發送 cookies
      });

      if (!response.ok) {
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage =
            errorData.message || `HTTP error! status: ${response.status}`;
        } catch (e) {
          errorMessage = `HTTP error! status: ${response.status}`;
        }

        if (response.status === 401 && requireAuth) {
          window.location.href = "/admin/login";
          throw new Error("請先登入");
        }

        throw new Error(errorMessage);
      }
      return await response.json();
    } catch (error) {
      console.error("API request failed:", error);
      throw error;
    }
  },

  // 身份驗證相關 API
  auth: {
    login: (userData) => apiService.post("/api/auth/login", userData),
    register: (userData) => apiService.post("/api/auth/register", userData),
    logout: () => apiService.post("/api/auth/logout"),
    checkSession: () => apiService.get("/api/auth/status"),
    forgotPassword: (email) =>
      apiService.post("/api/auth/forgot-password", { email }),
    resetPassword: (token, newPassword) =>
      apiService.post("/api/auth/reset-password", {
        token,
        password: newPassword,
      }),

    // NCU Portal OAuth 相關
    portal: {
      // 用於Portal綁定的URL
      getBindingUrl: () => {
        const clientId = "20250507153856UyZ8gD4BXoY5";
        const redirectUri = encodeURIComponent(
          `${window.location.origin}/auth/callback`
        );
        const scopes = encodeURIComponent(
          "id identifier chinese-name student-id academy-records email mobile-phone"
        );
        const state = generateRandomState();

        // 保存 state 到 localStorage
        localStorage.setItem("oauth_state", state);
        localStorage.setItem("oauth_action", "binding");

        return `https://portal.ncu.edu.tw/oauth2/authorization?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=${state}`;
      },

      // Portal 快速登入
      getLoginUrl: () => {
        const clientId = "20250507153856UyZ8gD4BXoY5";
        const redirectUri = encodeURIComponent(
          `${window.location.origin}/auth/callback`
        );
        const scopes = encodeURIComponent(
          "id identifier chinese-name student-id academy-records email mobile-phone"
        );
        const state = generateRandomState();

        // 保存 state 到 localStorage
        localStorage.setItem("oauth_state", state);
        localStorage.setItem("oauth_action", "login");

        return `https://portal.ncu.edu.tw/oauth2/authorization?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=${state}`;
      },

      // 註冊時獲取 Portal 資訊
      getInfoUrl: () => {
        const clientId = "20250507153856UyZ8gD4BXoY5";
        const redirectUri = encodeURIComponent(
          `${window.location.origin}/auth/callback`
        );
        const scopes = encodeURIComponent(
          "id identifier chinese-name student-id academy-records email mobile-phone"
        );
        const state = generateRandomState();

        // 保存 state 到 localStorage
        localStorage.setItem("oauth_state", state);
        localStorage.setItem("oauth_action", "getinfo");
        localStorage.setItem("bindingForRegistration", "true");

        return `https://portal.ncu.edu.tw/oauth2/authorization?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code&scope=${scopes}&state=${state}`;
      },
      handleCallback: (code, action_type) =>
        apiService.post("/api/auth/portal-callback", { code, action_type }),
    },
  },

  // 住宿相關 API
  accommodations: {
    getAccommodations: () => apiService.get("/api/accommodations"),
    getById: (id) => apiService.get(`/api/accommodations/${id}`),
    create: (data) => apiService.post("/api/accommodations", data),
    update: (id, data) => apiService.put(`/api/accommodations/${id}`, data),
    delete: (id) => apiService.delete(`/api/accommodations/${id}`),
    favorites: {
      getFavorites: () => apiService.get("/api/accommodations/favorites"),
      toggleFavorite: (id) =>
        apiService.post(`/api/accommodations/favorites/toggle/${id}`),
      addFavorite: (id) =>
        apiService.post(`/api/accommodations/favorites/${id}`),
      removeFavorite: (id) =>
        apiService.post(`/api/accommodations/favorites/delete/${id}`),
      checkFavoriteStatus: (id) =>
        apiService.get(`/api/accommodations/favorites/status/${id}`),
    },
  },

  // 評價相關 API
  reviews: {
    getByAccommodationId: (id) =>
      apiService.get(`/api/reviews/accommodation/${id}`),
    create: (data) => apiService.post("/api/reviews", data),
    update: (id, data) => apiService.put(`/api/reviews/${id}`, data),
    delete: (id) => apiService.delete(`/api/reviews/${id}`),
  },

  // 用戶相關 API
  users: {
    getProfile: () => apiService.get("/api/users/profile"),
    updateProfile: (data) => apiService.put("/api/users/profile", data),
    uploadProfileImage: (formData) =>
      apiService.post("/api/users/profile/image", formData),
    changePassword: (data) =>
      apiService.post("/api/users/change-password", data),
    unbindPortal: () => apiService.post("/api/users/unbind-portal"),
    updateEmail: (email) =>
      apiService.post("/api/users/update-email", { email }),
    updatePhone: (phone) =>
      apiService.post("/api/users/update-phone", { phone }),
  },

  // 維修請求相關 API
  maintenance: {
    getAll: () => apiService.get("/api/maintenance"),
    getById: (id) => apiService.get(`/api/maintenance/${id}`),
    create: (data) => apiService.post("/api/maintenance", data),
    update: (id, data) => apiService.put(`/api/maintenance/${id}`, data),
    resolve: (id, data) =>
      apiService.post(`/api/maintenance/${id}/resolve`, data),
  },

  // 管理員相關 API
  admin: {
    // 資料庫管理 API
    getTables: () => apiService.get("/api/admin/tables", true),
    getTableStructure: (tableName) =>
      apiService.get(`/api/admin/tables/${tableName}/structure`, true),
    getTableData: (tableName, params = {}) => {
      const queryString = new URLSearchParams(params).toString();
      return apiService.get(
        `/api/admin/tables/${tableName}/data?${queryString}`,
        true
      );
    },
    updateTableRow: (tableName, rowId, data) =>
      apiService.put(
        `/api/admin/tables/${tableName}/data/${rowId}`,
        data,
        true
      ),
    deleteTableRow: (tableName, rowId) =>
      apiService.delete(`/api/admin/tables/${tableName}/data/${rowId}`, true),
    addTableRow: (tableName, data) =>
      apiService.post(`/api/admin/tables/${tableName}/data`, data, true),
    getDashboard: () => apiService.get("/api/admin/dashboard", true),

    getUsers: (params = {}) => {
      const filteredParams = {};
      for (const [key, value] of Object.entries(params)) {
        if (value !== undefined && value !== "undefined") {
          filteredParams[key] = value;
        }
      }

      const queryString = new URLSearchParams(filteredParams).toString();
      return apiService.get(`/api/admin/users?${queryString}`, true);
    },
    getUser: (userId) => apiService.get(`/api/admin/users/${userId}`, true),
    createUser: (userData) =>
      apiService.post("/api/admin/users", userData, true),
    updateUser: (userId, userData) =>
      apiService.put(`/api/admin/users/${userId}`, userData, true),
    deleteUser: (userId) =>
      apiService.post(`/api/admin/delete/users/${userId}`, true),
  },

  verification: {
    sendEmailVerification: async (email) =>
      apiService.post("/api/verification/send-email", { email }),
    sendPhoneVerification: async (phone) =>
      apiService.post("/api/verification/send-phone", { phone }),
    verifyEmail: async (code) =>
      apiService.post("/api/verification/verify-email", { code }),
    verifyPhone: async (code) =>
      apiService.post("/api/verification/verify-phone", { code }),
  },

  landlord: {
    getDashboard: () => apiService.get("/api/landlord/dashboard"),

    // 房東認證
    submitVerification: (formData) =>
      apiService.post("/api/landlord/verification", formData),
    getVerificationStatus: () =>
      apiService.get("/api/landlord/verification/status"),

    // 房源管理
    getProperties: () => apiService.get("/api/landlord/properties"),
    getProperty: (id) => apiService.get(`/api/landlord/properties/${id}`),
    createProperty: (data) => apiService.post("/api/landlord/properties", data),
    updateProperty: (id, data) =>
      apiService.put(`/api/landlord/properties/${id}`, data),
    deleteProperty: (id) => apiService.delete(`/api/landlord/properties/${id}`),
    updatePropertyStatus: (id, status) =>
      apiService.post(`/api/landlord/properties/${id}/status`, { status }),

    // 訊息管理
    getMessages: () => apiService.get("/api/landlord/messages"),
    getMessage: (id) => apiService.get(`/api/landlord/messages/${id}`),
    replyMessage: (id, content) =>
      apiService.post(`/api/landlord/messages/${id}/reply`, { content }),

    // 租賃合同
    getContracts: () => apiService.get("/api/landlord/contracts"),
    getContract: (id) => apiService.get(`/api/landlord/contracts/${id}`),
    createContract: (data) => apiService.post("/api/landlord/contracts", data),
    updateContract: (id, data) =>
      apiService.put(`/api/landlord/contracts/${id}`, data),
  },
};

// 生成隨機狀態碼防止CSRF攻擊
function generateRandomState() {
  return (
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15)
  );
}

export default apiService;
