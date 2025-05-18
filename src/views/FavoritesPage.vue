<template>
  <div class="favorites-page">
    <div class="favorites-header">
      <h1>我的收藏</h1>
      <div class="favorites-tools">
        <div class="sort-by">
          <span>排序方式:</span>
          <select v-model="sortBy">
            <option value="date">收藏時間</option>
            <option value="price">價格</option>
            <option value="area">面積</option>
          </select>
        </div>
        <button
          class="compare-btn"
          @click="compareSelected"
          :disabled="selectedItems.length < 2"
        >
          比較選中項目
          <span v-if="selectedItems.length">({{ selectedItems.length }})</span>
        </button>
      </div>
    </div>

    <div class="favorites-empty" v-if="!favoriteItems.length">
      <div class="empty-state">
        <!-- <img src="@/assets/images/empty-heart.svg" alt="No favorites" /> -->
        <h2>您還沒有收藏任何房源</h2>
        <p>瀏覽租屋列表，點擊心形圖標收藏您感興趣的房源</p>
        <button class="cta-button" @click="goToList">瀏覽租屋列表</button>
      </div>
    </div>

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
        <div class="card-image" @click="viewDetail(item.id)">
          <img
            v-if="item.hasPhotos"
            :src="getPropertyImage(item.originalProperty)"
            :alt="item.title"
          />
          <div v-else class="no-image-placeholder">
            <div class="no-photo-notice">屋主尚未更新照片</div>
          </div>
          <span class="card-price"
            >NT$ {{ item.price.toLocaleString() }} <small>/月</small></span
          >
          <button class="remove-favorite" @click.stop="removeFavorite(item.id)">
            <i class="heart-icon"></i>
          </button>
        </div>
        <div class="card-content">
          <h3 @click="viewDetail(item.id)">{{ item.title }}</h3>
          <div class="card-details">
            <div class="detail-item">
              <i class="location-icon"></i>
              <span>{{ item.location }}</span>
            </div>
            <div class="detail-item">
              <i class="area-icon"></i>
              <span>{{ item.area }}坪</span>
            </div>
            <div class="detail-item">
              <i class="bedroom-icon"></i>
              <span>{{ item.bedrooms }}房 {{ item.bathrooms }}衛</span>
            </div>
          </div>
          <div class="card-tags">
            <span v-for="tag in item.tags" :key="tag" class="tag">{{
              tag
            }}</span>
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

    <div class="pagination" v-if="totalPages > 1">
      <button
        class="page-btn prev"
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        &laquo; 上一頁
      </button>

      <div class="page-numbers">
        <template v-for="(page, index) in pageNumbers" :key="index">
          <button
            v-if="page !== '...'"
            :class="['page-number', { active: currentPage === page }]"
            @click="changePage(page)"
          >
            {{ page }}
          </button>
          <span v-else class="page-ellipsis">{{ page }}</span>
        </template>
      </div>

      <button
        class="page-btn next"
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一頁 &raquo;
      </button>
    </div>
  </div>
</template>

<script>
  import { computed, ref, onMounted } from "vue";
  import { useRouter } from "vue-router";
  import { useStore } from "vuex";
  import { apiService } from "@/services/api";

  export default {
    name: "FavoritesPage",
    setup() {
      const router = useRouter();
      const store = useStore();

      const selectedItems = ref([]);
      const sortBy = ref("date");
      const currentPage = ref(1);
      // 修改为每頁顯示24個项目
      const itemsPerPage = 24;
      const isLoading = ref(false);

      const favoriteItems = computed(() => {
        return store.getters.favoriteProperties.map(property => ({
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
          hasPhotos: hasPhotos(property)
        }));
      });

      const syncFavorites = async () => {
        isLoading.value = true;
        try {
          // 僅嘗試與 API 同步收藏狀態，不直接設置數據
          if (store.getters.isLoggedIn) {
            await store.dispatch('syncFavorites');
          }
        } catch (error) {
          console.error("同步收藏列表失敗:", error);
        } finally {
          isLoading.value = false;
        }
      };

      // 獲取收藏列表
      const fetchFavorites = async () => {
        isLoading.value = true;
        try {
          const response =
            await apiService.accommodations.favorites.getFavorites();

          favoriteItems.value = response.map((item) => ({
            id: item.id,
            title: item.title,
            price: item.rent_price,
            location: item.address,
            area: item.area || 0,
            bedrooms: item.room_count || 1,
            bathrooms: item.bathroom_count || 1,
            tags: generateTags(item),
            dateAdded: new Date(item.created_at),
            image_url: item.image_url,
            district: item.district,
            property_type: item.property_type,
          }));
        } catch (error) {
          console.error("獲取收藏列表失敗:", error);

          favoriteItems.value = this.$store.getters.favoriteProperties.map(
            (property) => ({
              id: property.編碼 || 0,
              title: property.標題 || "無標題",
              price: this.extractMinPrice(property.房租 || "0"),
              location: property.地址 || "地址不詳",
              area: this.getPropertyArea(property),
              bedrooms: this.getPropertyRooms(property),
              bathrooms: 1,
              tags: this.getPropertyTags(property),
              dateAdded: new Date(),
              originalProperty: property,
              hasPhotos: this.hasPhotos(property),
            })
          );
        } finally {
          isLoading.value = false;
        }
      };

      // 生成標籤
      const generateTags = (item) => {
        const tags = [];
        if (item.property_type) tags.push(item.property_type);
        if (item.district) tags.push(item.district);
        if (item.area) tags.push(`${item.area}坪`);
        return tags.slice(0, 3);
      };

      // 解析最低價格 (修正 extractMinPrice undefined)
      const extractMinPrice = (priceStr) => {
        try {
          // 處理價格範圍，例如 "8000-10000"
          if (typeof priceStr === "string" && priceStr.includes("-")) {
            const prices = priceStr
              .split("-")
              .map((p) => parseInt(p.trim().replace(/[^\d]/g, "")));
            return prices[0] || 0;
          }
          // 處理單一價格，轉換為數字
          return parseInt(priceStr.toString().replace(/[^\d]/g, "")) || 0;
        } catch (error) {
          console.error("解析價格時出錯:", error);
          return 0;
        }
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

      // 獲取房源圖片 (與 AccommodationList 保持一致的實現)
      const getPropertyImage = (property) => {
        if (!property) return "";

        // 有照片時顯示真實照片
        if (
          property.房屋照片 &&
          Array.isArray(property.房屋照片) &&
          property.房屋照片.length > 0
        ) {
          // 嘗試找到不包含特殊哈希值的圖片
          for (let i = 0; i < property.房屋照片.length; i++) {
            try {
              const imageUrl = property.房屋照片[i];
              const loadedImg = require("@/" + imageUrl);

              // 使用 match 檢查是否包含特殊哈希值
              if (!loadedImg.match(/-1\.49632716/)) {
                return loadedImg;
              }
            } catch (e) {
              console.error("載入圖片失敗:", e);
              // 繼續嘗試下一張
            }
          }
        }

        // 無照片或所有照片都不符合要求時使用預設圖片
        return `https://picsum.photos/id/${
          (((property.編碼 || 0) * 13) % 100) + 1000
        }/400/300`;
      };

      // 獲取房源面積 (修正 getPropertyArea undefined)
      const getPropertyArea = (property) => {
        try {
          if (
            property.出租房數 &&
            property.出租房數.套房 &&
            property.出租房數.套房.坪數
          ) {
            return parseFloat(property.出租房數.套房.坪數) || 0;
          }
          return 0;
        } catch (error) {
          console.error("獲取面積時出錯:", error);
          return 0;
        }
      };

      // 獲取房源房間數 (修正 getPropertyRooms undefined)
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

      // 獲取房源標籤 (修正 getPropertyTags undefined)
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
        } catch (error) {
          console.error("獲取標籤時出錯:", error);
        }

        // 最多返回3個標籤
        return tags.slice(0, 3);
      };

      // 查看詳情 (修正 viewDetail undefined)
      const viewDetail = (id) => {
        router.push({
          name: "home",
          query: { propertyId: id },
        });
      };

      // 聯繫房東 (修正 contactLandlord undefined)
      const contactLandlord = (id) => {
        const property = store.getters.favoriteProperties.find(
          (p) => p.編碼 === id
        );
        if (property && property.聯絡資訊 && property.聯絡資訊.電話) {
          window.open(`tel:${property.聯絡資訊.電話}`);
        } else {
          // 如果沒有電話，返回詳情頁
          viewDetail(id);
          alert("此房源未提供聯繫電話，請查看詳情頁獲取更多聯絡方式。");
        }
      };

      // 前往租屋列表 (修正 goToList undefined)
      const goToList = () => {
        router.push({ name: "home" });
      };

      // 排序後的收藏
      const sortedFavorites = computed(() => {
        try {
          let sorted = [...favoriteItems.value];

          if (sortBy.value === "date") {
            sorted.sort((a, b) => b.dateAdded - a.dateAdded);
          } else if (sortBy.value === "price") {
            sorted.sort((a, b) => a.price - b.price);
          } else if (sortBy.value === "area") {
            sorted.sort((a, b) => b.area - a.area);
          }

          return sorted;
        } catch (error) {
          console.error("Error sorting favorites:", error);
          return [];
        }
      });

      // 分頁後的收藏項目
      const paginatedFavorites = computed(() => {
        try {
          const startIndex = (currentPage.value - 1) * itemsPerPage;
          return sortedFavorites.value.slice(
            startIndex,
            startIndex + itemsPerPage
          );
        } catch (error) {
          console.error("Error paginating favorites:", error);
          return [];
        }
      });

      // 計算總頁數，每頁24個項目
      const totalPages = computed(() =>
        Math.ceil(favoriteItems.value.length / itemsPerPage)
      );

      const isSelected = (id) => selectedItems.value.includes(id);

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
                alert("因連線問題，變更僅保存在本機。下次登入時將同步變更。");
              }, 300);
            }
          } catch (error) {
            console.error('Error removing favorite:', error);
            card.style.opacity = "1";
            card.style.transform = "scale(1)";
          }
        }
      };

      const compareSelected = () => {
        if (selectedItems.value.length >= 2) {
          // 導航到比較頁面
          router.push({
            name: "compare",
            query: { ids: selectedItems.value.join(",") },
          });
        }
      };

      // 翻頁控制
      const changePage = (page) => {
        currentPage.value = page;
        // 添加滾動到頁面頂部
        window.scrollTo({
          top: 0,
          behavior: "smooth",
        });
      };

      // 優化分頁控制，显示更多页码
      const pageNumbers = computed(() => {
        const maxPageButtons = 5; // 最多顯示的頁碼按鈕數量
        if (totalPages.value <= maxPageButtons) {
          // 如果總頁數少於等於最大按鈕數，顯示所有頁碼
          return Array.from({ length: totalPages.value }, (_, i) => i + 1);
        }

        const halfWay = Math.ceil(maxPageButtons / 2);

        // 如果當前頁碼靠近開始
        if (currentPage.value <= halfWay) {
          return [1, 2, 3, "...", totalPages.value];
        }

        // 如果當前頁碼靠近結束
        if (currentPage.value > totalPages.value - halfWay) {
          return [
            1,
            "...",
            totalPages.value - 2,
            totalPages.value - 1,
            totalPages.value,
          ];
        }

        // 當前頁碼在中間
        return [1, "...", currentPage.value, "...", totalPages.value];
      });

      onMounted(() => {
        syncFavorites();
      });

      return {
        fetchFavorites,
        favoriteItems,
        selectedItems,
        sortBy,
        currentPage,
        totalPages,
        pageNumbers,
        sortedFavorites,
        paginatedFavorites,
        isSelected,
        removeFavorite,
        compareSelected,
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
      };
    },
  };
</script>

<style scoped>
  /* 整體頁面結構和布局 */

  .favorites-page {
    padding: 20px;
    width: 100%; /* 改用 100% 替代 100vw */
    max-width: 100%; /* 改為 100% 替代 100vw */
    margin: 0;
    height: 100vh;
    box-sizing: border-box;
    overflow-y: auto;
    overflow-x: hidden;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
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

  .sort-by {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .sort-by span {
    color: #666;
    font-size: 0.95rem;
  }

  .sort-by select {
    padding: 8px 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: #fff;
    font-size: 0.9rem;
    cursor: pointer;
    height: 42px;
  }

  .compare-btn {
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
  }

  .compare-btn:hover:not(:disabled) {
    background: #0069d9;
  }

  .compare-btn:disabled {
    background: #ccc;
    cursor: not-allowed;
  }

  /* 添加圖標樣式 */
  .location-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E");
  }

  .area-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81l5-4.5M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z'/%3E%3C/svg%3E");
  }

  .bedroom-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M19 7h-8v7H3V5H1v15h2v-3h18v3h2v-9a4 4 0 0 0-4-4zm-8 10H3v-2h8v2zm10 0h-8v-2h8v2zm0-4h-8V8h8v5z'/%3E%3C/svg%3E");
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

  /* 卡片網格布局，與 AccommodationList 保持一致 */
  .favorites-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 25px;
  }

  /* 卡片樣式，與 AccommodationList 保持一致 */
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

  /* 圖片樣式，與 AccommodationList 保持一致 */
  .card-image {
    height: 180px;
    background-size: cover;
    background-position: center;
    position: relative;
    cursor: pointer;
  }

  .card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  /* 無圖片佔位符樣式 */
  .no-image-placeholder {
    width: 100%;
    height: 100%;
    background-color: #f5f5f5;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
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

  /* 價格標籤樣式，與 AccommodationList 保持一致 */
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

  /* 收藏按鈕樣式，與 AccommodationList 保持一致 */
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

  .heart-icon {
    color: #ff4757;
    font-size: 18px;
    display: inline-block;
    width: 18px;
    height: 18px;
    background-size: cover;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='red'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E");
  }

  /* 卡片內容樣式，與 AccommodationList 保持一致 */
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
  }

  .card-content h3:hover {
    color: #007bff;
  }

  /* 詳情樣式 */
  .card-details {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 12px;
    color: #666;
    font-size: 0.85rem;
  }

  .detail-item {
    display: flex;
    align-items: center;
  }

  .detail-item i {
    margin-right: 5px;
    width: 16px;
    height: 16px;
    display: inline-block;
    background-size: contain;
    background-repeat: no-repeat;
  }

  /* 標籤樣式，與 AccommodationList 保持一致 */
  .card-tags {
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
    align-items: center;
    margin-top: 30px;
    gap: 10px;
  }

  .page-btn {
    padding: 8px 15px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s;
    font-size: 0.9rem;
  }

  .page-btn:not(:disabled):hover {
    background: #f5f5f5;
  }

  .page-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .page-numbers {
    display: flex;
    gap: 8px;
    align-items: center;
  }

  .page-number {
    width: 35px;
    height: 35px;
    border-radius: 50%;
    border: 1px solid #ddd;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background: white;
    font-size: 0.9rem;
    transition: all 0.2s;
  }

  .page-number:hover:not(.active) {
    background: #f5f5f5;
  }

  .page-number.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
  }

  .page-ellipsis {
    color: #666;
    font-size: 0.9rem;
  }

  /* 響應式設計，與 AccommodationList 保持一致 */
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

    .favorites-header h1 {
      font-size: 1.6rem;
      margin-bottom: 0;
    }

    .favorites-tools {
      width: 100%;
      flex-direction: column;
      gap: 12px;
    }

    .sort-by {
      width: 100%;
    }

    .sort-by select {
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

    .card-details {
      flex-direction: column;
      gap: 8px;
    }

    .pagination {
      flex-direction: row;
      padding: 0 20px;
    }
  }

  /* 處理寬螢幕顯示 */
  @media (min-width: 1400px) {
    .favorites-grid {
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    }
    .favorites-page {
      width: 100%;
    }
  }
</style>
