import { createStore } from "vuex";
import apiService from "@/services/api";

export default createStore({
  state: {
    // 使用者資訊
    user: null,
    isAuthenticated: false,

    // 導航狀態
    navigationOpen: false,
    currentRoute: localStorage.getItem("currentRoute") || "home",
    isNavOpen: false,

    // 房源資料
    accommodations: [],
    filteredAccommodations: [],
    selectedAccommodation: null,
    favoriteIds: [],
    loading: false,
    dataInitialized: false,

    // 搜尋和篩選條件
    searchQuery: "",
    sortOption: "newest",
    filters: {
      minPrice: null,
      maxPrice: null,
      types: [],
      features: [],
    },

    // 地圖狀態
    mapView: false,
    mapCenter: { lat: 24.968, lng: 121.1944 }, // 中央大學座標
    mapZoom: 15,

    // 修改：評論資料結構，空物件準備從資料庫加載
    comments: {},
  },

  mutations: {
    SET_USER(state, user) {
      state.user = user;
      state.isAuthenticated = !!user;
    },

    TOGGLE_NAVIGATION(state) {
      state.navigationOpen = !state.navigationOpen;
    },

    SET_CURRENTROUTE(state, route) {
      state.currentRoute = route;
      localStorage.setItem("currentRoute", route);
    },

    OPEN_NAV(state) {
      state.isNavOpen = true;
    },

    CLOSE_NAV(state) {
      state.isNavOpen = false;
    },

    TOGGLE_NAV(state) {
      state.isNavOpen = !state.isNavOpen;
    },

    SET_ACCOMMODATIONS(state, accommodations) {
      state.accommodations = accommodations;
      state.filteredAccommodations = accommodations;
    },

    SET_DATA_INITIALIZED(state, value) {
      state.dataInitialized = value;
    },

    SET_LOADING(state, isLoading) {
      state.loading = isLoading;
    },

    SET_FILTERED_ACCOMMODATIONS(state, accommodations) {
      state.filteredAccommodations = accommodations;
    },

    SET_SELECTED_ACCOMMODATION(state, accommodation) {
      state.selectedAccommodation = accommodation;
    },

    SET_SEARCH_QUERY(state, query) {
      state.searchQuery = query;
    },

    SET_SORT_OPTION(state, option) {
      state.sortOption = option;
    },

    SET_FILTERS(state, filters) {
      state.filters = { ...state.filters, ...filters };
    },

    SET_FAVORITE_IDS(state, ids) {
      state.favoriteIds = ids;
    },

    TOGGLE_FAVORITE(state, id) {
      const index = state.favoriteIds.indexOf(id);
      if (index === -1) {
        state.favoriteIds.push(id);
      } else {
        state.favoriteIds.splice(index, 1);
      }
      // 儲存到 localStorage
      localStorage.setItem(
        "favoriteAccommodations",
        JSON.stringify(state.favoriteIds)
      );
    },

    REMOVE_FAVORITE(state, id) {
      const index = state.favoriteIds.indexOf(id);
      if (index !== -1) {
        state.favoriteIds.splice(index, 1);
      }
      // 儲存到 localStorage
      localStorage.setItem(
        "favoriteAccommodations",
        JSON.stringify(state.favoriteIds)
      );
    },

    TOGGLE_MAP_VIEW(state) {
      state.mapView = !state.mapView;
    },

    SET_MAP_CENTER(state, center) {
      state.mapCenter = center;
    },

    // 更新評論相關 mutations
    ADD_COMMENT(state, { propertyId, comment }) {
      if (!state.comments[propertyId]) {
        state.comments[propertyId] = [];
      }
      state.comments[propertyId].unshift(comment);

      // 可保留 localStorage 作為緩存，或完全依賴資料庫
      localStorage.setItem("propertyComments", JSON.stringify(state.comments));
    },

    LIKE_COMMENT(state, { propertyId, commentId }) {
      const comment = state.comments[propertyId]?.find(
        (c) => c.id === commentId
      );
      if (comment) {
        comment.likes += 1;
        localStorage.setItem(
          "propertyComments",
          JSON.stringify(state.comments)
        );
      }
    },

    SET_PROPERTY_COMMENTS(state, { propertyId, comments }) {
      // 設置特定房源的評論
      state.comments[propertyId] = comments;
    },

    SET_ALL_COMMENTS(state, comments) {
      // 替換所有評論數據
      state.comments = comments;
    }
  },

  actions: {
    // 初始化應用程式
    async initializeApp({ commit, dispatch }) {
      try {
        // 嘗試從 localStorage 載入收藏
        const savedFavorites = localStorage.getItem("favoriteAccommodations");
        if (savedFavorites) {
          commit("SET_FAVORITE_IDS", JSON.parse(savedFavorites));
        }

        // 嘗試從 localStorage 載入房源資料
        const savedAccommodations = localStorage.getItem("accommodations");
        if (savedAccommodations) {
          const parsedData = JSON.parse(savedAccommodations);
          commit("SET_ACCOMMODATIONS", parsedData);
          commit("SET_LOADING", false);

          // 如果有本地資料，先套用篩選和排序
          dispatch("applyFiltersAndSort");

          // 標記為已初始化
          commit("SET_DATA_INITIALIZED", true);
        }

        // 檢查是否需要更新資料（如果資料太舊或不存在）
        const lastUpdate = localStorage.getItem("accommodationsLastUpdated");
        const now = new Date().getTime();
        const dataAge = lastUpdate ? now - parseInt(lastUpdate) : Infinity;

        // 如果資料不存在或太舊（超過1小時），則從API獲取
        if (!savedAccommodations || dataAge > 3600000) {
          console.log("Data is stale or missing, fetching from API...");
          await dispatch("fetchAccommodations");
        }

        // 檢查用戶登入狀態
        const userFromLocal = localStorage.getItem("user");
        const userFromSession = sessionStorage.getItem("user");

        if (userFromLocal || userFromSession) {
          const userData = JSON.parse(userFromLocal || userFromSession);
          commit("SET_USER", userData);
          commit("SET_AUTHENTICATED", true);

          // 如果用戶已登入，嘗試同步收藏
          dispatch("syncFavorites");
        }
      } catch (error) {
        console.error("Failed to initialize app:", error);

        // 如果初始化失敗但有本地資料，仍標記為已初始化
        if (localStorage.getItem("accommodations")) {
          commit("SET_DATA_INITIALIZED", true);
        }
      }
    },

    // 獲取房源資料
    async fetchAccommodations({ commit, dispatch, state }) {
      try {
        commit("SET_LOADING", true);

        // 從 API 獲取房源資料
        const response = await apiService.accommodations.getAccommodations();

        if (
          response &&
          response.success === true &&
          Array.isArray(response.items)
        ) {
          // 將 API 返回的資料格式轉換為前端使用的格式
          const formattedData = response.items.map((item) => {
            return {
              編碼: item.accommodation_id,
              標題: item.title,
              房租: String(item.rent_price),
              地址: item.address,
              聯絡資訊: item.contact_info || "請聯絡房東",
              屋內設備: item.amenities
                ? item.amenities
                  .filter(
                    (a) =>
                      a.category === "appliance" || a.category === "furniture"
                  )
                  .map((a) => a.name)
                : [],
              公共設施: item.amenities
                ? item.amenities
                  .filter(
                    (a) => a.category === "utility" || a.category === "other"
                  )
                  .map((a) => a.name)
                : [],
              屋況說明: item.description
                ? item.description.split(/[,，、。；;]/).filter((s) => s.trim())
                : [],
              出租房數: {
                套房:
                  item.studio_count > 0
                    ? {
                      總數: item.studio_count,
                      空房: item.studio_available,
                      坪數: item.studio_area
                        ? `約${item.studio_area}坪`
                        : item.area
                          ? `約${item.area}坪`
                          : "未提供",
                    }
                    : null,
                雅房:
                  item.single_count > 0
                    ? {
                      總數: item.single_count,
                      空房: item.single_available,
                      坪數: item.single_area
                        ? `約${item.single_area}坪`
                        : item.area
                          ? `約${item.area}坪`
                          : "未提供",
                    }
                    : null,
              },
              其他費用: item.deposit ? `押金：${item.deposit}元` : "無額外費用",
              房屋照片: item.images ? item.images.map((img) => img.url) : [],
              建立時間: item.created_at,
              更新時間: item.updated_at,
              latitude: item.latitude,
              longitude: item.longitude,
              distance_to_university: item.distance_to_university,
            };
          });

          commit("SET_ACCOMMODATIONS", formattedData);

          localStorage.setItem("accommodations", JSON.stringify(formattedData));
          localStorage.setItem('accommodationsLastUpdated', new Date().getTime().toString());

          commit('SET_DATA_INITIALIZED', true);

          dispatch('applyFiltersAndSort');
        } else {
          console.error(
            "Failed to fetch accommodations:",
            response?.message || "Unknown error"
          );
          throw new Error("Failed to fetch accommodations");
        }

        // 從 localStorage 載入收藏
        const savedFavorites = localStorage.getItem("favoriteAccommodations");
        const favoriteIds = savedFavorites ? JSON.parse(savedFavorites) : [];
        commit("SET_FAVORITE_IDS", favoriteIds);

        // 應用初始篩選和排序
        dispatch("applyFiltersAndSort");
      } catch (error) {
        console.error("Failed to fetch accommodations:", error);

        // 錯誤處理：嘗試從本地 JSON 檔案獲取
        const fallbackData = await import("@/data.json").catch((err) => {
          console.error("Failed to load fallback data:", err);
          return { default: [] };
        });

        if (state.accommodations.length > 0) {
          commit('SET_DATA_INITIALIZED', true);
        }

        commit("SET_ACCOMMODATIONS", fallbackData.default || []);

        // 應用初始篩選和排序
        dispatch("applyFiltersAndSort");
      } finally {
        commit("SET_LOADING", false);
      }
    },

    // 獲取收藏房源
    async fetchFavorites({ commit }) {
      try {
        const response =
          await apiService.accommodations.favorites.getFavorites();

        if (response) {
          // 提取 accommodation_id，設置到 favoriteIds
          const favoriteIds = response.map((item) => item.id);
          commit("SET_FAVORITE_IDS", favoriteIds);

          // 更新 localStorage
          localStorage.setItem(
            "favoriteAccommodations",
            JSON.stringify(favoriteIds)
          );
        }
      } catch (error) {
        console.error("Failed to fetch favorites:", error);
        // 如果 API 請求失敗，可以保留本地的收藏資料
      }
    },

    // 切換收藏狀態
    async toggleFavoriteWithApi({ commit }, id) {
      try {
        const response =
          await apiService.accommodations.favorites.toggleFavorite(id);

        if (response && response.success) {
          commit("TOGGLE_FAVORITE", id);
          return true;
        } else {
          throw new Error("API failed to toggle favorite");
        }
      } catch (error) {
        console.error("Failed to toggle favorite:", error);

        commit("TOGGLE_FAVORITE", id);

        console.warn("Changes are saved locally only");
        return false;
      }
    },

    // 從收藏中移除單個項目
    async removeFavorite({ commit }, id) {
      try {
        // 嘗試使用 API 移除收藏
        const response =
          await apiService.accommodations.favorites.removeFavorite(id);

        if (response && response.success) {
          // API 成功，更新本地狀態
          commit("REMOVE_FAVORITE", id);
          return true;
        } else {
          throw new Error("API request failed");
        }
      } catch (error) {
        console.error("Failed to remove favorite with API:", error);

        // API 失敗，僅在本地移除收藏
        commit("REMOVE_FAVORITE", id);

        // 顯示提示
        console.warn("Changes are saved locally only");
        return false;
      }
    },

    // 同步收藏列表與伺服器
    async syncFavorites({ commit, state }) {
      // 如果用戶已登入，則嘗試與伺服器同步收藏
      if (state.isAuthenticated) {
        try {
          const response =
            await apiService.accommodations.favorites.getFavorites();

          // 從回應中提取房源 ID
          const serverFavoriteIds = response.map((item) => item.id);

          // 本地收藏 ID
          const localFavoriteIds = state.favoriteIds;

          if (JSON.stringify(serverFavoriteIds.sort()) === JSON.stringify(localFavoriteIds.sort())) {
            console.log("本地收藏與伺服器一致，無需同步");
            return;
          }

          // 找出需要添加到伺服器的本地收藏
          const toAdd = localFavoriteIds.filter(
            (id) => !serverFavoriteIds.includes(id)
          );

          // 找出需要從本地移除的伺服器收藏 (已在伺服器上移除)
          const toRemove = serverFavoriteIds.filter(
            (id) => !localFavoriteIds.includes(id)
          );

          // 同步添加
          for (const id of toAdd) {
            await apiService.accommodations.favorites.toggleFavorite(id);
          }

          // 同步移除
          for (const id of toRemove) {
            await apiService.accommodations.favorites.removeFavorite(id);
          }

          // 更新本地狀態為伺服器狀態
          commit("SET_FAVORITE_IDS", serverFavoriteIds);

          // 更新 localStorage
          localStorage.setItem(
            "favoriteAccommodations",
            JSON.stringify(serverFavoriteIds)
          );

          console.log("Favorites synced with server");
        } catch (error) {
          console.error("Failed to sync favorites with server:", error);
        }
      }
    },

    // 應用篩選和排序
    async applyFiltersAndSort({ commit, state }) {
      let filtered = [...state.accommodations];

      // 套用搜尋
      if (state.searchQuery) {
        const query = state.searchQuery.toLowerCase();
        filtered = filtered.filter(
          (property) =>
            (property.標題 && property.標題.toLowerCase().includes(query)) ||
            (property.地址 && property.地址.toLowerCase().includes(query)) ||
            (property.屋內設備 &&
              property.屋內設備.some((item) =>
                item.toLowerCase().includes(query)
              )) ||
            (property.公共設施 &&
              property.公共設施.some((item) =>
                item.toLowerCase().includes(query)
              ))
        );
      }

      // 套用價格過濾
      if (state.filters.minPrice) {
        filtered = filtered.filter((property) => {
          const price = extractMinPrice(property.房租 || "0");
          return price >= state.filters.minPrice;
        });
      }

      if (state.filters.maxPrice) {
        filtered = filtered.filter((property) => {
          const price = extractMaxPrice(property.房租 || "0");
          return price <= state.filters.maxPrice;
        });
      }

      // 套用房型過濾
      if (state.filters.types && state.filters.types.length > 0) {
        filtered = filtered.filter((property) => {
          if (!property.出租房數) return false;

          if (state.filters.types.includes("套房") && property.出租房數.套房) {
            return true;
          }
          if (state.filters.types.includes("雅房") && property.出租房數.雅房) {
            return true;
          }
          return false;
        });
      }

      // 套用設備與特色過濾
      if (state.filters.features && state.filters.features.length > 0) {
        filtered = filtered.filter((property) => {
          const allFeatures = [
            ...(property.屋內設備 || []),
            ...(property.公共設施 || []),
          ];
          return state.filters.features.every((feature) =>
            allFeatures.includes(feature)
          );
        });
      }

      // 套用排序
      switch (state.sortOption) {
        case "priceAsc":
          filtered.sort(
            (a, b) =>
              extractMinPrice(a.房租 || "0") - extractMinPrice(b.房租 || "0")
          );
          break;
        case "priceDesc":
          filtered.sort(
            (a, b) =>
              extractMinPrice(b.房租 || "0") - extractMinPrice(a.房租 || "0")
          );
          break;
        case "distanceAsc":
          // 由於沒有實際距離資料，這裡使用編碼作為排序標準，模擬接近程度
          filtered.sort((a, b) => (a.編碼 || 0) - (b.編碼 || 0));
          break;
        case "newest":
          // 假設編碼越大越新
          filtered.sort((a, b) => (b.編碼 || 0) - (a.編碼 || 0));
          break;
        default:
          break;
      }

      commit("SET_FILTERED_ACCOMMODATIONS", filtered);
    },

    // 設置路由並觸發動畫
    navigateTo({ commit }, route) {
      commit("SET_CURRENTROUTE", route);
    },

    // 從資料庫加載特定房源的評論
    async fetchPropertyComments({ commit }, propertyId) {
      try {
        // 這裡將來替換為實際的 API 調用
        // const response = await apiService.comments.getComments(propertyId);
        // if (response && response.success) {
        //   commit("SET_PROPERTY_COMMENTS", { 
        //     propertyId, 
        //     comments: response.comments 
        //   });
        // }

        // 臨時：從 localStorage 加載
        const savedComments = localStorage.getItem("propertyComments");
        if (savedComments) {
          const allComments = JSON.parse(savedComments);
          const propertyComments = allComments[propertyId] || [];
          commit("SET_PROPERTY_COMMENTS", {
            propertyId,
            comments: propertyComments
          });
        }
      } catch (error) {
        console.error(`無法獲取房源 ${propertyId} 的評論:`, error);
      }
    },

    // 從資料庫加載所有評論
    async fetchAllComments({ commit }) {
      try {
        // 這裡將來替換為實際的 API 調用
        // const response = await apiService.comments.getAllComments();
        // if (response && response.success) {
        //   commit("SET_ALL_COMMENTS", response.comments);
        // }

        // 臨時：從 localStorage 加載
        const savedComments = localStorage.getItem("propertyComments");
        if (savedComments) {
          commit("SET_ALL_COMMENTS", JSON.parse(savedComments));
        }
      } catch (error) {
        console.error("無法獲取所有評論:", error);
      }
    },

    // 添加評論 - 準備連接資料庫
    async addComment({ commit, state }, { propertyId, content, rating }) {
      try {
        const newComment = {
          id: Date.now(), // 臨時ID，資料庫應生成真實ID
          userId: state.user?.id || "guest",
          userName: state.user?.name || "訪客",
          content,
          rating,
          date: new Date().toISOString().split("T")[0],
          likes: 0,
        };

        // 這裡將來替換為實際的 API 調用
        // const response = await apiService.comments.addComment(propertyId, {
        //   content,
        //   rating,
        //   userId: state.user?.id
        // });
        // 
        // if (response && response.success) {
        //   // 使用後端返回的評論數據
        //   commit("ADD_COMMENT", { propertyId, comment: response.comment });
        //   return true;
        // }

        // 臨時：直接添加到本地狀態
        commit("ADD_COMMENT", { propertyId, comment: newComment });
        return true;
      } catch (error) {
        console.error("添加評論失敗:", error);
        return false;
      }
    },

    // 點贊評論 - 準備連接資料庫
    async likeComment({ commit }, { propertyId, commentId }) {
      try {
        // 這裡將來替換為實際的 API 調用
        // const response = await apiService.comments.likeComment(propertyId, commentId);
        // if (response && response.success) {
        //   commit("LIKE_COMMENT", { propertyId, commentId });
        //   return true;
        // }

        // 臨時：直接更新本地狀態
        commit("LIKE_COMMENT", { propertyId, commentId });
        return true;
      } catch (error) {
        console.error("點贊評論失敗:", error);
        return false;
      }
    },
  },

  getters: {
    isLoggedIn: (state) => state.isAuthenticated,
    currentUser: (state) => state.user,
    allAccommodations: (state) => state.accommodations,
    filteredAccommodations: (state) => state.filteredAccommodations,
    selectedAccommodation: (state) => state.selectedAccommodation,
    favoriteIds: (state) => state.favoriteIds,
    favoriteProperties: (state) => {
      return state.accommodations.filter((property) =>
        state.favoriteIds.includes(property.編碼 || 0)
      );
    },
    getPropertyComments: (state) => (propertyId) => {
      return state.comments[propertyId] || [];
    },

    // 計算每個房源的平均評分
    getPropertyRating: (state) => (propertyId) => {
      const comments = state.comments[propertyId] || [];
      if (comments.length === 0) return 0;

      const sum = comments.reduce(
        (total, comment) => total + comment.rating,
        0
      );
      return (sum / comments.length).toFixed(1);
    },

    // 計算每個房源的評論數量
    getPropertyCommentCount: (state) => (propertyId) => {
      return (state.comments[propertyId] || []).length;
    },
  },
});

// 輔助函數
function extractMinPrice(priceString) {
  if (!priceString) return 0;

  try {
    const prices = priceString.match(/\d+/g);
    if (!prices || prices.length === 0) return 0;

    return Math.min(...prices.map((p) => parseInt(p)));
  } catch (error) {
    console.error("價格提取錯誤:", error);
    return 0;
  }
}

function extractMaxPrice(priceString) {
  if (!priceString) return 0;

  try {
    const prices = priceString.match(/\d+/g);
    if (!prices || prices.length === 0) return 0;

    return Math.max(...prices.map((p) => parseInt(p)));
  } catch (error) {
    console.error("價格提取錯誤:", error);
    return 0;
  }
}
