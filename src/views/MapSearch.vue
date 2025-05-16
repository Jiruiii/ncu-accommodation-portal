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
          <div class="chip active">全部</div>
          <div class="chip">5000以下</div>
          <div class="chip">5000-8000</div>
          <div class="chip">8000以上</div>
          <div class="chip">限學生</div>
          <div class="chip">可養寵物</div>
        </div>
      </div>
      
      <div class="results">
        <h3>搜尋結果 <span class="result-count">(12)</span></h3>
        <div class="result-list">
          <div 
            v-for="property in searchResults" 
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
      <div id="google-map" style="height: 100%; width: 100%"></div>
    </div>
  </div>
</template>

<script>
/* Add this at the top of your script section */


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
          image: "https://picsum.photos/id/1026/300/150",
          lat: 24.9683,
          lng: 121.1945
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
          image: "https://picsum.photos/id/1027/300/150",
          lat: 24.9685,
          lng: 121.1950
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
          image: "https://picsum.photos/id/1028/300/150",
          lat: 24.9687,
          lng: 121.1948
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
          image: "https://picsum.photos/id/1029/300/150",
          lat: 24.9689,
          lng: 121.1952
        }
      ],
      mapMarkers: [],
      map: null,
      markers: [],
      isMapLoaded: false,
      mapLoadError: false,
      selectedMarker: null,
      API_KEY: 'AIzaSyCqNQRo2JFh8XSiBN0pZzemAmUh3WR910s', // 替換成你的 API Key
      shouldShowBelow: false
    };
  },
  computed: {
    selectedPropertyDetails() {
      return this.searchResults.find(p => p.id === this.selectedProperty) || {};
    }
  },
  mounted() {
    this.initGoogleMaps();
  },
  methods: {
    selectProperty(id) {
      this.selectedProperty = id;
    },
    closeInfoWindow() {
      this.selectedProperty = null;
    },
    getInfoWindowPosition() {
      const marker = this.mapMarkers.find(m => m.id === this.selectedProperty);
      if (!marker) return {};
      
      return {
        left: marker.x + "%",
        top: (marker.y - 15) + "%"
      };
    },
    initGoogleMaps() {
      // 添加錯誤處理
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${this.API_KEY}&callback=initMap`;
      script.async = true;
      script.defer = true;
      
      // 添加載入錯誤處理
      script.onerror = () => {
        console.error('Google Maps 載入失敗');
        this.mapLoadError = true;
        this.createFallbackMap();
      };

      window.initMap = () => {
        try {
          this.createMap();
          this.isMapLoaded = true;
        } catch (error) {
          console.error('地圖初始化失敗:', error);
          this.mapLoadError = true;
          this.createFallbackMap();
        }
      };

      document.head.appendChild(script);
    },
    createMap() {
      const ncuLocation = { lat: 24.9683, lng: 121.1945 };
      
      // Add type check for Google Maps
      if (window.google && window.google.maps) {
        this.map = new window.google.maps.Map(document.getElementById('google-map'), {
          center: ncuLocation,
          zoom: 15,
          styles: [],
          mapTypeControl: false,
          fullscreenControl: false,
        });

        this.searchResults.forEach(property => {
          const marker = new window.google.maps.Marker({
            position: { lat: property.lat, lng: property.lng },
            map: this.map,
            title: property.title,
          });

          marker.addListener('click', () => {
            this.selectProperty(property.id);
          });

          this.markers.push(marker);
        });
      } else {
        this.createFallbackMap();
      }
    },
    createFallbackMap() {
      const mapContainer = document.getElementById('google-map');
      if (!mapContainer) return;

      mapContainer.innerHTML = `
        <div style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; background: #f5f5f5;">
          <img src="https://picsum.photos/800/400" alt="Map placeholder" style="max-width: 100%; height: auto; margin-bottom: 20px;"/>
          <p style="color: #666; text-align: center; padding: 20px;">
            地圖暫時無法載入<br>
            請稍後再試
          </p>
        </div>
      `;
      this.mapLoadError = true;
    },
    selectMarker(markerId) {
      this.selectedMarker = this.selectedMarker === markerId ? null : markerId;
    },
    showMarkerInfo(markerId, event) {
      this.selectedMarker = markerId;
      const marker = event.target;
      const markerRect = marker.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      this.shouldShowBelow = markerRect.top < (windowHeight / 2);
    },
    hideMarkerInfo() {
      this.selectedMarker = null;
    },
    toggleFavorite(markerId) {
      if (!this.favorites) this.favorites = [];
      const index = this.favorites.indexOf(markerId);
      if (index === -1) {
        this.favorites.push(markerId);
      } else {
        this.favorites.splice(index, 1);
      }
    },
    isFavorite(markerId) {
      return this.favorites && this.favorites.includes(markerId);
    },
    viewDetails(markerId) {
      console.log(`Viewing details for marker ID: ${markerId}`);
    }
  },
  beforeUnmount() {
    if (this.map) {
      this.markers.forEach(marker => marker.setMap(null));
      this.markers = [];
      this.map = null;
    }
  },
  watch: {
    selectedProperty(newValue) {
      if (this.mapLoadError || !this.map) return;

      this.markers.forEach(marker => {
        const property = this.searchResults.find(p => 
          p.lat === marker.getPosition().lat() && 
          p.lng === marker.getPosition().lng()
        );
        if (property && property.id === newValue) {
          marker.setAnimation(window.google.maps.Animation.BOUNCE);
          this.map.panTo(marker.getPosition());
        } else {
          marker.setAnimation(null);
        }
      });
    }
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
}

#google-map {
  width: 100%;
  height: 100%;
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
  z-index: 1;
}

.marker-price {
  background: #6B5FF0; /* 更新為紫色系 */
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-weight: bold;
  font-size: 0.9rem;
  white-space: nowrap;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.map-marker.active {
  z-index: 100;
}

.map-marker.active .marker-price {
  background: #9747FF; /* 更亮的紫色 */
}

.info-window {
  position: absolute;
  width: 400px; /* 增加寬度 */
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  transform: translate(-50%, -120%);
  z-index: 101;
  overflow: hidden;
}

.info-window.show-below {
  transform: translate(-50%, 20px);
}

.info-header {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 2;
}

.title-link {
  color: #333;
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  cursor: pointer;
  text-decoration: none;
}

.title-link:hover {
  color: #6B5FF0;
}

.heart-btn {
  background: white;
  border: none;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  transition: transform 0.2s;
}

.heart-btn:hover {
  transform: scale(1.1);
}

.info-body {
  display: flex;
  align-items: stretch;
}

.image-container {
  width: 150px; /* 固定寬度 */
  height: 150px; /* 固定高度，保持正方形 */
  flex-shrink: 0;
}

.info-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-details {
  flex: 1;
  padding: 15px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-price {
  color: #6B5FF0;
  font-weight: bold;
  font-size: 18px;
}

.info-amenities {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  color: #666;
  font-size: 14px;
}

.close-btn {
  display: none;
}

.info-window::before {
  content: '';
  position: absolute;
  border: 8px solid transparent;
}

.info-window:not(.show-below)::before {
  bottom: -16px;
  left: 50%;
  transform: translateX(-50%);
  border-top-color: white;
}

.info-window.show-below::before {
  top: -16px;
  left: 50%;
  transform: translateX(-50%);
  border-bottom-color: white;
}
</style>