import { createStore } from 'vuex'

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
    
    // 篩選條件
    filters: {
      price: { min: 0, max: 30000 },
      distance: 5, // 預設 5km 內
      roomType: [],
      amenities: [],
      duration: []
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
    
    SET_SELECTED_ACCOMMODATION(state, accommodation) {
      state.selectedAccommodation = accommodation;
    },
    
    APPLY_FILTERS(state, filters) {
      state.filters = {...state.filters, ...filters};
      
      // 實現篩選邏輯
      state.filteredAccommodations = state.accommodations.filter(acc => {
        // 價格篩選
        if (acc.price < state.filters.price.min || acc.price > state.filters.price.max) {
          return false;
        }
        
        // 距離篩選
        if (acc.distance > state.filters.distance) {
          return false;
        }
        
        // 房型篩選
        if (state.filters.roomType.length && !state.filters.roomType.includes(acc.roomType)) {
          return false;
        }
        
        // 家電篩選
        if (state.filters.amenities.length) {
          const hasAllAmenities = state.filters.amenities.every(amenity => 
            acc.amenities.includes(amenity)
          );
          if (!hasAllAmenities) return false;
        }
        
        // 租期篩選
        if (state.filters.duration.length && !state.filters.duration.includes(acc.duration)) {
          return false;
        }
        
        return true;
      });
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
    async fetchAccommodations({ commit }) {
      try {
        // 這裡可以改為從 API 獲取資料
        const mockData = [
          {
            id: 1,
            title: '中大湖畔雙人套房',
            description: '近學校，環境優美，設備齊全',
            price: 8000,
            roomType: '套房',
            distance: 0.8, // km
            address: '桃園市中壢區中大路300號附近',
            amenities: ['冷氣', '洗衣機', '冰箱', 'Wi-Fi'],
            duration: '一年',
            photos: ['room1.jpg', 'room1-2.jpg'],
            location: { lat: 24.9678, lng: 121.1891 },
            rating: 4.5,
            reviews: []
          },
          // 更多模擬資料...
        ];
        
        commit('SET_ACCOMMODATIONS', mockData);
      } catch (error) {
        console.error('Failed to fetch accommodations:', error);
      }
    },
    
    // 設置路由並觸發動畫
    navigateTo({ commit }, route) {
      commit('SET_ROUTE', route);
    }
  },
  
  getters: {
    isLoggedIn: state => state.isAuthenticated,
    currentUser: state => state.user,
    allAccommodations: state => state.accommodations,
    filteredAccommodations: state => state.filteredAccommodations,
    selectedAccommodation: state => state.selectedAccommodation
  }
})