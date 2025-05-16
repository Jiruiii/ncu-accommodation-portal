import { createStore } from 'vuex';
import accommodationData from '@/data.json';

export default createStore({
  state: {
    // 使用者資訊
    user: null,
    isAuthenticated: false,

    // 導航狀態
    navigationOpen: false,
    currentRoute: localStorage.getItem('currentRoute') || 'home',
    isNavOpen: false,

    // 房源資料
    accommodations: [],
    filteredAccommodations: [],
    selectedAccommodation: null,
    favoriteIds: [],

    // 搜尋和篩選條件
    searchQuery: "",
    sortOption: "newest",
    filters: {
      minPrice: null,
      maxPrice: null,
      types: [],
      features: []
    },

    // 地圖狀態
    mapView: false,
    mapCenter: { lat: 24.9680, lng: 121.1944 }, // 中央大學座標
    mapZoom: 15,

    // 新增：房源評論資料
    comments: {
      // 預設假資料，使用房源編碼作為 key
      "1": [
        {
          id: 1,
          userId: "user123",
          userName: "張小明",
          content: "房東人很好，環境也很乾淨！浴室有暖氣，住起來很舒適。",
          rating: 5,
          date: "2025-05-10",
          likes: 3
        },
        {
          id: 2,
          userId: "user456",
          userName: "林小華",
          content: "地點很方便，走路到中央大學只要10分鐘。附近有超商也很方便。",
          rating: 4,
          date: "2025-05-08",
          likes: 1
        }
      ],
      "2": [
        {
          id: 3,
          userId: "user789",
          userName: "王小美",
          content: "冷氣很涼，房間隔音還不錯。唯一缺點是洗衣機共用，要排隊。",
          rating: 4,
          date: "2025-05-05",
          likes: 2
        }
      ],
      "3": [
        {
          id: 4,
          userId: "user321",
          userName: "黃小傑",
          content: "價格合理，房間採光佳。房東定期打掃公共區域，環境很乾淨。",
          rating: 5,
          date: "2025-05-12",
          likes: 4
        },
        {
          id: 5,
          userId: "user654",
          userName: "陳小玉",
          content: "整體不錯，但廁所有點小。夏天熱水不太穩定，其他都還可以。",
          rating: 3,
          date: "2025-05-03",
          likes: 0
        }
      ],
      "5": [
        {
          id: 6,
          userId: "user111",
          userName: "李大明",
          content: "停車方便，房間明亮。不過走廊燈晚上有點太亮，需要厚窗簾。",
          rating: 4,
          date: "2025-05-01",
          likes: 2
        }
      ],
      "8": [
        {
          id: 7,
          userId: "user222",
          userName: "吳小芳",
          content: "網路很快，管理員人很親切。缺點是附近施工，早上有點吵。",
          rating: 3,
          date: "2025-04-28",
          likes: 1
        }
      ]
    }
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
      localStorage.setItem('currentRoute', route);
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
      localStorage.setItem('favoriteAccommodations', JSON.stringify(state.favoriteIds));
    },

    TOGGLE_MAP_VIEW(state) {
      state.mapView = !state.mapView;
    },

    SET_MAP_CENTER(state, center) {
      state.mapCenter = center;
    },

    // 新增：評論相關 mutations
    ADD_COMMENT(state, { propertyId, comment }) {
      if (!state.comments[propertyId]) {
        state.comments[propertyId] = [];
      }
      state.comments[propertyId].unshift(comment);
      
      // 更新 localStorage
      localStorage.setItem('propertyComments', JSON.stringify(state.comments));
    },
    
    LIKE_COMMENT(state, { propertyId, commentId }) {
      const comment = state.comments[propertyId]?.find(c => c.id === commentId);
      if (comment) {
        comment.likes += 1;
        
        // 更新 localStorage
        localStorage.setItem('propertyComments', JSON.stringify(state.comments));
      }
    },
    
    LOAD_COMMENTS(state, comments) {
      if (comments) {
        state.comments = comments;
      }
    }
  },

  actions: {
    // 獲取房源資料
    async fetchAccommodations({ commit, dispatch }) {
      try {
        // 篩選有效資料
        const validAccommodations = accommodationData.filter(property =>
          property &&
          property.編碼 &&
          property.標題 &&
          property.房租
        );

        commit('SET_ACCOMMODATIONS', validAccommodations);

        // 從 localStorage 載入收藏
        const savedFavorites = localStorage.getItem('favoriteAccommodations');
        const favoriteIds = savedFavorites ? JSON.parse(savedFavorites) : [];
        commit('SET_FAVORITE_IDS', favoriteIds);

        // 應用初始篩選和排序
        dispatch('applyFiltersAndSort');
      } catch (error) {
        console.error('Failed to fetch accommodations:', error);
      }
    },

    // 應用篩選和排序
    applyFiltersAndSort({ commit, state }) {
      let filtered = [...state.accommodations];

      // 套用搜尋
      if (state.searchQuery) {
        const query = state.searchQuery.toLowerCase();
        filtered = filtered.filter(
          (property) =>
            (property.標題 && property.標題.toLowerCase().includes(query)) ||
            (property.地址 && property.地址.toLowerCase().includes(query)) ||
            (property.屋內設備 && property.屋內設備.some(item => item.toLowerCase().includes(query))) ||
            (property.公共設施 && property.公共設施.some(item => item.toLowerCase().includes(query)))
        );
      }

      // 套用價格過濾
      if (state.filters.minPrice) {
        filtered = filtered.filter((property) => {
          const price = extractMinPrice(property.房租 || '0');
          return price >= state.filters.minPrice;
        });
      }

      if (state.filters.maxPrice) {
        filtered = filtered.filter((property) => {
          const price = extractMaxPrice(property.房租 || '0');
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
              extractMinPrice(a.房租 || '0') - extractMinPrice(b.房租 || '0')
          );
          break;
        case "priceDesc":
          filtered.sort(
            (a, b) =>
              extractMinPrice(b.房租 || '0') - extractMinPrice(a.房租 || '0')
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

      commit('SET_FILTERED_ACCOMMODATIONS', filtered);

      
    },

    // 設置路由並觸發動畫
    navigateTo({ commit }, route) {
      commit('SET_CURRENTROUTE', route);
    },

    addComment({ commit, state }, { propertyId, content, rating }) {
      // 產生新評論
      const newComment = {
        id: Date.now(),
        userId: state.user?.id || "guest",
        userName: state.user?.name || "訪客",
        content,
        rating,
        date: new Date().toISOString().split('T')[0],
        likes: 0
      };
      
      // 提交 mutation
      commit('ADD_COMMENT', { propertyId, comment: newComment });
    },
    
    likeComment({ commit }, { propertyId, commentId }) {
      commit('LIKE_COMMENT', { propertyId, commentId });
    },
    
    // 從 localStorage 加載評論
    loadComments({ commit }) {
      try {
        const savedComments = localStorage.getItem('propertyComments');
        if (savedComments) {
          commit('LOAD_COMMENTS', JSON.parse(savedComments));
        }
      } catch (error) {
        console.error('無法載入評論:', error);
      }
    },
    
    // 初始化資料時同時加載評論
    // async fetchAccommodations({ commit, dispatch }) {
    //   try {
    //     // 原有的加載邏輯...
    //     const validAccommodations = accommodationData.filter(property =>
    //       property &&
    //       property.編碼 &&
    //       property.標題 &&
    //       property.房租
    //     );

    //     commit('SET_ACCOMMODATIONS', validAccommodations);

    //     const savedFavorites = localStorage.getItem('favoriteAccommodations');
    //     const favoriteIds = savedFavorites ? JSON.parse(savedFavorites) : [];
    //     commit('SET_FAVORITE_IDS', favoriteIds);
        
    //     // 新增：載入評論
    //     dispatch('loadComments');

    //     dispatch('applyFiltersAndSort');
    //   } catch (error) {
    //     console.error('Failed to fetch accommodations:', error);
    //   }
    // }
    
  },

  getters: {
    isLoggedIn: state => state.isAuthenticated,
    currentUser: state => state.user,
    allAccommodations: state => state.accommodations,
    filteredAccommodations: state => state.filteredAccommodations,
    selectedAccommodation: state => state.selectedAccommodation,
    favoriteIds: state => state.favoriteIds,
    favoriteProperties: (state) => {
      return state.accommodations.filter(property =>
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
      
      const sum = comments.reduce((total, comment) => total + comment.rating, 0);
      return (sum / comments.length).toFixed(1);
    },
    
    // 計算每個房源的評論數量
    getPropertyCommentCount: (state) => (propertyId) => {
      return (state.comments[propertyId] || []).length;
    }
  }
})

// 輔助函數
function extractMinPrice(priceString) {
  if (!priceString) return 0;

  try {
    const prices = priceString.match(/\d+/g);
    if (!prices || prices.length === 0) return 0;

    return Math.min(...prices.map(p => parseInt(p)));
  } catch (error) {
    console.error('價格提取錯誤:', error);
    return 0;
  }
}

function extractMaxPrice(priceString) {
  if (!priceString) return 0;

  try {
    const prices = priceString.match(/\d+/g);
    if (!prices || prices.length === 0) return 0;

    return Math.max(...prices.map(p => parseInt(p)));
  } catch (error) {
    console.error('價格提取錯誤:', error);
    return 0;
  }
}


