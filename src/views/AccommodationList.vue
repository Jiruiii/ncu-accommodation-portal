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
        @click="showPropertyDetail(property)"
      >
        <div
          class="property-image"
          :style="{
            backgroundImage: getPropertyImage(property, 0),
          }"
        >
          <div class="price-tag">
            NT$ {{ formatPrice(property.房租 || "0") }}/月
          </div>
          <button
            class="favorite-btn"
            @click.stop="toggleFavorite(property.編碼 || index)"
          >
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
          <h3>{{ property.標題 || "無標題" }}</h3>
          <p class="location">
            <i class="location-icon">📍</i> {{ property.地址 || "地址不詳" }}
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
            <i class="contact-icon">📞</i>
            {{ property.聯絡資訊 || "聯絡方式不詳" }}
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
              ><input
                type="checkbox"
                v-model="localFilters.types"
                value="套房"
              />
              套房</label
            >
            <label
              ><input
                type="checkbox"
                v-model="localFilters.types"
                value="雅房"
              />
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
              ><input
                type="checkbox"
                v-model="localFilters.features"
                value="電梯"
              />
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

    <!-- 房源詳細資訊彈窗 -->
    <div
      class="property-detail-modal"
      v-if="selectedProperty"
      @click.self="closePropertyDetail"
    >
      <div class="property-detail-content">
        <button class="close-btn" @click="closePropertyDetail">×</button>

        <div class="property-detail-gallery">
          <div
            class="gallery-image"
            :style="{
              backgroundImage: getPropertyImage(
                selectedProperty,
                currentPhotoIndex
              ),
            }"
          ></div>

          <button
            v-if="hasMultiplePhotos(selectedProperty)"
            class="gallery-nav prev-btn"
            @click.stop="prevPhoto"
          >
            &#10094;
          </button>

          <button
            v-if="hasMultiplePhotos(selectedProperty)"
            class="gallery-nav next-btn"
            @click.stop="nextPhoto"
          >
            &#10095;
          </button>

          <div class="photo-counter" v-if="hasPhotos(selectedProperty)">
            {{ currentPhotoIndex + 1 }}/{{ getPhotoCount(selectedProperty) }}
          </div>
        </div>

        <div class="property-detail-info">
          <h2>{{ selectedProperty.標題 || "無標題" }}</h2>

          <div class="detail-price">
            NT$ {{ formatPrice(selectedProperty.房租 || "0") }}/月
          </div>

          <div class="detail-address">
            <i class="location-icon">📍</i>
            {{ selectedProperty.地址 || "地址不詳" }}
          </div>

          <div class="detail-section">
            <h3>房型資訊</h3>
            <div class="detail-room-info">
              <div
                v-if="
                  selectedProperty.出租房數 && selectedProperty.出租房數.套房
                "
              >
                <p>
                  <strong>套房：</strong>
                  {{ selectedProperty.出租房數.套房.總數 || 0 }}間 (空房
                  {{ selectedProperty.出租房數.套房.空房 || 0 }}間)
                </p>
                <p>
                  <strong>坪數：</strong>
                  {{ selectedProperty.出租房數.套房.坪數 || "未提供" }}
                </p>
              </div>
              <div
                v-if="
                  selectedProperty.出租房數 && selectedProperty.出租房數.雅房
                "
              >
                <p>
                  <strong>雅房：</strong>
                  {{ selectedProperty.出租房數.雅房.總數 || 0 }}間 (空房
                  {{ selectedProperty.出租房數.雅房.空房 || 0 }}間)
                </p>
                <p>
                  <strong>坪數：</strong>
                  {{ selectedProperty.出租房數.雅房.坪數 || "未提供" }}
                </p>
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3>聯絡資訊</h3>
            <p>{{ selectedProperty.聯絡資訊 || "聯絡方式不詳" }}</p>
          </div>

          <div class="detail-section" v-if="selectedProperty.其他費用">
            <h3>其他費用</h3>
            <p>{{ selectedProperty.其他費用 }}</p>
          </div>

          <div
            class="detail-section features"
            v-if="
              selectedProperty.屋內設備 && selectedProperty.屋內設備.length > 0
            "
          >
            <h3>屋內設備</h3>
            <div class="features-list">
              <span
                v-for="(item, i) in selectedProperty.屋內設備"
                :key="`indoor-${i}`"
                class="feature-tag"
              >
                {{ item }}
              </span>
            </div>
          </div>

          <div
            class="detail-section features"
            v-if="
              selectedProperty.公共設施 && selectedProperty.公共設施.length > 0
            "
          >
            <h3>公共設施</h3>
            <div class="features-list">
              <span
                v-for="(item, i) in selectedProperty.公共設施"
                :key="`public-${i}`"
                class="feature-tag"
              >
                {{ item }}
              </span>
            </div>
          </div>

          <div
            class="detail-section"
            v-if="
              selectedProperty.屋況說明 && selectedProperty.屋況說明.length > 0
            "
          >
            <h3>屋況說明</h3>
            <ul class="condition-list">
              <li
                v-for="(item, i) in selectedProperty.屋況說明"
                :key="`condition-${i}`"
              >
                {{ item }}
              </li>
            </ul>
          </div>

          <div class="detail-actions">
            <button
              class="action-btn contact-btn"
              @click.stop="contactLandlord"
            >
              聯絡房東
            </button>
            <button
              class="action-btn favorite-action"
              @click.stop="toggleFavorite(selectedProperty.編碼 || 0)"
            >
              {{ isFavorite(selectedProperty.編碼 || 0) ? "取消收藏" : "收藏" }}
              <i>{{ isFavorite(selectedProperty.編碼 || 0) ? "❤️" : "🤍" }}</i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapGetters, mapMutations, mapActions } from "vuex";

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
        features: [],
      },
      selectedProperty: null,
      currentPhotoIndex: 0,
    };
  },
  computed: {
    ...mapState({
      accommodations: (state) => state.accommodations,
    }),
    ...mapGetters(["filteredAccommodations", "favoriteIds"]),
  },
  created() {
    // 從 Vuex store 載入房源資料
    this.fetchAccommodations();
  },
  methods: {
    ...mapMutations([
      "SET_SEARCH_QUERY",
      "SET_SORT_OPTION",
      "SET_FILTERS",
      "TOGGLE_FAVORITE",
    ]),
    ...mapActions(["fetchAccommodations", "applyFiltersAndSort"]),

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
        features: [],
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
      if (!priceString) return "0";

      try {
        if (typeof priceString === "string" && priceString.includes("~")) {
          const prices = priceString.match(/\d+/g);
          if (prices && prices.length >= 2) {
            const [min, max] = prices.map((p) => parseInt(p));
            return `${min.toLocaleString()} ~ ${max.toLocaleString()}`;
          }
        }

        const prices = priceString.toString().match(/\d+/g);
        if (prices && prices.length > 0) {
          const price = parseInt(prices[0]);
          return price.toLocaleString();
        }

        return "0";
      } catch (error) {
        console.error("價格格式化錯誤:", error);
        return "0";
      }
    },

    getSizeRange(property) {
      if (!property.出租房數) return "大小不詳";

      let sizes = [];

      if (property.出租房數.套房 && property.出租房數.套房.坪數) {
        sizes.push(property.出租房數.套房.坪數);
      }

      if (property.出租房數.雅房 && property.出租房數.雅房.坪數) {
        sizes.push(property.出租房數.雅房.坪數);
      }

      return sizes.length > 0 ? sizes.join(" / ") : "大小不詳";
    },

    getEquipments(property) {
      const allEquipments = [
        ...(property.屋內設備 || []).slice(0, 3),
        ...(property.公共設施 || []).slice(0, 2),
      ];

      return allEquipments.slice(0, 5);
    },

    // 新增方法 - 獲取房源圖片
    getPropertyImage(property, index) {
      if (!property) return "";

      // 有照片時顯示真實照片
      if (
        property.房屋照片 &&
        Array.isArray(property.房屋照片) &&
        property.房屋照片.length > 0
      ) {
        if (index >= 0 && index < property.房屋照片.length) {
          try {
            // 使用 require 動態引入圖片
            const imageUrl = property.房屋照片[index];
            // 判斷照片路徑是否存在，如果不存在則使用預設圖片
            try {
              return `url(${require("@/" + imageUrl)})`;
            } catch (e) {
              return `url(https://picsum.photos/id/${
                (((property.編碼 || 0) * 13) % 100) + 1000
              }/600/400)`;
            }
          } catch (error) {
            console.error("圖片載入錯誤:", error);
            return `url(https://picsum.photos/id/${
              (((property.編碼 || 0) * 13) % 100) + 1000
            }/600/400)`;
          }
        }
      }

      // 無照片時使用預設圖片（根據編碼產生不同圖片）
      return `url(https://picsum.photos/id/${
        (((property.編碼 || 0) * 13) % 100) + 1000
      }/600/400)`;
    },

    // 新增方法 - 顯示房源詳細資訊
    showPropertyDetail(property) {
      this.selectedProperty = property;
      this.currentPhotoIndex = 0;
      document.body.style.overflow = "hidden"; // 防止背景滾動
    },

    // 新增方法 - 關閉房源詳細資訊
    closePropertyDetail() {
      this.selectedProperty = null;
      document.body.style.overflow = "auto"; // 恢復背景滾動
    },

    // 新增方法 - 下一張照片
    nextPhoto(event) {
      event.stopPropagation(); // 阻止事件傳播
      if (this.selectedProperty && this.hasPhotos(this.selectedProperty)) {
        this.currentPhotoIndex =
          (this.currentPhotoIndex + 1) %
          this.getPhotoCount(this.selectedProperty);
      }
    },

    // 新增方法 - 上一張照片
    prevPhoto(event) {
      event.stopPropagation(); // 阻止事件傳播
      if (this.selectedProperty && this.hasPhotos(this.selectedProperty)) {
        this.currentPhotoIndex =
          (this.currentPhotoIndex -
            1 +
            this.getPhotoCount(this.selectedProperty)) %
          this.getPhotoCount(this.selectedProperty);
      }
    },

    // 新增方法 - 聯絡房東
    contactLandlord() {
      if (this.selectedProperty && this.selectedProperty.聯絡資訊) {
        alert(`聯絡資訊：${this.selectedProperty.聯絡資訊}`);
      }
    },

    // 檢查是否有多張照片
    hasMultiplePhotos(property) {
      return this.getPhotoCount(property) > 1;
    },

    // 檢查是否有照片
    hasPhotos(property) {
      return this.getPhotoCount(property) > 0;
    },

    // 獲取照片數量
    getPhotoCount(property) {
      if (
        !property ||
        !property.房屋照片 ||
        !Array.isArray(property.房屋照片)
      ) {
        return 0;
      }
      return property.房屋照片.length;
    },
  },
};
</script>

<style scoped>
.accommodation-list {
  padding: 20px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  height: 100vh;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.header {
  margin-bottom: 20px;
}

.header h1 {
  font-size: 2rem;
  color: #333;
  margin: 0 0 20px;
}

.search-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
}

.search-box {
  flex: 1;
  min-width: 200px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.95rem;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #777;
}

.filter-options {
  display: flex;
  gap: 10px;
}

.filter-btn {
  padding: 0 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  cursor: pointer;
  height: 42px;
  font-weight: 500;
}

.filter-btn:hover {
  background: #0069d9;
}

.sort-dropdown select {
  padding: 8px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fff;
  font-size: 0.9rem;
  cursor: pointer;
  height: 42px;
}

.results-summary {
  margin-bottom: 20px;
  color: #555;
}

.no-results {
  color: #dc3545;
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
  cursor: pointer;
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
  color: #777;
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
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2; /* 最多顯示兩行 */
  -webkit-box-orient: vertical;
}

.location {
  display: flex;
  align-items: center;
  color: #555;
  font-size: 0.85rem;
  margin-bottom: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.location i {
  margin-right: 5px;
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
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  padding: 25px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.15);
}

.filter-content h2 {
  margin-top: 0;
  color: #333;
  font-size: 1.5rem;
  margin-bottom: 20px;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-section h3 {
  font-size: 1.1rem;
  color: #444;
  margin-bottom: 10px;
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
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
}

.checkbox-group {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #555;
  font-size: 0.9rem;
  cursor: pointer;
}

.filter-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 30px;
}

.reset-btn,
.apply-btn {
  padding: 10px 15px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-weight: 500;
}

.reset-btn {
  background: #f1f1f1;
  color: #333;
}

.apply-btn {
  background: #007bff;
  color: white;
}

/* 房源詳細信息彈窗 */
.property-detail-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  z-index: 1100;
  padding: 10px;
  overflow-y: auto;
  overflow-x: hidden;
}

.property-detail-content {
  width: 90%;
  max-width: 900px;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
  margin:15px 0 30px 0;
  max-height: none;
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.8);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  cursor: pointer;
  z-index: 1200;
}

.property-detail-gallery {
  position: relative;
  height: 300px;
}

.gallery-image {
  width: 100%;
  height: 100%;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #f5f5f5;
}

.gallery-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 45px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.7);
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: #333;
}

.prev-btn {
  left: 15px;
}

.next-btn {
  right: 15px;
}

.photo-counter {
  position: absolute;
  bottom: 15px;
  right: 15px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 0.8rem;
}

.property-detail-info {
  padding: 20px;
  overflow-y: visible;
}

.property-detail-info h2 {
  margin: 0 0 15px;
  font-size: 1.5rem;
  color: #333;
}

.detail-price {
  font-size: 1.3rem;
  color: #007bff;
  font-weight: bold;
  margin-bottom: 15px;
}

.detail-address {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 1rem;
  color: #555;
}

.detail-address i {
  margin-right: 8px;
}

.detail-section {
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #eee;
}

.detail-section:last-child {
  border-bottom: none;
}

.detail-section h3 {
  margin: 0 0 10px;
  font-size: 1.1rem;
  color: #444;
}

.detail-room-info {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  font-size: 0.95rem;
}

.detail-room-info p {
  margin: 5px 0;
  color: #555;
}

.detail-room-info strong {
  color: #333;
}

.features-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
}

.feature-tag {
  background: #f1f5fe;
  color: #3273dc;
  padding: 5px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.condition-list {
  margin: 10px 0;
  padding-left: 20px;
}

.condition-list li {
  margin-bottom: 8px;
  color: #555;
}

.detail-actions {
  display: flex;
  gap: 15px;
  margin-top: 20px;
}

.action-btn {
  flex: 1;
  padding: 12px 0;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.contact-btn {
  background: #007bff;
  color: white;
}

.favorite-action {
  background: #f5f5f5;
  color: #333;
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
}

@media (max-width: 992px) {
  .header h1 {
    font-size: 1.8rem;
  }

  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
    gap: 10px;
  }

  .filter-options {
    width: 100%;
    justify-content: space-between;
  }

  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
  }

  .property-detail-modal {
    align-items: flex-start;
    padding: 5px;
  }
  
  .property-detail-content {
    margin: 10px 0 20px 0;
  }
  
  .property-detail-gallery {
    height: 250px;
  }


  .gallery-image {
    height: 250px;
  }

  .detail-room-info {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-height: 600px) {
  .property-detail-gallery {
    height: 200px;
  }
}

@media (max-width: 576px), (max-height: 500px) {
  .property-detail-modal {
    padding: 0;
  }
  
  .property-detail-content {
    width: 100%;
    margin: 0;
    border-radius: 0; /* 移除圓角 */
    height: 100%; /* 佔滿整個螢幕 */
  }
  
  .property-detail-gallery {
    height: 180px;
  }
  
  .close-btn {
    top: 10px;
    right: 10px;
    width: 36px;
    height: 36px;
    background: rgba(0, 0, 0, 0.6);
    color: white;
  }
  
  .gallery-nav {
    width: 36px;
    height: 36px;
  }
}

@media (min-width: 1400px) {
  .property-list {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
}
</style>


