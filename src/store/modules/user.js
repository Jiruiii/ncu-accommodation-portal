import apiService from "@/services/api";
import router from "@/router";

// 獲取存儲的用戶資料，優先使用 sessionStorage
const getStoredUser = () => {
  try {
    // 優先從 sessionStorage 讀取（瀏覽器關閉時會自動清除）
    const sessionUser = sessionStorage.getItem("user");
    if (sessionUser) {
      return JSON.parse(sessionUser);
    }

    // 如果 sessionStorage 中沒有，且允許使用 localStorage，則嘗試從 localStorage 讀取
    const localUser = localStorage.getItem("user");
    if (localUser) {
      // 找到 localStorage 中的用戶資料，將其也存入 sessionStorage
      const userData = JSON.parse(localUser);
      sessionStorage.setItem("user", localUser);
      return userData;
    }

    return null;
  } catch (error) {
    console.error("讀取用戶資料失敗:", error);
    return null;
  }
};

// 保存用戶資料，依據 rememberMe 決定是否同時存入 localStorage
const saveUserData = (userData, rememberMe = false) => {
  try {
    // 總是存入 sessionStorage
    sessionStorage.setItem("user", JSON.stringify(userData));
    
    // 如果選擇記住我，也存入 localStorage
    if (rememberMe) {
      localStorage.setItem("user", JSON.stringify(userData));
    } else {
      // 確保清除 localStorage 中的資料
      localStorage.removeItem("user");
    }
  } catch (error) {
    console.error("儲存用戶資料失敗:", error);
  }
};

// 清除用戶資料
const clearUserData = () => {
  sessionStorage.removeItem("user");
  localStorage.removeItem("user");
};

export default {
  namespaced: true,

  state: {
    user: getStoredUser(),
    isAuthenticated: !!getStoredUser(),
    authError: null,
    loading: false,
    lastVerified: 0, // 最後驗證時間戳
    rememberMe: localStorage.getItem("user") !== null, // 檢查 localStorage 判斷是否記住用戶
  },

  mutations: {
    SET_USER(state, user) {
      state.user = user;
      state.isAuthenticated = !!user;
      state.authError = null;
    },

    SET_AUTH_ERROR(state, error) {
      state.authError = error;
    },

    SET_LOADING(state, status) {
      state.loading = status;
    },

    UPDATE_USER_PROFILE(state, profileData) {
      state.user = { ...state.user, ...profileData };
    },

    SET_LAST_VERIFIED(state, timestamp) {
      state.lastVerified = timestamp;
    },
    
    SET_REMEMBER_ME(state, status) {
      state.rememberMe = status;
    },
  },

  actions: {
    // 登入動作
    async login({ commit, state }, { email, password, rememberMe = false }) {
      try {
        commit("SET_LOADING", true);
        commit("SET_AUTH_ERROR", null);

        const response = await apiService.auth.login({ email, password });

        if (response && response.success) {
          // 儲存使用者資料
          commit("SET_USER", response.user);
          commit("SET_REMEMBER_ME", rememberMe);
          saveUserData(response.user, rememberMe);
          commit("SET_LAST_VERIFIED", Date.now());
          return true;
        } else {
          commit("SET_AUTH_ERROR", response?.message || "登入失敗");
          return false;
        }
      } catch (error) {
        commit("SET_AUTH_ERROR", error.message || "登入請求失敗");
        return false;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 登出動作
    async logout({ commit, state }) {
      try {
        // 先導航到登入頁，再清除資料，避免渲染錯誤
        router.push("/login");

        // 短暫延遲確保導航完成
        setTimeout(async () => {
          // 清除用戶資料
          commit("SET_USER", null);
          commit("SET_REMEMBER_ME", false);
          clearUserData();

          // 調用 API 登出
          try {
            await apiService.auth.logout();
          } catch (error) {
            console.error("API 登出請求失敗:", error);
            // 即使 API 呼叫失敗，我們仍然希望客戶端登出
          }
        }, 100);
      } catch (error) {
        console.error("登出失敗:", error);

        // 即使出錯，也要確保用戶被登出
        commit("SET_USER", null);
        commit("SET_REMEMBER_ME", false);
        clearUserData();
      }
    },

    // 註冊動作 (保持不變)
    async register({ commit }, userData) {
      try {
        commit("SET_LOADING", true);
        commit("SET_AUTH_ERROR", null);

        const response = await apiService.auth.register(userData);

        if (response && response.success) {
          // 註冊成功，可以自動登入或導向登入頁
          return true;
        } else {
          commit("SET_AUTH_ERROR", response?.message || "註冊失敗");
          return false;
        }
      } catch (error) {
        commit("SET_AUTH_ERROR", error.message || "註冊請求失敗");
        return false;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 獲取最新的使用者資料
    async fetchUserProfile({ commit, state }) {
      try {
        // 如果最近已驗證過，跳過再次獲取
        const now = Date.now();
        if (now - state.lastVerified < 300000) { // 5分鐘內已驗證
          return state.user;
        }

        commit("SET_LOADING", true);
        const response = await apiService.users.getProfile();

        if (response && response.user) {
          commit("UPDATE_USER_PROFILE", response.user);

          // 更新存儲的資料，保持 rememberMe 狀態
          saveUserData({ ...state.user, ...response.user }, state.rememberMe);
          commit("SET_LAST_VERIFIED", now);

          return response.user;
        }

        return state.user;
      } catch (error) {
        console.error("獲取用戶資料失敗:", error);
        return state.user;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 更新使用者資料
    async updateProfile({ commit, state }, profileData) {
      try {
        commit("SET_LOADING", true);

        const response = await apiService.users.updateProfile(profileData);

        if (response && response.success) {
          commit("UPDATE_USER_PROFILE", profileData);

          // 更新存儲的資料，保持 rememberMe 狀態
          saveUserData({ ...state.user, ...profileData }, state.rememberMe);
          return true;
        } else {
          return false;
        }
      } catch (error) {
        console.error("更新用戶資料失敗:", error);
        return false;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 更新使用者頭像
    async updateProfileImage({ commit, state }, formData) {
      try {
        commit("SET_LOADING", true);

        const response = await apiService.users.uploadProfileImage(formData);

        if (response && response.profile_image) {
          const profileData = { profile_image: response.profile_image };
          commit("UPDATE_USER_PROFILE", profileData);

          // 更新存儲的資料，保持 rememberMe 狀態
          saveUserData({ ...state.user, ...profileData }, state.rememberMe);
          return response.profile_image;
        } else {
          return null;
        }
      } catch (error) {
        console.error("上傳頭像失敗:", error);
        return null;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 修改密碼 (保持不變)
    async changePassword({ commit }, { currentPassword, newPassword }) {
      try {
        commit("SET_LOADING", true);

        const response = await apiService.users.changePassword({
          current_password: currentPassword,
          new_password: newPassword,
        });

        return response && response.success;
      } catch (error) {
        console.error("修改密碼失敗:", error);
        return false;
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 修改 verifyAuth 方法
    async verifyAuth({ commit, dispatch, state }) {
      try {
        // 如果用戶未登入或沒有 token，直接返回 false
        if (!state.isAuthenticated || !state.user) {
          return false;
        }

        // 如果最近已驗證過，跳過再次驗證
        const now = Date.now();
        if (now - state.lastVerified < 300000) { // 5分鐘內已驗證
          return true;
        }

        // 使用 verifyToken API
        const response = await apiService.auth.verifyToken();

        if (response && response.valid) {
          // 如果用戶資料有更新，更新 store
          if (response.user) {
            commit("SET_USER", response.user);
            // 更新儲存的資料，保持 rememberMe 狀態
            saveUserData(response.user, state.rememberMe);
          }

          commit("SET_LAST_VERIFIED", now);
          return true;
        } else {
          // token 無效，登出用戶
          await dispatch("logout");
          return false;
        }
      } catch (error) {
        console.error("驗證 token 失敗:", error);

        // 如果收到 401 錯誤，說明 token 無效，登出用戶
        if (error.response && error.response.status === 401) {
          await dispatch("logout");
          return false;
        }

        // 其他錯誤，保持當前狀態
        return state.isAuthenticated;
      }
    },

    // 檢查用戶是否已登入並有相應權限 (保持不變)
    async checkAuth({ dispatch, state }, requiredRole = null) {
      // 先驗證登入狀態
      const isAuthenticated = await dispatch("verifyAuth");

      if (!isAuthenticated) {
        return false;
      }

      // 如果需要檢查角色
      if (requiredRole) {
        const userRole = state.user?.user_role;

        // 超級管理員可以訪問所有頁面
        if (userRole === "superuser") {
          return true;
        }

        // 檢查一般角色
        if (requiredRole === "admin") {
          return ["admin", "superuser"].includes(userRole);
        } else if (requiredRole === "landlord") {
          return ["landlord", "admin", "superuser"].includes(userRole);
        } else if (requiredRole === "student") {
          return state.user?.is_verified || false;
        }

        return false;
      }

      // 如果不需要特定角色，只要已登入即可
      return true;
    },
  },

  getters: {
    // 獲取當前用戶資料
    currentUser: (state) => state.user,

    // 檢查是否已登入
    isLoggedIn: (state) => state.isAuthenticated,

    // 檢查是否為管理員
    isAdmin: (state) => {
      const role = state.user?.user_role;
      return role === "admin" || role === "superuser";
    },

    // 檢查是否為超級管理員
    isSuperuser: (state) => state.user?.user_role === "superuser",

    // 檢查是否為房東
    isLandlord: (state) => {
      const role = state.user?.user_role;
      return role === "landlord" || role === "admin" || role === "superuser";
    },

    // 檢查是否為已驗證學生
    isVerifiedStudent: (state) => state.user?.is_verified || false,

    // 登入錯誤訊息
    authError: (state) => state.authError,

    // 載入狀態
    isLoading: (state) => state.loading,

    // 獲取頭像 URL
    avatarUrl: (state) => {
      if (!state.user || !state.user.profile_image) {
        return require("@/assets/default-avatar.jpg");
      }

      // 如果已經是完整 URL
      if (state.user.profile_image.startsWith("http")) {
        return state.user.profile_image;
      }

      // 否則拼接 API 基礎 URL
      return `http://localhost:5000${state.user.profile_image}`;
    },

    // 添加 rememberMe 狀態
    rememberMe: (state) => state.rememberMe,
  },
};
