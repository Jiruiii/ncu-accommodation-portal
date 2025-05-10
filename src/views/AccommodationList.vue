<template>
  <div class="accommodation-list">
    <div class="header">
      <h1>租屋列表</h1>
      <div class="search-filters">
        <div class="search-box">
          <i class="search-icon">🔍</i>
          <input
            type="text"
            placeholder="搜尋地址、特色..."
            v-model="searchQuery"
            @input="handleSearch"
          />
        </div>
        <div class="filter-options">
          <button class="filter-btn" @click="showFilterModal = true">
            篩選 <i class="filter-icon">⚙️</i>
          </button>
          <div class="sort-dropdown">
            <select v-model="sortOption" @change="applySorting">
              <option value="priceAsc">價格 ↑</option>
              <option value="priceDesc">價格 ↓</option>
              <option value="distanceAsc">距離 ↑</option>
              <option value="newest">最新刊登</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <div class="results-summary" v-if="filteredAccommodations.length > 0">
      找到 {{ filteredAccommodations.length }} 間符合條件的房源
    </div>
    <div class="results-summary no-results" v-else>
      未找到符合條件的房源，請嘗試其他條件
    </div>

    <div class="property-list">
      <div
        v-for="(property, index) in filteredAccommodations"
        :key="property.編碼 || index"
        class="property-card"
      >
        <div
          class="property-image"
          :style="{
            backgroundImage: `url(https://picsum.photos/id/${
              ((property.編碼 || index) * 13) % 100 + 1000
            }/600/400)`,
          }"
        >
          <div class="price-tag">NT$ {{ formatPrice(property.房租 || '0') }}/月</div>
          <button class="favorite-btn" @click="toggleFavorite(property.編碼 || index)">
            <i
              :class="
                isFavorite(property.編碼 || index)
                  ? 'heart-filled'
                  : 'heart-outline'
              "
            >
              {{ isFavorite(property.編碼 || index) ? "❤️" : "🤍" }}
            </i>
          </button>
        </div>
        <div class="property-info">
          <h3>{{ property.標題 || '無標題' }}</h3>
          <p class="location">
            <i class="location-icon">📍</i> {{ property.地址 || '地址不詳' }}
          </p>
          <div class="amenities">
            <span v-if="property.出租房數 && property.出租房數.套房"
              ><i class="bed-icon">🏠</i>
              {{ property.出租房數.套房.總數 || 0 }}間套房 (空房{{
                property.出租房數.套房.空房 || 0
              }}間)</span
            >
            <span v-if="property.出租房數 && property.出租房數.雅房"
              ><i class="bed-icon">🏠</i>
              {{ property.出租房數.雅房.總數 || 0 }}間雅房 (空房{{
                property.出租房數.雅房.空房 || 0
              }}間)</span
            >
            <span v-if="property.出租房數"
              ><i class="size-icon">📏</i> {{ getSizeRange(property) }}</span
            >
          </div>
          <div class="tags">
            <span
              v-for="(item, i) in getEquipments(property)"
              :key="i"
              class="tag"
              >{{ item }}</span
            >
          </div>
          <div class="contact-info">
            <i class="contact-icon">📞</i> {{ property.聯絡資訊 || '聯絡方式不詳' }}
          </div>
        </div>
      </div>
    </div>

    <!-- 篩選器彈出視窗 -->
    <div
      class="filter-modal"
      v-if="showFilterModal"
      @click.self="showFilterModal = false"
    >
      <div class="filter-content">
        <h2>篩選條件</h2>
        <div class="filter-section">
          <h3>價格範圍</h3>
          <div class="price-range">
            <div class="price-inputs">
              <input
                type="number"
                v-model.number="localFilters.minPrice"
                placeholder="最低價"
              />
              ~
              <input
                type="number"
                v-model.number="localFilters.maxPrice"
                placeholder="最高價"
              />
            </div>
          </div>
        </div>

        <div class="filter-section">
          <h3>房型</h3>
          <div class="checkbox-group">
            <label
              ><input type="checkbox" v-model="localFilters.types" value="套房" />
              套房</label
            >
            <label
              ><input type="checkbox" v-model="localFilters.types" value="雅房" />
              雅房</label
            >
          </div>
        </div>

        <div class="filter-section">
          <h3>設備與特色</h3>
          <div class="checkbox-group">
            <label
              ><input
                type="checkbox"
                v-model="localFilters.features"
                value="電冰箱"
              />
              電冰箱</label
            >
            <label
              ><input
                type="checkbox"
                v-model="localFilters.features"
                value="冷氣機"
              />
              冷氣機</label
            >
            <label
              ><input
                type="checkbox"
                v-model="localFilters.features"
                value="洗衣機"
              />
              洗衣機</label
            >
            <label
              ><input type="checkbox" v-model="localFilters.features" value="電梯" />
              有電梯</label
            >
            <label
              ><input
                type="checkbox"
                v-model="localFilters.features"
                value="光纖網路"
              />
              光纖網路</label
            >
            <label
              ><input
                type="checkbox"
                v-model="localFilters.features"
                value="停車場"
              />
              停車場</label
            >
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
import { mapState, mapGetters, mapMutations, mapActions } from 'vuex';

export default {
  name: "AccommodationList",
  data() {
    return {
      searchQuery: "",
      showFilterModal: false,
      sortOption: "newest",
      localFilters: {
        minPrice: null,
        maxPrice: null,
        types: [],
        features: []
      }
    };
  },
  computed: {
    ...mapState({
      accommodations: state => state.accommodations,
    }),
    ...mapGetters([
      'filteredAccommodations',
      'favoriteIds'
    ])
  },
  created() {
    // 從 Vuex store 載入房源資料
    this.fetchAccommodations();
  },
  methods: {
    ...mapMutations([
      'SET_SEARCH_QUERY',
      'SET_SORT_OPTION',
      'SET_FILTERS',
      'TOGGLE_FAVORITE'
    ]),
    ...mapActions([
      'fetchAccommodations',
      'applyFiltersAndSort'
    ]),
    
    handleSearch() {
      this.SET_SEARCH_QUERY(this.searchQuery);
      this.applyFiltersAndSort();
    },
    
    applySorting() {
      this.SET_SORT_OPTION(this.sortOption);
      this.applyFiltersAndSort();
    },
    
    applyFilters() {
      this.showFilterModal = false;
      this.SET_FILTERS(this.localFilters);
      this.applyFiltersAndSort();
    },
    
    resetFilters() {
      this.localFilters = {
        minPrice: null,
        maxPrice: null,
        types: [],
        features: []
      };
      this.SET_FILTERS(this.localFilters);
      this.applyFiltersAndSort();
    },
    
    toggleFavorite(id) {
      if (!id) return;
      this.TOGGLE_FAVORITE(id);
    },
    
    isFavorite(id) {
      return this.favoriteIds.includes(id);
    },
    
    formatPrice(priceString) {
      if (!priceString) return '0';
      
      try {
        if (priceString.includes("~")) {
          const prices = priceString.match(/\d+/g);
          if (prices && prices.length >= 2) {
            const [min, max] = prices.map((p) => parseInt(p));
            return `${min.toLocaleString()} ~ ${max.toLocaleString()}`;
          }
        }
        
        const prices = priceString.match(/\d+/g);
        if (prices && prices.length > 0) {
          const price = parseInt(prices[0]);
          return price.toLocaleString();
        }
        
        return '0';
      } catch (error) {
        console.error('價格格式化錯誤:', error);
        return '0';
      }
    },
    
    getSizeRange(property) {
      if (!property.出租房數) return '大小不詳';
      
      let sizes = [];

      if (property.出租房數.套房 && property.出租房數.套房.坪數) {
        sizes.push(property.出租房數.套房.坪數);
      }

      if (property.出租房數.雅房 && property.出租房數.雅房.坪數) {
        sizes.push(property.出租房數.雅房.坪數);
      }

      return sizes.length > 0 ? sizes.join(" / ") : '大小不詳';
    },
    
    getEquipments(property) {
      const allEquipments = [
        ...((property.屋內設備 || []).slice(0, 3)),
        ...((property.公共設施 || []).slice(0, 2)),
      ];

      return allEquipments.slice(0, 5);
    }
  }
};
</script>

<style scoped>

.accommodation-list {
  padding: 20px;
  
  width: 100vw;
  max-width: 100vw;
  
  margin: 0;
  height: 100vh;
  
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  /* 添加固定定位，確保完全覆蓋視窗 */
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
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

.results-summary {
  margin-bottom: 20px;
  font-size: 0.9rem;
  color: #666;
}

.no-results {
  color: #e74c3c;
  font-weight: bold;
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
  opacity: 0.7;
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
  /* 限制標題最多兩行 */
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.location {
  display: flex;
  align-items: center;
  color: #555;
  margin-bottom: 12px;
  font-size: 0.9rem;
  /* 限制地址顯示一行 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.location i {
  margin-right: 5px;
  flex-shrink: 0;
}

.amenities {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 12px;
  color: #666;
  font-size: 0.85rem;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.tag {
  background: #f1f5fe;
  color: #3273dc;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.contact-info {
  font-size: 0.85rem;
  color: #555;
  border-top: 1px solid #eee;
  padding-top: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.price-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.price-inputs input {
  width: 100%;
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

@media (max-width: 1200px) {
  .accommodation-list {
    padding: 15px;
  }
  
  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 992px) {
  .header h1 {
    font-size: 1.8rem;
  }
  
  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 15px;
  }
  
  .property-image {
    height: 160px;
  }
}

@media (max-width: 768px) {
  .header h1 {
    font-size: 1.6rem;
    margin-bottom: 15px;
  }
  
  .search-filters {
    flex-direction: column;
    gap: 12px;
  }
  
  .filter-options {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-btn {
    flex: 1;
    padding: 0 15px;
    height: 38px;
  }
  
  .sort-dropdown {
    flex: 1;
    margin-left: 10px;
  }
  
  .sort-dropdown select {
    width: 100%;
    height: 38px;
  }
  
  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
  }
  
  .property-card {
    display: flex;
    flex-direction: column;
  }
  
  .property-image {
    height: 200px;
  }
  
  .checkbox-group {
    grid-template-columns: 1fr;
  }
  
  .filter-content {
    width: 95%;
    padding: 20px 15px;
  }
}

@media (max-width: 576px) {
  .accommodation-list {
    padding: 10px;
  }
  
  .header h1 {
    font-size: 1.4rem;
    margin-bottom: 12px;
  }
  
  .property-image {
    height: 180px;
  }
  
  .property-info h3 {
    font-size: 1rem;
  }
  
  .amenities {
    flex-direction: column;
    gap: 8px;
  }
  
  .price-inputs {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .filter-actions {
    flex-direction: column-reverse;
    gap: 10px;
  }
  
  .reset-btn, .apply-btn {
    width: 100%;
    padding: 10px 0;
  }
  
  .filter-section h3 {
    font-size: 0.95rem;
  }
}

/* 修復直向手機模式下的問題 */
@media (max-height: 700px) and (max-width: 576px) {
  .filter-modal {
    align-items: flex-start;
    padding-top: 10px;
  }
  
  .filter-content {
    max-height: 90vh;
    overflow-y: auto;
  }
  
  .checkbox-group {
    max-height: 120px;
    overflow-y: auto;
  }
}

/* 處理寬螢幕顯示 */
@media (min-width: 1400px) {
  .accommodation-list {
   width: 100%;
  }
  
  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}
</style>


