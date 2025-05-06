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
          <button class="compare-btn" @click="compareSelected" :disabled="selectedItems.length < 2">
            比較選中項目 <span v-if="selectedItems.length">({{ selectedItems.length }})</span>
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
        <div v-for="item in sortedFavorites" :key="item.id" class="favorite-card" :class="{'selected': isSelected(item.id)}">
          <div class="card-checkbox">
            <input type="checkbox" :id="`favorite-${item.id}`" v-model="selectedItems" :value="item.id">
            <label :for="`favorite-${item.id}`"></label>
          </div>
          <div class="card-image" @click="viewDetail(item.id)">
            <img :src="item.imageUrl" :alt="item.title" />
            <span class="card-price">$ {{ item.price }} <small>/月</small></span>
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
              <span v-for="tag in item.tags" :key="tag" class="tag">{{ tag }}</span>
            </div>
            <div class="card-actions">
              <button @click="viewDetail(item.id)" class="view-btn">查看詳情</button>
              <button @click="contactLandlord(item.id)" class="contact-btn">聯繫房東</button>
            </div>
          </div>
        </div>
      </div>
  
      <div class="pagination" v-if="totalPages > 1">
        <button :disabled="currentPage === 1" @click="changePage(currentPage - 1)">上一頁</button>
        <span>{{ currentPage }} / {{ totalPages }}</span>
        <button :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">下一頁</button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue';
  import { useRouter } from 'vue-router';
  
  export default {
    name: 'FavoritesPage',
    setup() {
      const router = useRouter();
      
      // 模擬收藏數據
      const favoriteItems = ref([
        {
          id: 1,
          title: "近中央大學雙人套房",
          price: 8000,
          location: "中壢區中大路300號附近",
          area: 8,
          bedrooms: 1,
          bathrooms: 1,
          imageUrl: "https://picsum.photos/id/20/400/300",
          tags: ["靠近學校", "新裝修", "含傢俱"],
          dateAdded: new Date("2025-04-20")
        },
        {
          id: 2,
          title: "中大湖畔景觀三房",
          price: 16000,
          location: "中壢區中大路500號附近",
          area: 18,
          bedrooms: 3,
          bathrooms: 2,
          imageUrl: "https://picsum.photos/id/42/400/300",
          tags: ["湖景", "寵物友善", "近公車站"],
          dateAdded: new Date("2025-04-25")
        },
        {
          id: 3,
          title: "松濤別墅單人房",
          price: 6500,
          location: "中壢區松濤街125號",
          area: 5,
          bedrooms: 1,
          bathrooms: 1,
          imageUrl: "https://picsum.photos/id/65/400/300",
          tags: ["獨立衛浴", "安靜", "光線充足"],
          dateAdded: new Date("2025-05-01")
        }
      ]);
  
      const selectedItems = ref([]);
      const sortBy = ref('date');
      const currentPage = ref(1);
      const itemsPerPage = 6;
  
      // 排序後的收藏
      const sortedFavorites = computed(() => {
        let sorted = [...favoriteItems.value];
        
        if (sortBy.value === 'date') {
          sorted.sort((a, b) => b.dateAdded - a.dateAdded);
        } else if (sortBy.value === 'price') {
          sorted.sort((a, b) => a.price - b.price);
        } else if (sortBy.value === 'area') {
          sorted.sort((a, b) => b.area - a.area);
        }
        
        return sorted;
      });
  
      const totalPages = computed(() => 
        Math.ceil(favoriteItems.value.length / itemsPerPage)
      );
  
      const isSelected = (id) => selectedItems.value.includes(id);
  
      const removeFavorite = (id) => {
        // 實際應用中，這應該是發送請求到後端
        favoriteItems.value = favoriteItems.value.filter(item => item.id !== id);
        // 從已選項目中移除
        selectedItems.value = selectedItems.value.filter(itemId => itemId !== id);
      };
  
      const compareSelected = () => {
        if (selectedItems.value.length >= 2) {
          // 導航到比較頁面
          router.push({
            name: 'compare',
            query: { ids: selectedItems.value.join(',') }
          });
        }
      };
  
      const viewDetail = (id) => {
        // 導航到詳情頁
        router.push({
          name: 'accommodation-detail',
          params: { id }
        });
      };
  
      const contactLandlord = (id) => {
        // 模擬聯繫房東功能
        alert(`即將聯繫房源 #${id} 的房東`);
      };
  
      const changePage = (page) => {
        currentPage.value = page;
      };
  
      const goToList = () => {
        router.push({ name: 'accommodation-list' });
      };
  
      return {
        favoriteItems,
        selectedItems,
        sortBy,
        currentPage,
        totalPages,
        sortedFavorites,
        isSelected,
        removeFavorite,
        compareSelected,
        viewDetail,
        contactLandlord,
        changePage,
        goToList
      };
    }
  }
  </script>
  
  <style scoped>
  .favorites-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .favorites-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }
  
  .favorites-header h1 {
    font-size: 2rem;
    color: #333;
    margin: 0;
  }
  
  .favorites-tools {
    display: flex;
    align-items: center;
    gap: 20px;
  }
  
  .sort-by {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .sort-by span {
    font-size: 0.9rem;
    color: #666;
  }
  
  .sort-by select {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background-color: #f8f8f8;
    font-size: 0.9rem;
  }
  
  .compare-btn {
    padding: 8px 16px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }
  
  .compare-btn:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .compare-btn:not(:disabled):hover {
    background-color: #0069d9;
  }
  
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
  
  .empty-state img {
    width: 120px;
    margin-bottom: 20px;
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
    padding: 10px 20px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.2s;
  }
  
  .cta-button:hover {
    background-color: #0069d9;
  }
  
  .favorites-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
  }
  
  .favorite-card {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    background-color: white;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .favorite-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
  }
  
  .favorite-card.selected {
    border: 2px solid #007bff;
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.3);
  }
  
  .card-checkbox {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 2;
  }
  
  .card-checkbox input {
    display: none;
  }
  
  .card-checkbox label {
    display: block;
    width: 20px;
    height: 20px;
    background-color: rgba(255, 255, 255, 0.8);
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .card-checkbox input:checked + label {
    background-color: #007bff;
    border-color: #007bff;
    position: relative;
  }
  
  .card-checkbox input:checked + label:after {
    content: '\2713';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    color: white;
  }
  
  .card-image {
    position: relative;
    height: 200px;
    overflow: hidden;
    cursor: pointer;
  }
  
  .card-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s;
  }
  
  .favorite-card:hover .card-image img {
    transform: scale(1.05);
  }
  
  .card-price {
    position: absolute;
    bottom: 10px;
    left: 10px;
    background-color: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-weight: bold;
  }
  
  .card-price small {
    font-size: 0.8rem;
    font-weight: normal;
  }
  
  .remove-favorite {
    position: absolute;
    top: 10px;
    right: 10px;
    background-color: rgba(255, 255, 255, 0.8);
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .remove-favorite:hover {
    background-color: rgba(255, 0, 0, 0.2);
  }
  
  .heart-icon {
    display: inline-block;
    width: 15px;
    height: 15px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='red'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E");
    background-size: cover;
  }
  
  .card-content {
    padding: 15px;
  }
  
  .card-content h3 {
    margin: 0 0 10px 0;
    font-size: 1.2rem;
    color: #333;
    cursor: pointer;
  }
  
  .card-content h3:hover {
    color: #007bff;
  }
  
  .card-details {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 10px;
    margin-bottom: 12px;
  }
  
  .detail-item {
    display: flex;
    align-items: center;
    font-size: 0.9rem;
    color: #666;
  }
  
  .detail-item i {
    margin-right: 5px;
    width: 16px;
    height: 16px;
    background-size: contain;
    background-repeat: no-repeat;
  }
  
  .location-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z'/%3E%3C/svg%3E");
  }
  
  .area-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M21 15h2v2h-2v-2zm0-4h2v2h-2v-2zm0-4h2v2h-2V7zm-4 12h2v2h-2v-2zm0-16h2v2h-2V3zm4 0h2v2h-2V3zm-4 4h2v2h-2V7zm-4 12h2v2h-2v-2zM3 3h2v2H3V3zm0 4h18v2H3V7zm0 4h2v2H3v-2zm0 4h2v2H3v-2zm0 4h2v2H3v-2z'/%3E%3C/svg%3E");
  }
  
  .bedroom-icon {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%23666'%3E%3Cpath d='M7 13c1.66 0 3-1.34 3-3S8.66 7 7 7s-3 1.34-3 3 1.34 3 3 3zm12-6h-8v7H3V7H1v10h2v-3h18v3h2V9c0-2.21-1.79-4-4-4z'/%3E%3C/svg%3E");
  }
  
  .card-tags {
    margin-bottom: 15px;
  }
  
  .tag {
    display: inline-block;
    background-color: #f0f0f0;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
    color: #666;
    margin-right: 5px;
    margin-bottom: 5px;
  }
  
  .card-actions {
    display: flex;
    justify-content: space-between;
    gap: 10px;
  }
  
  .view-btn, .contact-btn {
    flex: 1;
    padding: 8px 0;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }
  
  .view-btn {
    background-color: #f0f0f0;
    color: #333;
  }
  
  .view-btn:hover {
    background-color: #e0e0e0;
  }
  
  .contact-btn {
    background-color: #007bff;
    color: white;
  }
  
  .contact-btn:hover {
    background-color: #0069d9;
  }
  
  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 30px;
    gap: 15px;
  }
  
  .pagination button {
    padding: 8px 16px;
    background-color: #f0f0f0;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .pagination button:disabled {
    background-color: #e0e0e0;
    color: #999;
    cursor: not-allowed;
  }
  
  .pagination button:not(:disabled):hover {
    background-color: #e0e0e0;
  }
  </style>