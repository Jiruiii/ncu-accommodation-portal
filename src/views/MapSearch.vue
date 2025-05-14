<template>
    <div class="map-search">
      <div class="sidebar">
        <div class="search-container">
          <input type="text" placeholder="搜尋位置..." v-model="searchText" class="search-input" />
          <button class="search-btn">搜尋</button>
        </div>
        
        <div class="filters">
          <h3>快速篩選</h3>
          <div class="filter-chips">
            <div class="chip" @click="filterOff('全部')" :class="{active : activeChip === '全部'}">全部</div>
            <div class="chip" @click="filterChips(0, 5000, '5000以下')" :class="{active : activeChip === '5000以下'}">5000以下</div>
            <div class="chip" @click="filterChips(5000, 8000, '5000-8000')" :class="{active : activeChip === '5000-8000'}">5000-8000</div>
            <div class="chip" @click="filterChips(8000, Infinity, '8000以上')" :class="{active : activeChip === '8000以上'}">8000以上</div>
            <div class="chip" @click="filterChips_boolean('限學生')" :class="{active : activeChip === '限學生'}">限學生</div>
            <div class="chip" @click="filterChips_boolean('可養寵物')" :class="{active : activeChip === '可養寵物'}">可養寵物</div>
          </div>
        </div>
        
        <div class="results">
          <h3>搜尋結果 <span class="result-count">(12)</span></h3>
          <div class="result-list">
            <div 
              v-for="property in rightIds" 
              :key="property.id" 
              class="result-item"
              :class="{ active: selectedProperty === property.id }"
              @click="selectProperty(property.id)"
            >
              <img :src="property.image" alt="房屋照片" class="property-thumbnail" />
              <div class="item-details">
                <h4>{{ property.title }}</h4>
                <div class="price">NT$ {{ property.price.toLocaleString() }}/月</div>
                <div class="location">
                  <i class="location-icon">📍</i> {{ property.location }}
                </div>
                <div class="amenities">
                  <span>{{ property.type }}</span>
                  <span>{{ property.size }}坪</span>
                  <span v-if="property.bedrooms > 0">{{ property.bedrooms }}房</span>
                  <span v-if="property.bathrooms > 0">{{ property.bathrooms }}衛</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="map-container">
        <!-- 這裡會放置實際的地圖，採用顯示範例圖片 -->
        <div class="map-placeholder">
          <!--
          <img src="https://developers.google.com/static/maps/images/landing/hero_maps_static_api.png" alt="地圖示例" />
          -->

          <div id="map" style="height: 100%; width: 100%"></div>
          
          <!-- 地圖標記點示例 -->
          <div 
            v-for="marker in mapMarkers.value" 
            :key="marker.id" 
            class="map-marker"
            :class="{ active: selectedProperty === marker.id }"
            :style="{ left: marker.x + '%', top: marker.y + '%' }"
            @click="selectProperty(marker.id)"
          >
            <div class="marker-price">{{ marker.price }}</div>
          </div>
          
          <!-- 選定項目資訊視窗 -->
          <div class="info-window" v-if="selectedProperty" :style="getInfoWindowPosition()">
            <div class="info-content">
              <div class="info-header">
                <h4>{{ selectedPropertyDetails.title }}</h4>
                <button class="close-btn" @click="closeInfoWindow">×</button>
              </div>
              <img :src="selectedPropertyDetails.image" alt="Property" class="info-image" />
              <div class="info-details">
                <div class="info-price">NT$ {{ selectedPropertyDetails.price.toLocaleString() }}/月</div>
                <div class="info-location">{{ selectedPropertyDetails.location }}</div>
                <div class="info-amenities">
                  <span>{{ selectedPropertyDetails.type }}</span> · 
                  <span>{{ selectedPropertyDetails.size }}坪</span>
                  <span v-if="selectedPropertyDetails.bedrooms > 0"> · {{ selectedPropertyDetails.bedrooms }}房</span>
                  <span v-if="selectedPropertyDetails.bathrooms > 0"> · {{ selectedPropertyDetails.bathrooms }}衛</span>
                </div>
                <div class="info-actions">
                  <button class="view-btn">查看詳情</button>
                  <button class="favorite-btn">❤️ 收藏</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="map-controls">
          <button class="control-btn zoom-in">+</button>
          <button class="control-btn zoom-out">-</button>
          <button class="control-btn my-location">📍</button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted } from "vue";
  import L from "leaflet";

  export default {
    name: "MapSearch",
    data() {
      return {
        searchText: "",
        selectedProperty: null,
        searchResults: [
          {
            id: 1,
            title: "中央大學附近精美套房",
            location: "中壢區中大路300號附近",
            price: 7500,
            type: "套房",
            bedrooms: 1,
            bathrooms: 1,
            size: 8,
            student: true,
            pet: false,
            image: "https://picsum.photos/id/1026/300/150"
          },
          {
            id: 2,
            title: "近中壢夜市雅房",
            location: "中壢區五權里",
            price: 4800,
            type: "雅房",
            bedrooms: 0,
            bathrooms: 1,
            size: 5,
            student: true,
            pet: false,
            image: "https://picsum.photos/id/1027/300/150"
          },
          {
            id: 3,
            title: "中央大學旁整層出租",
            location: "中壢區中大路350號附近",
            price: 15000,
            type: "整層住家",
            bedrooms: 3,
            bathrooms: 2,
            size: 25,
            student: false,
            pet: true,
            image: "https://picsum.photos/id/1028/300/150"
          },
          {
            id: 4,
            title: "全新裝潢獨立套房",
            location: "中壢區五權二街",
            price: 8800,
            type: "獨立套房",
            bedrooms: 1,
            bathrooms: 1,
            size: 12,
            student: true,
            pet: false,
            image: "https://picsum.photos/id/1029/300/150"
          }
        ],
        rightIds: [],
        activeChip: '全部',
      };
    },
    setup() {
      const convertToXY = (lat, lng) => {
        return {
          x: ((lng - 121.18) / (121.22 - 121.18)) * 100,
          y: ((24.96 - lat) / (24.97 - 24.96)) * 100,
        };
      };

      const mapMarkers = ref([
        { id: 1, lat: 24.96798, lng: 121.19982, price: "7.5K", ...convertToXY(24.96798, 121.19982) },
        { id: 2, lat: 24.96046, lng: 121.21435, price: "4.8K", ...convertToXY(24.96046, 121.21435) },
        { id: 3, lat: 24.97034, lng: 121.18890, price: "15K", ...convertToXY(24.97034, 121.18890) },
        { id: 4, lat: 24.96585, lng: 121.18702, price: "8.8K", ...convertToXY(24.96585, 121.18702) },
      ]); 
      const selectedProperty = ref(null);
      const map = ref(null);
    
      const selectProperty = (id) => {
        selectedProperty.value = id;

        // 找到對應的標記
        const selectedMarker = mapMarkers.value.find(m => m.id === id);

        if (!selectedMarker) {
          console.error("selectedMarker not found for id:", id);
          return;
        }

        // 讓地圖平移到標記並彈出對話框
        if (map.value) {
          map.value.setView([selectedMarker.lat, selectedMarker.lng], 18);
          selectedMarker.leafletMarker.openPopup();
        }
      };

      const closeInfoWindow = () => {
        selectedProperty.value = null;
      };

      const getInfoWindowPosition = () => {
        const marker = mapMarkers.value.find(m => m.id === selectedProperty.value);
        if (!marker) return {};
        return {
          left: marker.x + "%",
          top: (marker.y - 15) + "%"
        };
      };

      onMounted(() => {
        // 初始化 Leaflet 地圖
        map.value = L.map("map").setView([24.96847, 121.19518], 15);

        // 載入 OpenStreetMap 圖層
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution: "© OpenStreetMap contributors",
        }).addTo(map.value);

        // 自定義標記樣式
        const customIcon = L.icon({
          iconUrl: require("@/assets/icons/marker4.png"),
          iconSize: [32, 32],
        });

        // 加入標記
        mapMarkers.value.forEach((marker) => {
          const leafletMarker = L.marker([marker.lat, marker.lng], { icon: customIcon })
            .addTo(map.value)
            .bindPopup(`<div style="color: #007bff; font-size: 16px; font-weight: bold; text-align: center">${marker.price}</div>`);

          marker.leafletMarker = leafletMarker;
        });
      });

      return {
        mapMarkers,
        selectedProperty,
        selectProperty,
        closeInfoWindow,
        getInfoWindowPosition,
      };
    },
    mounted (){
      this.rightIds = this.searchResults;
    },
    computed: {
      selectedPropertyDetails() {
        return this.searchResults.find(p => p.id === this.selectedProperty) || {};
      }
    },
    methods: {
      closeInfoWindow() {
        this.selectedProperty = null;
      },
      getInfoWindowPosition() {
        if (!this.selectedProperty || !this.mapMarkers?.value) return {};

        const marker = this.mapMarkers.value.find(m => m.id === this.selectedProperty);
        if (!marker) return {};
        
        return {
          left: marker.x + "%",
          top: (marker.y - 15) + "%"
        };
      },
      filterOff(label){
        this.activeChip = label;
        this.rightIds = this.searchResults;
      },
      filterChips(min, max, label) {
        this.activeChip = label;
        const rightProperties = this.searchResults.filter(p => p.price < max && p.price > min);
        this.rightIds = rightProperties;
      },
      filterChips_boolean(type){
        if (type === "限學生"){
          this.activeChip = type;
          const rightProperties = this.searchResults.filter(p => p.student === true);
          this.rightIds = rightProperties;
        }else{
          this.activeChip = type;
          const rightProperties = this.searchResults.filter(p => p.pet === true);
          this.rightIds = rightProperties;
        }
      },
      
    }
  };
  </script>
  
  <style scoped>
  .map-search {
    display: flex;
    height: 100vh;
    overflow: hidden;
  }
  
  .sidebar {
    width: 350px;
    background-color: #fff;
    border-right: 1px solid #e0e0e0;
    display: flex;
    flex-direction: column;
    z-index: 10;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.05);
  }
  
  .search-container {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
  }
  
  .search-input {
    flex: 1;
    padding: 10px 15px;
    border: 1px solid #ddd;
    border-radius: 8px 0 0 8px;
    font-size: 1rem;
  }
  
  .search-btn {
    padding: 10px 15px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 0 8px 8px 0;
    cursor: pointer;
  }
  
  .filters {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
  }
  
  .filters h3 {
    font-size: 1rem;
    margin: 0 0 10px;
    color: #555;
  }
  
  .filter-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .chip {
    padding: 6px 12px;
    background: #f5f7fa;
    border-radius: 20px;
    font-size: 0.85rem;
    cursor: pointer;
    transition: background 0.2s, color 0.2s;
  }
  
  .chip.active {
    background: #007bff;
    color: white;
  }
  
  .chip:hover:not(.active) {
    background: #e5e9f0;
  }
  
  .results {
    padding: 15px 20px;
    flex: 1;
    overflow-y: auto;
  }
  
  .results h3 {
    font-size: 1rem;
    margin: 0 0 15px;
    color: #555;
    display: flex;
    align-items: center;
  }
  
  .result-count {
    color: #888;
    margin-left: 5px;
    font-weight: normal;
  }
  
  .result-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .result-item {
    display: flex;
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
  }
  
  .result-item:hover,
  .result-item.active {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .result-item.active {
    border: 2px solid #007bff;
  }
  
  .property-thumbnail {
    width: 100px;
    height: 100px;
    object-fit: cover;
  }
  
  .item-details {
    padding: 10px;
    flex: 1;
  }
  
  .item-details h4 {
    margin: 0 0 5px;
    font-size: 0.95rem;
    color: #333;
  }
  
  .price {
    font-weight: bold;
    color: #007bff;
    margin-bottom: 5px;
    font-size: 0.9rem;
  }
  
  .location {
    color: #666;
    font-size: 0.8rem;
    margin-bottom: 5px;
    display: flex;
    align-items: center;
  }
  
  .location-icon {
    margin-right: 3px;
    font-size: 0.8rem;
  }
  
  .amenities {
    display: flex;
    gap: 8px;
    font-size: 0.75rem;
    color: #777;
  }
  
  .map-container {
    flex: 1;
    position: relative;
    background: #f5f5f5;
  }
  
  .map-placeholder {
    width: 100%;
    height: 100%;
    position: relative;
  }
  
  .map-placeholder img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .map-marker {
    position: absolute;
    transform: translate(-50%, -100%);
    cursor: pointer;
  }

  .marker-price {
    background: #007bff;
    color: white;
    padding: 5px 8px;
    border-radius: 4px;
    font-weight: bold;
    font-size: 0.75rem;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  }
  
  .marker-price::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 50%;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #007bff;
  }
  
  .map-marker.active .marker-price {
    background: #ff4757;
    transform: scale(1.1);
  }
  
  .map-marker.active .marker-price::after {
    border-top-color: #ff4757;
  }
  
  .info-window {
    position: absolute;
    width: 300px;
    transform: translate(-50%, -100%);
    z-index: 1000;
  }
  
  .info-content {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
  }
  
  .info-header {
    padding: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #eee;
  }
  
  .info-header h4 {
    margin: 0;
    font-size: 1rem;
    color: #333;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: #777;
  }
  
  .info-image {
    width: 100%;
    height: 150px;
    object-fit: cover;
  }
  
  .info-details {
    padding: 15px;
  }
  
  .info-price {
    font-weight: bold;
    font-size: 1.1rem;
    color: #007bff;
    margin-bottom: 8px;
  }
  
  .info-location {
    color: #555;
    font-size: 0.9rem;
    margin-bottom: 8px;
  }
  
  .info-amenities {
    color: #777;
    font-size: 0.85rem;
    margin-bottom: 15px;
  }
  
  .info-actions {
    display: flex;
    gap: 10px;
  }
  
  .view-btn {
    flex: 1;
    padding: 8px 0;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .favorite-btn {
    padding: 8px 15px;
    background: #f1f1f1;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .map-controls {
    position: absolute;
    bottom: 20px;
    right: 20px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .control-btn {
    width: 40px;
    height: 40px;
    background: white;
    border: none;
    border-radius: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .control-btn:hover {
    background: #f8f8f8;
  }
  </style>