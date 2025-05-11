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
          <img :src="item.imageUrl" :alt="item.title" />
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
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        上一頁
      </button>
      <span>{{ currentPage }} / {{ totalPages }}</span>
      <button
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        下一頁
      </button>
    </div>
  </div>
</template>
  
<script>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

export default {
  name: "FavoritesPage",
  setup() {
    const router = useRouter();
    const store = useStore();

    const selectedItems = ref([]);
    const sortBy = ref("date");
    const currentPage = ref(1);
    const itemsPerPage = 6;

    // 從 Vuex 獲取收藏房源列表
    const favoriteItems = computed(() => {
      try {
        return store.getters.favoriteProperties.map((property) => ({
          id: property.編碼 || 0,
          title: property.標題 || "無標題",
          price: extractMinPrice(property.房租 || "0"),
          location: property.地址 || "地址不詳",
          area: getPropertyArea(property),
          bedrooms: getPropertyRooms(property),
          bathrooms: 1, // 假設所有房源都有1間衛浴
          imageUrl: `https://picsum.photos/id/${
            (((property.編碼 || 0) * 13) % 100) + 1000
          }/400/300`,
          tags: getPropertyTags(property),
          dateAdded: new Date(), // 由於沒有收藏時間，使用當前時間
        }));
      } catch (error) {
        console.error("Error processing favorite properties:", error);
        return [];
      }
    });

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

    const totalPages = computed(() =>
      Math.ceil(favoriteItems.value.length / itemsPerPage)
    );

    const isSelected = (id) => selectedItems.value.includes(id);

    const removeFavorite = (id) => {
      // 使用動畫效果
      const card = document.getElementById(`favorite-card-${id}`);
      if (card) {
        card.style.opacity = "0";
        card.style.transform = "scale(0.8)";

        setTimeout(() => {
          store.commit("TOGGLE_FAVORITE", id);
          selectedItems.value = selectedItems.value.filter(
            (itemId) => itemId !== id
          );
        }, 300); // 300ms 後執行刪除
      } else {
        // 如果找不到元素，直接執行
        store.commit("TOGGLE_FAVORITE", id);
        selectedItems.value = selectedItems.value.filter(
          (itemId) => itemId !== id
        );
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

    const viewDetail = (id) => {
      // 導航到詳情頁
      router.push({
        name: "accommodation-detail",
        params: { id },
      });
    };

    const contactLandlord = (id) => {
      try {
        // 獲取該房源的聯絡資訊
        const property = store.state.accommodations.find((p) => p.編碼 === id);
        if (property && property.聯絡資訊) {
          alert(`聯繫房東: ${property.聯絡資訊}`);
        } else {
          alert("無法獲取房東聯絡資訊");
        }
      } catch (error) {
        console.error("Error contacting landlord:", error);
        alert("處理請求時發生錯誤");
      }
    };

    const changePage = (page) => {
      currentPage.value = page;
    };

    const goToList = () => {
      store.commit("SET_CURRENTROUTE", "accommodation-list");
      
      router.push({ name: "accommodation-list" });
    };

    // 輔助函數: 獲取房源面積
    function getPropertyArea(property) {
      if (!property || !property.出租房數) return 0;

      let area = 0;
      try {
        if (property.出租房數.套房 && property.出租房數.套房.坪數) {
          const match = property.出租房數.套房.坪數.match(/\d+/);
          if (match) area = parseInt(match[0]);
        } else if (property.出租房數.雅房 && property.出租房數.雅房.坪數) {
          const match = property.出租房數.雅房.坪數.match(/\d+/);
          if (match) area = parseInt(match[0]);
        }
      } catch (error) {
        console.error("Error getting property area:", error);
      }

      return area || 5; // 默認面積
    }

    // 輔助函數: 獲取房間數量
    function getPropertyRooms(property) {
      if (!property || !property.出租房數) return 1;

      let rooms = 0;
      try {
        if (
          property.出租房數.套房 &&
          typeof property.出租房數.套房.總數 === "number"
        ) {
          rooms += property.出租房數.套房.總數;
        }
        if (
          property.出租房數.雅房 &&
          typeof property.出租房數.雅房.總數 === "number"
        ) {
          rooms += property.出租房數.雅房.總數;
        }
      } catch (error) {
        console.error("Error getting property rooms:", error);
      }

      return rooms || 1; // 至少一間房
    }

    // 輔助函數: 獲取房源標籤
    function getPropertyTags(property) {
      if (!property) return [];

      const tags = [];

      // 添加屋況說明為標籤 - 確保是陣列
      try {
        if (
          property.屋況說明 &&
          Array.isArray(property.屋況說明) &&
          property.屋況說明.length > 0
        ) {
          property.屋況說明.forEach((desc) => {
            if (desc && typeof desc === "string") {
              if (desc.includes("安全評核")) tags.push("安全認證");
              if (desc.includes("消防")) tags.push("消防合格");
              if (desc.includes("聯誼會")) tags.push("房東聯盟");
            }
          });
        }
      } catch (error) {
        console.error("Error processing property descriptions:", error);
      }

      // 添加設備標籤 (最多3個)
      try {
        const allEquipments = [
          ...(property.屋內設備 && Array.isArray(property.屋內設備)
            ? property.屋內設備.slice(0, 2)
            : []),
          ...(property.公共設施 && Array.isArray(property.公共設施)
            ? property.公共設施.slice(0, 1)
            : []),
        ];

        tags.push(...allEquipments);
      } catch (error) {
        console.error("Error processing property equipments:", error);
      }

      return tags.slice(0, 3); // 最多返回3個標籤
    }

    // 輔助函數: 提取最低價格
    function extractMinPrice(priceString) {
      if (!priceString || typeof priceString !== "string") return 0;

      try {
        const prices = priceString.match(/\d+/g);
        if (!prices || prices.length === 0) return 0;

        return Math.min(...prices.map((p) => parseInt(p)));
      } catch (error) {
        console.error("價格提取錯誤:", error);
        return 0;
      }
    }

    return {
      favoriteItems,
      selectedItems,
      sortBy,
      currentPage,
      totalPages,
      sortedFavorites,
      paginatedFavorites, // 添加這個
      isSelected,
      removeFavorite,
      compareSelected,
      viewDetail,
      contactLandlord,
      changePage,
      goToList,
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
  gap: 20px;
}

.pagination button {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.pagination button:not(:disabled):hover {
  background: #eee;
}

.pagination button:disabled {
  background: #f0f0f0;
  color: #aaa;
  cursor: not-allowed;
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