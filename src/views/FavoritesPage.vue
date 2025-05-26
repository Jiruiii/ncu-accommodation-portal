<template>
  <div class="favorites-page">
    <!-- 頂部區域優化，保持與 AccommodationList 一致的風格 -->
    <div class="favorites-header">
      <h1>我的收藏</h1>
      <div class="favorites-tools">
        <div class="search-box">
          <i class="search-icon">🔍</i>
          <input
            type="text"
            placeholder="搜尋標題、地址..."
            v-model="searchQuery"
            @input="filterFavorites"
          />
        </div>
        <div class="sort-dropdown">
          <span>排序方式:</span>
          <select v-model="sortBy" @change="applySorting">
            <option value="date">收藏時間</option>
            <option value="price">價格</option>
            <option value="area">面積</option>
          </select>
        </div>
        <!-- <button
          class="compare-btn"
          @click="compareSelected"
          :disabled="selectedItems.length < 2"
        >
          比較選中項目
          <span v-if="selectedItems.length">({{ selectedItems.length }})</span>
        </button> -->
        <button
          class="map-view-btn"
          @click="viewOnMap"
          :disabled="!favoriteItems.length"
        >
          <i class="map-icon"></i>
          在地圖上查看
          <span v-if="selectedItems.length"
            >(已選 {{ selectedItems.length }} 間)</span
          >
        </button>
      </div>
    </div>

    <div class="results-summary" v-if="isLoading">
      <div class="loading-spinner">載入中...</div>
    </div>
    <div class="results-summary" v-else-if="favoriteItems.length > 0">
      共收藏了 {{ favoriteItems.length }} 間房源
    </div>

    <div class="favorites-empty" v-if="!favoriteItems.length && !isLoading">
      <div class="empty-state">
        <div class="empty-icon">❤️</div>
        <h2>您還沒有收藏任何房源</h2>
        <p>瀏覽租屋列表，點擊心形圖標收藏您感興趣的房源</p>
        <button class="cta-button" @click="goToList">瀏覽租屋列表</button>
      </div>
    </div>

    <!-- 使用與 AccommodationList 相似的網格布局 -->
    <div class="favorites-grid" v-else>
      <div
        v-for="item in paginatedFavorites"
        :key="item.id"
        :id="`favorite-card-${item.id}`"
        class="favorite-card"
        :class="{ selected: isSelected(item.id) }"
      >
        <div class="card-checkbox">
          <input
            type="checkbox"
            :id="`favorite-${item.id}`"
            v-model="selectedItems"
            :value="item.id"
          />
          <label :for="`favorite-${item.id}`"></label>
        </div>
        <!-- 使用與 AccommodationList 相似的卡片結構 -->
        <div class="card-image" @click="viewDetail(item.id)">
          <div
            class="property-image"
            :style="{
              backgroundImage: getPropertyImage(item.originalProperty),
            }"
          >
            <div class="no-photo-notice" v-if="!item.hasPhotos">
              屋主尚未更新照片
            </div>
          </div>
          <span class="card-price"
            >NT$ {{ formatPrice(item.price) }} <small>/月</small></span
          >
          <button class="remove-favorite" @click.stop="removeFavorite(item.id)">
            <div class="heart-filled"></div>
          </button>
        </div>
        <div class="card-content">
          <h3 @click="viewDetail(item.id)">{{ item.title }}</h3>
          <p class="location">
            <i class="location-icon"></i>
            <span>{{ item.location }}</span>
          </p>
          <div class="property-highlights">
            <div class="amenities">
              <!-- 房型資訊 -->
              <div class="room-type" v-if="item.roomType">
                <i class="bed-icon"></i>
                <span>{{ item.roomType }}</span>
                <span class="available-rooms" v-if="item.availableRooms">
                  (空房{{ item.availableRooms }}間)
                </span>
              </div>
              <!-- 坪數資訊 -->
              <div class="room-size" v-if="item.area">
                <i class="size-icon"></i>
                <span>{{ item.area }}坪</span>
              </div>
            </div>
          </div>
          <div class="tags">
            <span v-for="(tag, i) in item.tags" :key="i" class="tag">
              {{ tag }}
            </span>
          </div>
          <div class="card-actions">
            <button @click="viewDetail(item.id)" class="view-btn">
              查看詳情
            </button>
            <button @click="contactLandlord(item.id)" class="contact-btn">
              聯繫房東
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 分頁控制元件 -->
    <div class="pagination" v-if="totalPages > 1">
      <button
        class="page-btn prev"
        @click="changePage(currentPage - 1)"
        :disabled="currentPage === 1"
        :class="{ disabled: currentPage === 1 }"
      >
        &laquo; 上一頁
      </button>

      <button v-if="pageButtons[0] > 1" class="page-btn" @click="changePage(1)">
        1
      </button>

      <span v-if="pageButtons[0] > 2" class="ellipsis">...</span>

      <button
        v-for="page in pageButtons"
        :key="page"
        class="page-btn"
        :class="{ active: currentPage === page }"
        @click="changePage(page)"
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
        @click="changePage(totalPages)"
      >
        {{ totalPages }}
      </button>

      <button
        class="page-btn next"
        @click="changePage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        :class="{ disabled: currentPage === totalPages }"
      >
        下一頁 &raquo;
      </button>
    </div>

    <!-- 添加房源詳情彈出視窗，與 AccommodationList 一致 -->
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
            <i class="location-icon"></i>
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

          <div class="detail-actions">
            <button
              class="action-btn contact-btn"
              @click.stop="contactLandlord(selectedProperty.編碼)"
            >
              聯絡房東
            </button>
            <button
              class="action-btn favorite-action"
              @click.stop="removeFavorite(selectedProperty.編碼)"
            >
              取消收藏
              <div class="heart-filled"></div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

export default {
  name: "FavoritesPage",
  setup() {
    const router = useRouter();
    const store = useStore();

    // 狀態管理
    const selectedItems = ref([]);
    const searchQuery = ref("");
    const sortBy = ref("date");
    const currentPage = ref(1);
    const itemsPerPage = ref(24);
    const isLoading = ref(false);
    const selectedProperty = ref(null);
    const currentPhotoIndex = ref(0);
    const slideShowInterval = ref(null);
    const autoSlideShowEnabled = ref(true);
    const slideShowDelay = 2000;

    // 從 store 獲取收藏房源
    const favoriteProperties = computed(() => {
      return store.getters.favoriteProperties || [];
    });

    // 格式化收藏項目列表
    const favoriteItems = computed(() => {
      return favoriteProperties.value.map((property) => ({
        id: property.編碼 || 0,
        title: property.標題 || "無標題",
        price: extractMinPrice(property.房租 || "0"),
        location: property.地址 || "地址不詳",
        area: getPropertyArea(property),
        bedrooms: getPropertyRooms(property),
        bathrooms: 1,
        tags: getPropertyTags(property),
        dateAdded: new Date(),
        originalProperty: property,
        hasPhotos: hasPhotos(property),
        roomType: getRoomTypeDisplay(property),
        availableRooms: getAvailableRooms(property),
      }));
    });

    // 搜尋篩選功能
    const filteredFavorites = computed(() => {
      if (!searchQuery.value.trim()) {
        return favoriteItems.value;
      }

      const query = searchQuery.value.toLowerCase().trim();
      return favoriteItems.value.filter((item) => {
        return (
          item.title.toLowerCase().includes(query) ||
          item.location.toLowerCase().includes(query)
        );
      });
    });

    // 排序功能
    const sortedFavorites = computed(() => {
      let sorted = [...filteredFavorites.value];

      if (sortBy.value === "date") {
        sorted.sort((a, b) => b.dateAdded - a.dateAdded);
      } else if (sortBy.value === "price") {
        sorted.sort((a, b) => a.price - b.price);
      } else if (sortBy.value === "area") {
        sorted.sort((a, b) => b.area - a.area);
      }

      return sorted;
    });

    // 分頁功能
    const paginatedFavorites = computed(() => {
      const startIndex = (currentPage.value - 1) * itemsPerPage.value;
      return sortedFavorites.value.slice(
        startIndex,
        startIndex + itemsPerPage.value
      );
    });

    // 計算總頁數
    const totalPages = computed(() =>
      Math.ceil(sortedFavorites.value.length / itemsPerPage.value)
    );

    // 計算顯示的頁碼按鈕
    const pageButtons = computed(() => {
      const buttons = [];
      const maxButtons = 5; // 最多顯示的頁碼按鈕數

      // 計算起始和結束頁碼
      let startPage = Math.max(
        1,
        currentPage.value - Math.floor(maxButtons / 2)
      );
      const endPage = Math.min(totalPages.value, startPage + maxButtons - 1);

      // 調整起始頁碼，確保顯示足夠的按鈕
      startPage = Math.max(1, endPage - maxButtons + 1);

      // 生成頁碼按鈕
      for (let i = startPage; i <= endPage; i++) {
        buttons.push(i);
      }

      return buttons;
    });

    // 同步收藏列表
    const syncFavorites = async () => {
      isLoading.value = true;
      try {
        if (store.getters["user/isLoggedIn"]) {
          await store.dispatch("syncFavorites");
        }
      } catch (error) {
        console.error("同步收藏列表失敗:", error);
      } finally {
        isLoading.value = false;
      }
    };

    // 解析最低價格
    const extractMinPrice = (priceStr) => {
      try {
        if (typeof priceStr === "string" && priceStr.includes("-")) {
          const prices = priceStr
            .split("-")
            .map((p) => parseInt(p.trim().replace(/[^\d]/g, "")));
          return prices[0] || 0;
        }
        return parseInt(priceStr.toString().replace(/[^\d]/g, "")) || 0;
      } catch (error) {
        console.error("解析價格時出錯:", error);
        return 0;
      }
    };

    // 格式化價格顯示
    const formatPrice = (priceVal) => {
      if (!priceVal) return "0";
      try {
        if (
          typeof priceVal === "string" &&
          (priceVal.includes("~") || priceVal.includes("-"))
        ) {
          // 支援 3000~4000 或 3000-4000
          const prices = priceVal.match(/\d+/g);
          if (prices && prices.length >= 2) {
            const [min, max] = prices.map((p) => parseInt(p));
            return `${min.toLocaleString()} ~ ${max.toLocaleString()}`;
          }
        }
        if (typeof priceVal === "number") {
          return priceVal.toLocaleString();
        }
        const prices = priceVal.toString().match(/\d+/g);
        if (prices && prices.length > 0) {
          const price = parseInt(prices[0]);
          return price.toLocaleString();
        }
        return "0";
      } catch (error) {
        return "0";
      }
    };

    // 獲取房間類型顯示
    const getRoomTypeDisplay = (property) => {
      if (
        property.出租房數 &&
        property.出租房數.套房 &&
        property.出租房數.套房.總數
      ) {
        return `套房 ${property.出租房數.套房.總數}間`;
      } else if (
        property.出租房數 &&
        property.出租房數.雅房 &&
        property.出租房數.雅房.總數
      ) {
        return `雅房 ${property.出租房數.雅房.總數}間`;
      }
      return "房型未提供";
    };

    // 獲取可用房間數量
    const getAvailableRooms = (property) => {
      if (
        property.出租房數 &&
        property.出租房數.套房 &&
        property.出租房數.套房.空房
      ) {
        return property.出租房數.套房.空房;
      } else if (
        property.出租房數 &&
        property.出租房數.雅房 &&
        property.出租房數.雅房.空房
      ) {
        return property.出租房數.雅房.空房;
      }
      return 0;
    };

    // 檢查是否有照片
    const hasPhotos = (property) => {
      if (
        !property ||
        !property.房屋照片 ||
        !Array.isArray(property.房屋照片)
      ) {
        return false;
      }
      return property.房屋照片.length > 0;
    };

    // 獲取房源圖片
    const getPropertyImage = (property, index = 0) => {
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
      return `url(https://picsum.photos/id/${
        (((property.編碼 || 0) * 13) % 100) + 1000
      }/600/400)`;
    };

    // 獲取房源面積
    const getPropertyArea = (property) => {
      try {
        if (
          property.出租房數 &&
          property.出租房數.套房 &&
          property.出租房數.套房.坪數
        ) {
          return parseFloat(property.出租房數.套房.坪數) || 0;
        } else if (
          property.出租房數 &&
          property.出租房數.雅房 &&
          property.出租房數.雅房.坪數
        ) {
          return parseFloat(property.出租房數.雅房.坪數) || 0;
        }
        return 0;
      } catch (error) {
        console.error("獲取面積時出錯:", error);
        return 0;
      }
    };

    // 獲取房源房間數
    const getPropertyRooms = (property) => {
      try {
        let totalRooms = 0;
        if (property.出租房數) {
          if (property.出租房數.套房 && property.出租房數.套房.總數) {
            totalRooms += parseInt(property.出租房數.套房.總數) || 0;
          }
          if (property.出租房數.雅房 && property.出租房數.雅房.總數) {
            totalRooms += parseInt(property.出租房數.雅房.總數) || 0;
          }
        }
        return totalRooms || 1;
      } catch (error) {
        console.error("獲取房間數時出錯:", error);
        return 1;
      }
    };

    // 獲取房源標籤
    const getPropertyTags = (property) => {
      const tags = [];

      try {
        // 添加房型標籤
        if (property.房型) {
          tags.push(property.房型);
        } else if (
          property.出租房數 &&
          property.出租房數.套房 &&
          property.出租房數.套房.總數
        ) {
          tags.push("套房");
        } else if (
          property.出租房數 &&
          property.出租房數.雅房 &&
          property.出租房數.雅房.總數
        ) {
          tags.push("雅房");
        }

        // 添加租金包含項目
        if (property.租金包含) {
          if (property.租金包含.水費) tags.push("含水費");
          if (property.租金包含.電費) tags.push("含電費");
          if (property.租金包含.網路) tags.push("含網路");
        }

        // 添加特色標籤
        if (property.特色) {
          if (property.特色.陽台) tags.push("有陽台");
          if (property.特色.廚房) tags.push("有廚房");
          if (property.特色.冷氣) tags.push("有冷氣");
          if (property.特色.電梯) tags.push("有電梯");
          if (property.特色.停車位) tags.push("有停車位");
        }

        // 添加設備標籤
        if (property.屋內設備 && Array.isArray(property.屋內設備)) {
          const importantEquipments = ["冰箱", "洗衣機", "電視", "床"];
          for (const item of importantEquipments) {
            if (property.屋內設備.some((e) => e.includes(item))) {
              tags.push(`有${item}`);
            }
          }
        }
      } catch (error) {
        console.error("獲取標籤時出錯:", error);
      }

      // 最多返回3個標籤
      return tags.slice(0, 3);
    };

    // 查看詳情
    const viewDetail = (id) => {
      const property = favoriteProperties.value.find((p) => p.編碼 === id);
      if (property) {
        selectedProperty.value = property;
        currentPhotoIndex.value = 0;
        document.body.style.overflow = "hidden"; // 防止背景滾動

        // 開始照片輪播
        startSlideShow();
      }
    };

    // 關閉詳情視窗
    const closePropertyDetail = () => {
      stopSlideShow();
      selectedProperty.value = null;
      document.body.style.overflow = "auto"; // 恢復背景滾動
    };

    // 聯繫房東
    const contactLandlord = (id) => {
      const property = favoriteProperties.value.find((p) => p.編碼 === id);
      if (property && property.聯絡資訊) {
        window.open(`tel:${property.聯絡資訊}`);
      } else {
        // 如果沒有電話，返回詳情頁
        viewDetail(id);
        alert("此房源未提供聯繫電話，請查看詳情頁獲取更多聯絡方式。");
      }
    };

    // 前往租屋列表
    const goToList = () => {
      router.push({ name: "accommodation-list" });
    };

    // 檢查項目是否被選中
    const isSelected = (id) => selectedItems.value.includes(id);

    // 移除收藏
    const removeFavorite = async (id) => {
      const card = document.getElementById(`favorite-card-${id}`);
      if (card) {
        card.style.opacity = "0";
        card.style.transform = "scale(0.8)";

        try {
          // 使用 store 中的 action 移除收藏
          const success = await store.dispatch("removeFavorite", id);

          if (!success) {
            // 如果 API 失敗但本地成功，顯示提示
          setTimeout(() => {
               //alert("因連線問題，變更僅保存在本機。下次登入時將同步變更。");
             }, 300);
           }
        } catch (error) {
          console.error("Error removing favorite:", error);
          card.style.opacity = "1";
          card.style.transform = "scale(1)";
        }
      }
    };

    // 比較選中房源
    // const compareSelected = () => {
    //   if (selectedItems.value.length >= 2) {
    //     // 導航到比較頁面
    //     router.push({
    //       name: "compare",
    //       query: { ids: selectedItems.value.join(",") },
    //     });
    //   }
    // };

    // 新增查看地圖方法
    const viewOnMap = () => {
      // 如果有選中特定房源，則只在地圖上顯示選中的房源
      let idsToShow =
        selectedItems.value.length > 0
          ? selectedItems.value
          : favoriteItems.value.map((item) => item.id);

      console.log("準備在地圖上顯示的房源 ID:", idsToShow);

      router.push({
        name: "map-search",
        query: {
          ids: idsToShow.join(","),
          source: "favorites",
          selected: selectedItems.value.length > 0 ? "true" : "false" 
        },
      });
    };

    // 翻頁控制
    const changePage = (page) => {
      if (page >= 1 && page <= totalPages.value) {
        currentPage.value = page;
        // 添加滾動到頁面頂部
        window.scrollTo({
          top: 0,
          behavior: "smooth",
        });
      }
    };

    // 篩選收藏項目
    const filterFavorites = () => {
      // 已由計算屬性 filteredFavorites 處理
      currentPage.value = 1; // 重置為第一頁
    };

    // 應用排序
    const applySorting = () => {
      // 已由計算屬性 sortedFavorites 處理
      currentPage.value = 1; // 重置為第一頁
    };

    // 開始自動輪播
    const startSlideShow = () => {
      // 清除之前的計時器
      stopSlideShow();

      // 只有在有選中的房源且有多張照片時才啟動輪播
      if (
        selectedProperty.value &&
        hasMultiplePhotos(selectedProperty.value) &&
        autoSlideShowEnabled.value
      ) {
        slideShowInterval.value = setInterval(() => {
          // 滾動到下一張照片
          currentPhotoIndex.value =
            (currentPhotoIndex.value + 1) %
            getPhotoCount(selectedProperty.value);
        }, slideShowDelay);
      }
    };

    // 停止自動輪播
    const stopSlideShow = () => {
      if (slideShowInterval.value) {
        clearInterval(slideShowInterval.value);
        slideShowInterval.value = null;
      }
    };

    // 上一張照片
    const prevPhoto = () => {
      if (selectedProperty.value && hasPhotos(selectedProperty.value)) {
        currentPhotoIndex.value =
          (currentPhotoIndex.value -
            1 +
            getPhotoCount(selectedProperty.value)) %
          getPhotoCount(selectedProperty.value);
      }
    };

    // 下一張照片
    const nextPhoto = () => {
      if (selectedProperty.value && hasPhotos(selectedProperty.value)) {
        currentPhotoIndex.value =
          (currentPhotoIndex.value + 1) % getPhotoCount(selectedProperty.value);
      }
    };

    // 獲取照片數量
    const getPhotoCount = (property) => {
      return property && property.房屋照片 ? property.房屋照片.length : 0;
    };

    // 是否有多張照片
    const hasMultiplePhotos = (property) => {
      return getPhotoCount(property) > 1;
    };

    // 生命週期鉤子
    onMounted(() => {
      syncFavorites();
    });

    return {
      favoriteItems,
      selectedItems,
      sortBy,
      currentPage,
      totalPages,
      pageButtons,
      filteredFavorites,
      sortedFavorites,
      paginatedFavorites,
      isSelected,
      removeFavorite,
      // compareSelected,
      viewOnMap,
      viewDetail,
      contactLandlord,
      changePage,
      goToList,
      extractMinPrice,
      getPropertyArea,
      getPropertyRooms,
      getPropertyTags,
      hasPhotos,
      getPropertyImage,
      searchQuery,
      filterFavorites,
      applySorting,
      selectedProperty,
      closePropertyDetail,
      stopSlideShow,
      startSlideShow,
      prevPhoto,
      nextPhoto,
      getPhotoCount,
      hasMultiplePhotos,
      currentPhotoIndex,
      formatPrice,
      getRoomTypeDisplay,
      getAvailableRooms,
      isLoading,
    };
  },
};
</script>

<style scoped>
/* 整體頁面結構和布局 */
.favorites-page {
  padding: 20px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

/* 載入中樣式 */
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

/* 標題和頂部工具欄樣式 */
.favorites-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.favorites-header h1 {
  font-size: 2rem;
  color: #333;
  margin: 0;
}

.favorites-tools {
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

.sort-dropdown {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-dropdown span {
  color: #666;
  font-size: 0.95rem;
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

/* .compare-btn {
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
  transition: background 0.2s;
} */

/* .compare-btn:hover:not(:disabled) {
  background: #0069d9;
}

.compare-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
} */

/* 添加新的地圖按鈕樣式 */
.map-view-btn {
  padding: 0 20px;
  background: #28a745; /* 使用綠色區分 */
  color: white;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  cursor: pointer;
  height: 42px;
  font-weight: 500;
  transition: background 0.2s;
}

.map-view-btn:hover:not(:disabled) {
  background: #218838;
}

.map-view-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.map-icon {
  display: inline-block;
  width: 18px;
  height: 18px;
  margin-right: 8px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

/* 結果摘要 */
.results-summary {
  margin-bottom: 20px;
  color: #555;
  font-size: 1rem;
}

/* 空狀態樣式 */
.favorites-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 60vh;
}

.empty-state {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  font-size: 3rem;
  margin-bottom: 15px;
}

.empty-state h2 {
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 10px;
}

.empty-state p {
  color: #666;
  margin-bottom: 20px;
}

.cta-button {
  padding: 12px 24px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.2s;
}

.cta-button:hover {
  background: #0069d9;
}

/* 卡片網格布局 */
.favorites-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

/* 卡片樣式 */
.favorite-card {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
  background: white;
  position: relative;
  transition: transform 0.3s, box-shadow 0.3s, opacity 0.3s;
}

.favorite-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.favorite-card.selected {
  border: 2px solid #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.3);
}

/* 卡片複選框樣式 */
.card-checkbox {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 2;
}

.card-checkbox input {
  display: none;
}

.card-checkbox label {
  display: block;
  width: 22px;
  height: 22px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.card-checkbox input:checked + label {
  background: #007bff;
  border-color: #007bff;
  position: relative;
}

.card-checkbox input:checked + label:after {
  content: "\2713";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
}

/* 圖片樣式 */
.card-image {
  height: 180px;
  position: relative;
  cursor: pointer;
}

.property-image {
  height: 100%;
  width: 100%;
  background-size: cover;
  background-position: center;
  background-color: #f0f0f0;
}

/* 無照片提示樣式 */
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

/* 價格標籤樣式 */
.card-price {
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

/* 取消收藏按鈕樣式 */
.remove-favorite {
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

.remove-favorite:hover {
  background: rgba(255, 255, 255, 1);
}

.heart-filled {
  width: 18px;
  height: 18px;
  background-repeat: no-repeat;
  background-position: center;
  background-size: contain;
  display: inline-block;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23ff4757'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E");
}

/* 卡片內容樣式 */
.card-content {
  padding: 15px;
}

.card-content h3 {
  margin: 0 0 10px;
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  cursor: pointer;
  line-height: 1.4;
}

.card-content h3:hover {
  color: #007bff;
}

/* 位置樣式 */
.location {
  display: flex;
  align-items: flex-start;
  color: #555;
  font-size: 0.9rem;
  margin-bottom: 12px;
  line-height: 1.5;
}

.location i {
  width: 16px;
  height: 16px;
  margin-right: 8px;
  margin-top: 3px;
  flex-shrink: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.location span {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

/* 房源亮點樣式 */
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
  width: 16px;
  height: 16px;
  margin-right: 8px;
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
}

.bed-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V7H1v10h2v-3h18v3h2V9c0-2.21-1.79-4-4-4z'/%3E%3C/svg%3E");
}

.size-icon {
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M2.5 4v3h5V4H2.5zm0 13v3h5v-3h-5zM2 9.5h8v5H2v-5zM9.5 4v3h5V4h-5zm7.5 0v3h5V4h-5zM9.5 17v3h5v-3h-5zm7.5 0v3h5v-3h-5zM14.5 9.5h8v5h-8v-5z'/%3E%3C/svg%3E");
}

.available-rooms {
  color: #28a745;
  margin-left: 5px;
  font-weight: 500;
}

/* 標籤樣式 */
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

.tag:hover {
  background: #e1f0ff;
  transform: translateY(-1px);
}

/* 操作按鈕樣式 */
.card-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 15px;
}

.view-btn,
.contact-btn {
  flex: 1;
  padding: 10px 0;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  border: none;
  text-align: center;
  transition: background 0.2s;
}

.view-btn {
  background: #f5f5f5;
  color: #333;
}

.view-btn:hover {
  background: #e5e5e5;
}

.contact-btn {
  background: #007bff;
  color: white;
}

.contact-btn:hover {
  background: #0069d9;
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

.gallery-image {
  width: 100%;
  height: 100%;
  background-size: contain;
  background-position: center;
  background-repeat: no-repeat;
  background-color: #f5f5f5;
  transition: background-image 0.3s ease;
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

.detail-address i {
  margin-right: 8px;
  width: 20px;
  height: 20px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E");
  background-size: contain;
  background-repeat: no-repeat;
  background-position: center;
  margin-top: 2px;
  flex-shrink: 0;
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

.favorite-action .heart-filled {
  margin-left: 8px;
}

/* 響應式設計 */
@media (max-width: 1200px) {
  .favorites-page {
    padding: 15px;
  }

  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 20px;
  }
}

@media (max-width: 992px) {
  .favorites-header h1 {
    font-size: 1.8rem;
  }

  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 15px;
  }

  .card-image {
    height: 160px;
  }
}

@media (max-width: 768px) {
  .favorites-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .favorites-tools {
    width: 100%;
    flex-direction: column;
    gap: 12px;
  }

  .sort-dropdown {
    width: 100%;
  }

  .sort-dropdown select {
    flex: 1;
  }

  .compare-btn {
    width: 100%;
    justify-content: center;
  }

  .favorites-grid {
    grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
  }

  .card-image {
    height: 200px;
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

  .detail-room-info {
    flex-direction: column;
    gap: 10px;
  }
}

@media (max-width: 576px) {
  .favorites-page {
    padding: 10px;
  }

  .favorites-header h1 {
    font-size: 1.4rem;
  }

  .card-image {
    height: 180px;
  }

  .card-content h3 {
    font-size: 1rem;
  }

  .pagination {
    flex-direction: row;
    padding: 0 20px;
  }

  .property-detail-modal {
    padding: 0;
  }

  .property-detail-content {
    width: 100%;
    margin: 0;
    border-radius: 0;
    height: 100%;
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
</style>
