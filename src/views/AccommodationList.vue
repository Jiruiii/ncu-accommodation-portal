<template>
    <div class="accommodation-list">
      <div class="header">
        <h1>租屋列表</h1>
        <div class="search-filters">
          <div class="search-box">
            <i class="search-icon">🔍</i>
            <input type="text" placeholder="搜尋地址、特色..." v-model="searchQuery" />
          </div>
          <div class="filter-options">
            <button class="filter-btn" @click="showFilterModal = true">
              篩選 <i class="filter-icon">⚙️</i>
            </button>
            <div class="sort-dropdown">
              <select v-model="sortOption">
                <option value="priceAsc">價格 ↑</option>
                <option value="priceDesc">價格 ↓</option>
                <option value="distanceAsc">距離 ↑</option>
                <option value="newest">最新刊登</option>
              </select>
            </div>
          </div>
        </div>
      </div>
  
      <div class="property-list">
        <div v-for="(property, index) in filteredProperties" :key="index" class="property-card">
          <div class="property-image" :style="{ backgroundImage: `url(${property.image})` }">
            <div class="price-tag">NT$ {{ property.price.toLocaleString() }}/月</div>
            <button class="favorite-btn" @click="toggleFavorite(property.id)">
              <i :class="property.isFavorite ? 'heart-filled' : 'heart-outline'">❤️</i>
            </button>
          </div>
          <div class="property-info">
            <h3>{{ property.title }}</h3>
            <p class="location">
              <i class="location-icon">📍</i> {{ property.location }}
            </p>
            <div class="amenities">
              <span><i class="bed-icon">🛏️</i> {{ property.bedrooms }}房</span>
              <span><i class="bath-icon">🚿</i> {{ property.bathrooms }}衛</span>
              <span><i class="size-icon">📏</i> {{ property.size }}坪</span>
            </div>
            <div class="tags">
              <span v-for="(tag, i) in property.tags" :key="i" class="tag">{{ tag }}</span>
            </div>
          </div>
        </div>
      </div>
  
      <!-- 篩選器彈出視窗 -->
      <div class="filter-modal" v-if="showFilterModal">
        <div class="filter-content">
          <h2>篩選條件</h2>
          <div class="filter-section">
            <h3>價格範圍</h3>
            <div class="price-range">
              <input type="range" min="3000" max="30000" v-model="filters.minPrice" />
              <div class="price-inputs">
                <input type="number" v-model="filters.minPrice" /> ~ 
                <input type="number" v-model="filters.maxPrice" />
              </div>
            </div>
          </div>
          
          <div class="filter-section">
            <h3>房型</h3>
            <div class="checkbox-group">
              <label><input type="checkbox" v-model="filters.types" value="套房" /> 套房</label>
              <label><input type="checkbox" v-model="filters.types" value="雅房" /> 雅房</label>
              <label><input type="checkbox" v-model="filters.types" value="整層住家" /> 整層住家</label>
              <label><input type="checkbox" v-model="filters.types" value="獨立套房" /> 獨立套房</label>
            </div>
          </div>
          
          <div class="filter-section">
            <h3>特色</h3>
            <div class="checkbox-group">
              <label><input type="checkbox" v-model="filters.features" value="有陽台" /> 有陽台</label>
              <label><input type="checkbox" v-model="filters.features" value="近捷運" /> 近捷運</label>
              <label><input type="checkbox" v-model="filters.features" value="可養寵物" /> 可養寵物</label>
              <label><input type="checkbox" v-model="filters.features" value="有管理員" /> 有管理員</label>
              <label><input type="checkbox" v-model="filters.features" value="有電梯" /> 有電梯</label>
              <label><input type="checkbox" v-model="filters.features" value="近夜市" /> 近夜市</label>
            </div>
          </div>
          
          <div class="filter-actions">
            <button class="reset-btn" @click="resetFilters">重置</button>
            <button class="apply-btn" @click="applyFilters">套用篩選</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "AccommodationList",
    data() {
      return {
        searchQuery: "",
        showFilterModal: false,
        sortOption: "newest",
        filters: {
          minPrice: 5000,
          maxPrice: 20000,
          types: [],
          features: []
        },
        properties: [
          {
            id: 1,
            title: "陽光套房，近中央大學",
            location: "中壢區中大路300號附近",
            price: 7800,
            bedrooms: 1,
            bathrooms: 1,
            size: 8,
            isFavorite: false,
            tags: ["有陽台", "近學校", "新裝修"],
            image: "https://picsum.photos/id/1031/600/400"
          },
          {
            id: 2,
            title: "寧靜雅房，走路10分鐘到學校",
            location: "中壢區五權里",
            price: 4500,
            bedrooms: 1,
            bathrooms: 1,
            size: 6,
            isFavorite: true,
            tags: ["近夜市", "包水電", "女性限定"],
            image: "https://picsum.photos/id/1029/600/400"
          },
          {
            id: 3,
            title: "便宜實惠套房，近公車站",
            location: "中壢區中大路350號附近",
            price: 6000,
            bedrooms: 1,
            bathrooms: 1,
            size: 7,
            isFavorite: false,
            tags: ["近公車站", "學生專案", "可短租"],
            image: "https://picsum.photos/id/1040/600/400"
          },
          {
            id: 4,
            title: "精緻獨立套房，全新裝修",
            location: "中壢區五權二街",
            price: 9500,
            bedrooms: 1,
            bathrooms: 1,
            size: 10,
            isFavorite: false,
            tags: ["全新裝修", "有電梯", "可養寵物"],
            image: "https://picsum.photos/id/1048/600/400"
          }
        ]
      };
    },
    computed: {
      filteredProperties() {
        // 根據過濾條件過濾屬性
        return this.properties;
      }
    },
    methods: {
      toggleFavorite(id) {
        const property = this.properties.find(p => p.id === id);
        if (property) {
          property.isFavorite = !property.isFavorite;
        }
      },
      resetFilters() {
        this.filters = {
          minPrice: 3000,
          maxPrice: 30000,
          types: [],
          features: []
        };
      },
      applyFilters() {
        this.showFilterModal = false;
        // 應用過濾器邏輯
      }
    }
  };
  </script>
  
  <style scoped>
  .accommodation-list {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .header {
    margin-bottom: 20px;
  }
  
  .header h1 {
    font-size: 2rem;
    color: #333;
    margin-bottom: 20px;
  }
  
  .search-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 20px;
  }
  
  .search-box {
    flex: 1;
    position: relative;
    min-width: 250px;
  }
  
  .search-box input {
    width: 100%;
    padding: 12px 15px 12px 40px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
  }
  
  .search-icon {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #888;
  }
  
  .filter-options {
    display: flex;
    gap: 10px;
  }
  
  .filter-btn {
    padding: 0 20px;
    background: #f5f5f5;
    border: 1px solid #ddd;
    border-radius: 8px;
    display: flex;
    align-items: center;
    cursor: pointer;
    height: 42px;
    font-weight: 500;
  }
  
  .filter-btn:hover {
    background: #eee;
  }
  
  .sort-dropdown select {
    padding: 0 15px;
    height: 42px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #fff;
    font-size: 0.9rem;
    cursor: pointer;
  }
  
  .property-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 25px;
  }
  
  .property-card {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s, box-shadow 0.3s;
    background: white;
  }
  
  .property-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }
  
  .property-image {
    height: 180px;
    background-size: cover;
    background-position: center;
    position: relative;
  }
  
  .price-tag {
    position: absolute;
    bottom: 15px;
    left: 15px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-weight: bold;
    font-size: 0.9rem;
  }
  
  .favorite-btn {
    position: absolute;
    top: 15px;
    right: 15px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.8);
    display: flex;
    align-items: center;
    justify-content: center;
    border: none;
    cursor: pointer;
    transition: background 0.2s;
  }
  
  .favorite-btn:hover {
    background: rgba(255, 255, 255, 1);
  }
  
  .heart-outline {
    opacity: 0.5;
  }
  
  .heart-filled {
    color: #ff4757;
  }
  
  .property-info {
    padding: 15px;
  }
  
  .property-info h3 {
    margin: 0 0 10px;
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
  }
  
  .location {
    display: flex;
    align-items: center;
    color: #555;
    margin-bottom: 12px;
    font-size: 0.9rem;
  }
  
  .location i {
    margin-right: 5px;
  }
  
  .amenities {
    display: flex;
    gap: 15px;
    margin-bottom: 12px;
    color: #666;
    font-size: 0.85rem;
  }
  
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .tag {
    background: #f1f5fe;
    color: #3273dc;
    padding: 4px 10px;
    border-radius: 4px;
    font-size: 0.75rem;
  }
  
  /* 篩選器彈出視窗 */
  .filter-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  
  .filter-content {
    width: 90%;
    max-width: 500px;
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
  }
  
  .filter-content h2 {
    margin-top: 0;
    margin-bottom: 20px;
    font-size: 1.4rem;
    color: #333;
    border-bottom: 1px solid #eee;
    padding-bottom: 15px;
  }
  
  .filter-section {
    margin-bottom: 20px;
  }
  
  .filter-section h3 {
    font-size: 1rem;
    margin-bottom: 10px;
    color: #555;
  }
  
  .price-range {
    margin-bottom: 15px;
  }
  
  .price-range input[type="range"] {
    width: 100%;
    margin-bottom: 10px;
  }
  
  .price-inputs {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .price-inputs input {
    width: 100px;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  .checkbox-group {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .checkbox-group label {
    display: flex;
    align-items: center;
    font-size: 0.9rem;
    color: #555;
  }
  
  .checkbox-group input {
    margin-right: 8px;
  }
  
  .filter-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 25px;
  }
  
  .reset-btn {
    padding: 10px 20px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 6px;
    cursor: pointer;
  }
  
  .apply-btn {
    padding: 10px 20px;
    background: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  
  .apply-btn:hover {
    background: #0069d9;
  }
  </style>