import { createStore } from 'vuex';
import accommodationData from '@/data.json';

export default createStore({
  state: {
    // 使用者資訊
    user: null,
    isAuthenticated: false,

    // 導航狀態
    navigationOpen: false,
    currentRoute: 'home',

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
    mapZoom: 15
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


