import apiService from "@/services/api";
import router from "@/router";

// 使用 sessionStorage 替代 localStorage 來儲存敏感資訊
// sessionStorage 會在瀏覽器關閉時自動清除
const getStoredUser = () => {
  try {
    // 優先使用 sessionStorage (較安全)
    const sessionUser = sessionStorage.getItem("user");
    if (sessionUser) {
      return JSON.parse(sessionUser);
    }

    // 當 sessionStorage 無資料時，再檢查 localStorage (用於"記住我"功能)
    const localUser = localStorage.getItem("user");
    if (localUser) {
      // 從 localStorage 讀取後，優先存入 sessionStorage 以提高安全性
      const userData = JSON.parse(localUser);
      sessionStorage.setItem("user", JSON.stringify(userData));
      return userData;
    }

    return null;
  } catch (error) {
    console.error("讀取用戶資料失敗:", error);
    return null;
  }
};

// 根據「記住我」選項選擇適當的儲存方式
const saveUserData = (userData, rememberMe = false) => {
  try {
    // 總是存入 sessionStorage (會在關閉瀏覽器時清除)
    sessionStorage.setItem("user", JSON.stringify(userData));

    // 如果用戶選擇「記住我」，同時存入 localStorage
    if (rememberMe) {
      // 注意：可以考慮僅存儲必要的非敏感資訊
      const safeUserData = {
        ...userData,
        // 移除敏感資訊，例如：
        // token: undefined,  // 不儲存完整 token
        // tokenExpiry: userData.tokenExpiry
      };
      localStorage.setItem("user", JSON.stringify(safeUserData));
    } else {
      // 如果未選擇「記住我」，確保清除 localStorage 中的使用者資料
      localStorage.removeItem("user");
    }
  } catch (error) {
    console.error("儲存用戶資料失敗:", error);
  }
};

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
    rememberMe: false, // 記住我選項
    lastVerified: 0, // 最後驗證時間戳
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

    SET_REMEMBER_ME(state, status) {
      state.rememberMe = status;
    },

    UPDATE_USER_PROFILE(state, profileData) {
      state.user = { ...state.user, ...profileData };
    },

    SET_LAST_VERIFIED(state, timestamp) {
      state.lastVerified = timestamp;
    },
  },

  actions: {
    // 登入動作
    async login({ commit, state }, { email, password, rememberMe }) {
      try {
        commit("SET_LOADING", true);
        commit("SET_AUTH_ERROR", null);
        commit("SET_REMEMBER_ME", rememberMe);

        const response = await apiService.auth.login({ email, password });

        if (response && response.success) {
          // 儲存使用者資料
          commit("SET_USER", response.user);
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
    async logout({ commit }) {
      try {
        await apiService.auth.logout();
      } catch (error) {
        console.error("登出失敗:", error);
      } finally {
        commit("SET_USER", null);
        clearUserData();
        // 導向登入頁
        router.push("/login");
      }
    },

    // 註冊動作
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
        if (now - state.lastVerified < 300000) {
          // 5分鐘內已驗證
          return state.user;
        }

        commit("SET_LOADING", true);
        const response = await apiService.users.getProfile();

        if (response && response.user) {
          commit("UPDATE_USER_PROFILE", response.user);

          // 更新存儲的資料
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

          // 更新存儲的資料
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

          // 更新存儲的資料
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

    // 修改密碼
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
        if (now - state.lastVerified < 300000) {
          // 5分鐘內已驗證
          return true;
        }

        // 使用 verifyToken API
        const response = await apiService.auth.verifyToken();

        if (response && response.valid) {
          // 如果用戶資料有更新，更新 store
          if (response.user) {
            commit("SET_USER", response.user);
            // 更新儲存的資料
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

    // 檢查用戶是否已登入並有相應權限
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
  },
};
