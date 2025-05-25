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

    <div class="results-summary" v-if="loading">
      <div class="loading-spinner">載入中...</div>
    </div>
    <div class="results-summary" v-else-if="filteredAccommodations.length > 0">
      找到 {{ filteredAccommodations.length }} 間符合條件的房源
    </div>
    <div class="results-summary no-results" v-else>
      未找到符合條件的房源，請嘗試其他條件
    </div>

    <div class="property-list">
      <div
        v-for="(property, index) in paginatedProperties"
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
            <div
              :class="
                isFavorite(property.編碼 || index)
                  ? 'heart-filled'
                  : 'heart-outline'
              "
            ></div>
          </button>

          <div class="no-photo-notice" v-if="!hasPhotos(property)">
            屋主尚未更新照片
          </div>
        </div>
        <div class="property-info">
          <h3>{{ property.標題 || "無標題" }}</h3>
          <p class="location">
            <i class="location-icon">📍</i>
            <span>{{ property.地址 || "地址不詳" }}</span>
          </p>
          <div class="property-highlights">
            <div class="amenities">
              <div
                v-if="property.出租房數 && property.出租房數.套房"
                class="room-type"
              >
                <i class="bed-icon">🏠</i>
                <span>{{ property.出租房數.套房.總數 || 0 }}間套房</span>
                <span class="available-rooms"
                  >(空房{{ property.出租房數.套房.空房 || 0 }}間)</span
                >
              </div>
              <div
                v-if="property.出租房數 && property.出租房數.雅房"
                class="room-type"
              >
                <i class="bed-icon">🏠</i>
                <span>{{ property.出租房數.雅房.總數 || 0 }}間雅房</span>
                <span class="available-rooms"
                  >(空房{{ property.出租房數.雅房.空房 || 0 }}間)</span
                >
              </div>
              <div v-if="property.出租房數" class="room-size">
                <i class="size-icon">📏</i>
                <span>{{ getSizeRange(property) }}</span>
              </div>
            </div>
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

    <!-- 分頁控制元件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button
        class="page-btn prev"
        @click="prevPage"
        :disabled="currentPage === 1"
        :class="{ disabled: currentPage === 1 }"
      >
        &laquo; 上一頁
      </button>

      <button v-if="pageButtons[0] > 1" class="page-btn" @click="goToPage(1)">
        1
      </button>

      <span v-if="pageButtons[0] > 2" class="ellipsis">...</span>

      <button
        v-for="page in pageButtons"
        :key="page"
        class="page-btn"
        :class="{ active: currentPage === page }"
        @click="goToPage(page)"
      >
        {{ page }}
      </button>

      <span
        v-if="pageButtons[pageButtons.length - 1] < totalPages - 1"
        class="ellipsis"
        >...</span
      >

      <button
        v-if="pageButtons[pageButtons.length - 1] < totalPages"
        class="page-btn"
        @click="goToPage(totalPages)"
      >
        {{ totalPages }}
      </button>

      <button
        class="page-btn next"
        @click="nextPage"
        :disabled="currentPage === totalPages"
        :class="{ disabled: currentPage === totalPages }"
      >
        下一頁 &raquo;
      </button>
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
            @mouseover="stopSlideShow"
            @mouseleave="startSlideShow"
          ></div>

          <div
            class="no-photo-notice large"
            v-if="!hasPhotos(selectedProperty)"
          >
            屋主尚未更新照片
          </div>

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
              <div
                :class="
                  isFavorite(selectedProperty.編碼 || 0)
                    ? 'heart-filled'
                    : 'heart-outline'
                "
              ></div>
            </button>
          </div>
        </div>

        <!-- 評論組件 -->
        <CommentSection
          v-if="selectedProperty"
          :propertyId="selectedProperty.編碼"
        />
      </div>
    </div>
  </div>
</template>

<script>
  import { mapState, mapGetters, mapMutations, mapActions } from "vuex";
  import CommentSection from "@/components/CommentSection.vue";

  export default {
    name: "AccommodationList",
    components: {
      CommentSection,
    },

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
        slideShowInterval: null, // 自動輪播計時器
        autoSlideShowEnabled: true, // 是否啟用自動輪播
        slideShowDelay: 2000, // 輪播間隔，2秒
        currentPage: 1, // 當前頁碼
        totalPages: 1, // 總頁數
        pageHeight: 600, // 每頁的目標高度 (可以根據需要調整)
      };
    },

    computed: {
      ...mapState({
        accommodations: (state) => state.accommodations,
        loading: (state) => state.loading,
      }),
      ...mapGetters([
        "filteredAccommodations",
        "favoriteIds",
        "getPropertyComments",
        "getPropertyRating",
        "getPropertyCommentCount",
      ]),
      // 計算當前頁應顯示的房源
      paginatedProperties() {
        // 先將所有過濾後的房源切分為多個頁面
        const pages = this.divideByHeight(this.filteredAccommodations);

        // 確保頁碼在有效範圍內
        const validPage = Math.min(this.currentPage, Math.max(1, pages.length));

        // 返回當前頁的房源
        return pages[validPage - 1] || [];
      },

      // 計算應顯示的頁碼按鈕
      pageButtons() {
        const buttons = [];
        const maxButtons = 5; // 最多顯示的頁碼按鈕數

        // 計算起始和結束頁碼
        let startPage = Math.max(
          1,
          this.currentPage - Math.floor(maxButtons / 2)
        );
        const endPage = Math.min(this.totalPages, startPage + maxButtons - 1);

        // 調整起始頁碼，確保顯示足夠的按鈕
        startPage = Math.max(1, endPage - maxButtons + 1);

        // 生成頁碼按鈕
        for (let i = startPage; i <= endPage; i++) {
          buttons.push(i);
        }

        return buttons;
      },
    },

    created() {
      // 檢查資料是否已初始化，避免重複請求
      if (
        !this.$store.getters.isDataInitialized &&
        this.accommodations.length === 0
      ) {
        this.fetchAccommodations();
      } else {
        // 如果已有資料，僅應用篩選和排序
        this.applyFiltersAndSort();
      }
    },

    mounted() {
      // 初始化頁面高度
      const viewportHeight = window.innerHeight;
      this.pageHeight = Math.max(8000, viewportHeight * 1.5);

      // 添加窗口大小變化監聽器
      window.addEventListener("resize", this.handleResize);

      // 初始化分頁
      this.$nextTick(() => {
        this.reloadContent();
      });
    },

    beforeUnmount() {
      // 清除輪播定時器
      this.stopSlideShow();

      // 移除窗口大小變化監聽器
      window.removeEventListener("resize", this.handleResize);
    },

    // 添加 watch 以監控數據變化
    watch: {
      // 監控過濾後的房源以更新總頁數
      filteredAccommodations: {
        handler(newVal) {
          this.$nextTick(() => {
            // 計算分頁
            const pages = this.divideByHeight(newVal);
            this.totalPages = pages.length;

            // 確保當前頁碼有效
            if (this.currentPage > this.totalPages) {
              this.currentPage = Math.max(1, this.totalPages);
            }
          });
        },
        immediate: true,
      },

      // 監控總頁數變化
      totalPages(newVal) {
        // 如果當前頁超出總頁數，調整為最大有效頁碼
        if (this.currentPage > newVal) {
          this.currentPage = Math.max(1, newVal);
        }
      },
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
        this.currentPage = 1; // 重置為第一頁
      },

      applySorting() {
        this.SET_SORT_OPTION(this.sortOption);
        this.applyFiltersAndSort();
        this.currentPage = 1; // 重置為第一頁
      },

      applyFilters() {
        this.showFilterModal = false;
        this.SET_FILTERS(this.localFilters);
        this.applyFiltersAndSort();
        this.currentPage = 1; // 重置為第一頁
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
        this.currentPage = 1; // 重置為第一頁
      },

      toggleFavorite(id) {
        if (!id) return;

        // 檢查用戶是否登入 - 使用正確的 getter 路徑
        if (this.$store.getters["user/isLoggedIn"]) {
          // 使用 API 切換收藏狀態
          this.$store.dispatch("toggleFavoriteWithApi", id);
        } else {
          // 用戶未登入，僅在本地切換收藏狀態
          this.TOGGLE_FAVORITE(id);
        }
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
          sizes.push(`套房${property.出租房數.套房.坪數}`);
        }

        if (property.出租房數.雅房 && property.出租房數.雅房.坪數) {
          sizes.push(`雅房${property.出租房數.雅房.坪數}`);
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

      // 獲取房源圖片
      getPropertyImage(property, index) {
        if (!property) return "";

        // 有照片時顯示真實照片
        if (
          property.房屋照片 &&
          Array.isArray(property.房屋照片) &&
          property.房屋照片.length > 0
        ) {
          // 檢查圖片並找到可用的
          let attempts = 0;
          let currentIndex = index;
          const maxAttempts = property.房屋照片.length;

          // 遞迴查找可用圖片
          const findValidImage = (idx) => {
            // 防止無限循環
            if (attempts >= maxAttempts) {
              return `url(https://picsum.photos/id/${
                (((property.編碼 || 0) * 13) % 100) + 1000
              }/600/400)`;
            }

            attempts++;

            // 確保索引在範圍內
            if (idx >= property.房屋照片.length) {
              idx = 0; // 循環回到第一張
            }

            const imageUrl = property.房屋照片[idx];

            // 嘗試載入圖片
            try {
              const loadedImg = require("@/" + imageUrl);

              // 檢查實際載入後的圖片URL是否包含"-1.49632716"
              if (
                loadedImg &&
                typeof loadedImg === "string" &&
                loadedImg.includes("-1.49632716")
              ) {
                return findValidImage(idx + 1);
              }

              return `url(${loadedImg})`;
            } catch (e) {
              return findValidImage(idx + 1);
            }
          };

          // 開始查找有效圖片
          return findValidImage(currentIndex);
        }

        // 無照片時使用預設圖片
        return 'url(\'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="1" height="1" viewBox="0 0 1 1"%3E%3Crect width="1" height="1" fill="%23f5f5f5"/%3E%3C/svg%3E\')';
      },

      // 顯示房源詳細資訊
      showPropertyDetail(property) {
        this.selectedProperty = property;
        this.currentPhotoIndex = 0;
        document.body.style.overflow = "hidden"; // 防止背景滾動

        // 立即開始輪播，無需檢查 autoSlideShowEnabled
        this.$nextTick(() => {
          this.startSlideShow();
        });
      },

      // 關閉房源詳細資訊
      closePropertyDetail() {
        // 停止輪播
        this.stopSlideShow();

        this.selectedProperty = null;
        document.body.style.overflow = "auto"; // 恢復背景滾動
      },

      // 下一張照片
      nextPhoto(event) {
        event.stopPropagation(); // 阻止事件傳播

        // 手動切換時暫時停止自動輪播
        if (this.autoSlideShowEnabled) {
          this.stopSlideShow();

          // 2秒後重新開始輪播
          setTimeout(() => {
            if (this.selectedProperty && this.autoSlideShowEnabled) {
              this.startSlideShow();
            }
          }, 2000);
        }

        if (this.selectedProperty && this.hasPhotos(this.selectedProperty)) {
          this.currentPhotoIndex =
            (this.currentPhotoIndex + 1) %
            this.getPhotoCount(this.selectedProperty);
        }
      },

      // 上一張照片
      prevPhoto(event) {
        event.stopPropagation(); // 阻止事件傳播

        // 手動切換時暫時停止自動輪播
        if (this.autoSlideShowEnabled) {
          this.stopSlideShow();

          // 2秒後重新開始輪播
          setTimeout(() => {
            if (this.selectedProperty && this.autoSlideShowEnabled) {
              this.startSlideShow();
            }
          }, 2000);
        }

        if (this.selectedProperty && this.hasPhotos(this.selectedProperty)) {
          this.currentPhotoIndex =
            (this.currentPhotoIndex -
              1 +
              this.getPhotoCount(this.selectedProperty)) %
            this.getPhotoCount(this.selectedProperty);
        }
      },

      // 聯絡房東功能
      contactLandlord() {
        if (this.selectedProperty && this.selectedProperty.聯絡資訊) {
          // 如果聯絡資訊是電話號碼，則使用tel協議開啟撥號介面
          window.open(`tel:${this.selectedProperty.聯絡資訊}`);
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

      // 開始自動輪播
      startSlideShow() {
        // 清除之前的計時器
        this.stopSlideShow();

        // 只有在有選中的房源且有多張照片時才啟動輪播
        if (
          this.selectedProperty &&
          this.hasMultiplePhotos(this.selectedProperty)
        ) {
          this.slideShowInterval = setInterval(() => {
            // 滾動到下一張照片
            this.currentPhotoIndex =
              (this.currentPhotoIndex + 1) %
              this.getPhotoCount(this.selectedProperty);
          }, this.slideShowDelay);
        }
      },

      // 停止自動輪播
      stopSlideShow() {
        if (this.slideShowInterval) {
          clearInterval(this.slideShowInterval);
          this.slideShowInterval = null;
        }
      },

      // 根據高度將房源分頁
      divideByHeight(properties) {
        // 如果沒有房源，返回空頁
        if (!properties.length) return [[]];

        const pages = [];
        let currentPage = [];
        let currentHeight = 0;

        // 計算每個房源卡片的估計高度
        const estimateItemHeight = (item) => {
          // 基本高度 (卡片本身高度)
          let height = 300;

          // 根據內容增加高度
          if (item.標題 && item.標題.length > 30) height += 20;
          if (item.地址 && item.地址.length > 40) height += 20;

          // 根據設備數量增加高度
          const equipmentsCount =
            (item.屋內設備 || []).length + (item.公共設施 || []).length;
          if (equipmentsCount > 5) height += 25;

          return height;
        };

        // 遍歷所有房源，計算高度並分頁
        for (const property of properties) {
          const itemHeight = estimateItemHeight(property);

          // 如果添加此項目會超出頁面高度，則開始新的一頁
          if (
            currentHeight + itemHeight > this.pageHeight &&
            currentPage.length > 0
          ) {
            pages.push([...currentPage]);
            currentPage = [property];
            currentHeight = itemHeight;
          } else {
            // 否則添加到當前頁
            currentPage.push(property);
            currentHeight += itemHeight;
          }
        }

        // 確保添加最後一頁
        if (currentPage.length > 0) {
          pages.push(currentPage);
        }

        // 更新總頁數
        this.totalPages = pages.length;

        return pages;
      },

      // 跳轉到指定頁
      goToPage(page) {
        if (page >= 1 && page <= this.totalPages) {
          this.currentPage = page;
          // 回到頁面頂部
          window.scrollTo({ top: 0, behavior: "smooth" });
        }
      },

      // 跳到上一頁
      prevPage() {
        this.goToPage(this.currentPage - 1);
      },

      // 跳到下一頁
      nextPage() {
        this.goToPage(this.currentPage + 1);
      },

      // 監聽窗口大小變化
      handleResize() {
        // 根據當前視窗高度調整頁面高度
        const viewportHeight = window.innerHeight;
        this.pageHeight = Math.max(6000, viewportHeight * 1.5);

        // 重新計算分頁並保持當前頁面位置
        const currentIndex = this.currentPage - 1;
        const pages = this.divideByHeight(this.filteredAccommodations);
        this.goToPage(Math.min(currentIndex + 1, pages.length));
      },

      // 重載內容以適應窗口大小變化或內容變化
      reloadContent() {
        this.divideByHeight(this.filteredAccommodations);
        if (this.currentPage > this.totalPages) {
          this.currentPage = this.totalPages || 1;
        }
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

  .loading-spinner {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100px;
    font-size: 1.2rem;
    color: #007bff;
  }

  .loading-spinner:after {
    content: "";
    width: 20px;
    height: 20px;
    margin-left: 15px;
    border: 2px solid #007bff;
    border-top: 2px solid transparent;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
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
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.08);
    transition: all 0.3s;
    background: white;
    cursor: pointer;
    border: 1px solid #eaeaea;
  }

  .property-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.12);
    border-color: #d0e3ff;
  }

  .property-info {
    padding: 18px;
  }

  .property-image {
    height: 180px;
    background-size: cover;
    background-position: center;
    position: relative;
  }

  .property-highlights {
    margin-bottom: 15px;
  }

  .amenities {
    display: flex;
    flex-direction: column;
    gap: 8px;
    color: #555;
    font-size: 0.9rem;
  }

  .room-type,
  .room-size {
    display: flex;
    align-items: center;
  }

  .bed-icon,
  .size-icon {
    margin-right: 8px;
    font-size: 1rem;
    color: #666;
  }

  .available-rooms {
    color: #28a745;
    margin-left: 5px;
    font-weight: 500;
  }

  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 15px;
  }

  .tag {
    background: #f0f7ff;
    color: #0366d6;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    letter-spacing: 0.02em;
    font-weight: 500;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    transition: all 0.2s;
  }

  .contact-info {
    font-size: 0.85rem;
    color: #444;
    border-top: 1px solid #eee;
    padding-top: 12px;
    display: flex;
    align-items: center;
  }

  .contact-icon {
    margin-right: 8px;
    color: #007bff;
    font-size: 1rem;
  }

  .property-detail-info h2 {
    margin: 0 0 15px;
    font-size: 1.6rem;
    color: #333;
    line-height: 1.4;
    font-weight: 600;
    letter-spacing: 0.02em;
  }

  .detail-price {
    font-size: 1.5rem;
    color: #0366d6;
    font-weight: bold;
    margin-bottom: 18px;
    letter-spacing: 0.02em;
  }

  .detail-address {
    display: flex;
    align-items: flex-start;
    margin-bottom: 25px;
    font-size: 1.05rem;
    color: #555;
    line-height: 1.5;
    padding: 10px 15px;
    background: #f8f9fa;
    border-radius: 8px;
  }

  .detail-section {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
  }

  .detail-section h3 {
    margin: 0 0 15px;
    font-size: 1.2rem;
    color: #333;
    font-weight: 600;
    letter-spacing: 0.01em;
  }

  .feature-tag {
    background: #eef6ff;
    color: #0366d6;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.95rem;
    font-weight: 500;
    transition: all 0.2s;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  }

  .feature-tag:hover {
    background: #dceefb;
    transform: translateY(-2px);
  }

  .tag:hover {
    background: #e1f0ff;
    transform: translateY(-1px);
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

  .property-info h3 {
    margin: 0 0 12px;
    font-size: 1.2rem;
    font-weight: 600;
    color: #333;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    line-height: 1.4;
    letter-spacing: 0.02em;
  }

  .location {
    display: flex;
    align-items: flex-start;
    color: #555;
    font-size: 0.9rem;
    margin-bottom: 12px;
    line-height: 1.5;
  }

  .location i {
    margin-right: 8px;
    margin-top: 3px;
    flex-shrink: 0;
  }

  .location span {
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  .heart-outline,
  .heart-filled {
    width: 18px;
    height: 18px;
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
    display: inline-block;
  }

  .heart-outline {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' stroke='%23777' fill='none' stroke-width='2'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E");
  }

  .heart-filled {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ff4757'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E");
  }

  /* 分頁控制樣式 */
  .pagination {
    display: flex;
    justify-content: center;
    margin: 30px 0;
    gap: 5px;
  }

  .page-btn {
    min-width: 40px;
    height: 40px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: #333;
    transition: all 0.2s;
    font-size: 14px;
    padding: 0 12px;
  }

  .page-btn:hover:not(.disabled):not(.active) {
    background: #f5f5f5;
    border-color: #ccc;
  }

  .page-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
  }

  .page-btn.disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .page-btn.prev,
  .page-btn.next {
    padding: 0 15px;
  }

  .ellipsis {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    color: #777;
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
    margin: 15px 0 30px 0;
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

  /* 修改圖片過渡效果 */
  .gallery-image {
    width: 100%;
    height: 100%;
    background-size: contain;
    background-position: center;
    background-repeat: no-repeat;
    background-color: #f5f5f5;
    transition: background-image 0.3s ease; /* 添加過渡效果使輪播更平滑 */
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

  .favorite-action .heart-outline,
  .favorite-action .heart-filled {
    margin-left: 8px;
  }

  .no-photo-notice {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 8px 16px;
    border-radius: 8px;
    font-size: 0.9rem;
    text-align: center;
    white-space: nowrap;
  }

  .no-photo-notice.large {
    padding: 12px 24px;
    font-size: 1.1rem;
    font-weight: 500;
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

    .comment-header {
      flex-direction: column;
      gap: 10px;
    }

    .comment-rating {
      align-self: flex-start;
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
