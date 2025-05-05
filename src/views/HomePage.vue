<template>
  <div class="home-page">
    <!-- 全屏背景視頻/圖片區 -->
    <div class="hero-section">
      <div class="overlay"></div>
      <div class="hero-content">
        <h1>中央大學校外外宿網</h1>
        <p>整合式的校外住宿資訊平台，讓你的找房體驗更輕鬆</p>
        <div class="search-container">
          <div class="search-input">
            <i class="search-icon"></i>
            <input
              type="text"
              placeholder="輸入地點、價格或房型..."
              v-model="searchQuery"
            />
          </div>
          <div class="search-button" @click="quickSearch">快速搜尋</div>
        </div>
      </div>

      <!-- 波浪形狀分隔線 -->
      <div class="wave-divider">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320">
          <path
            fill="#ffffff"
            fill-opacity="1"
            d="M0,288L48,272C96,256,192,224,288,213.3C384,203,480,213,576,229.3C672,245,768,267,864,261.3C960,256,1056,224,1152,208C1248,192,1344,192,1392,192L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"
          ></path>
        </svg>
      </div>
    </div>

    <!-- 特色版塊 -->
    <div class="features-section">
      <div class="feature-card" v-for="(feature, idx) in features" :key="idx">
        <div class="feature-icon" :class="feature.iconClass"></div>
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.description }}</p>
      </div>
    </div>

    <!-- 推薦房源輪播 -->
    <div class="featured-listings">
      <h2>精選推薦房源</h2>
      <div class="listings-carousel">
        <div
          class="listing-card"
          v-for="listing in featuredListings"
          :key="listing.id"
          @click="viewListing(listing)"
        >
          <div
            class="listing-image"
            :style="`background-image: url(${listing.photo})`"
          >
            <div class="listing-price">NT$ {{ listing.price }} / 月</div>
          </div>
          <div class="listing-content">
            <h3>{{ listing.title }}</h3>
            <div class="listing-info">
              <span
                ><i class="location-icon"></i>{{ listing.distance }}km
                至中央大學</span
              >
              <span><i class="home-type-icon"></i>{{ listing.roomType }}</span>
            </div>
            <div class="listing-rating">
              <div class="stars">
                <i
                  class="star-icon"
                  v-for="n in 5"
                  :key="n"
                  :class="n <= listing.rating ? 'filled' : ''"
                ></i>
              </div>
              <span>{{ listing.reviews }} 評價</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用者故事/見證 -->
    <div class="testimonials">
      <h2>學生使用心得</h2>
      <div class="testimonial-container">
        <div
          class="testimonial"
          v-for="(testimonial, idx) in testimonials"
          :key="idx"
        >
          <div class="testimonial-content">
            <p>"{{ testimonial.content }}"</p>
          </div>
          <div class="testimonial-author">
            <div
              class="author-avatar"
              :style="`background-image: url(${testimonial.avatar})`"
            ></div>
            <div class="author-info">
              <h4>{{ testimonial.name }}</h4>
              <p>{{ testimonial.department }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref } from "vue";
  import { useStore } from "vuex";

  export default {
    name: "HomePage",
    setup() {
      const store = useStore();
      const searchQuery = ref("");

      const features = [
        {
          title: "整合式租屋資訊",
          description: "匯集各平台的租屋資訊，統一格式便於比較",
          iconClass: "integration-icon",
        },
        {
          title: "互動式地圖搜尋",
          description: "直觀顯示房源位置、學校距離與周邊便利設施",
          iconClass: "map-icon",
        },
        {
          title: "學生評價系統",
          description: "真實住宿體驗分享，提高租屋決策透明度",
          iconClass: "review-icon",
        },
        {
          title: "防詐騙機制",
          description: "身分驗證與舉報系統，創造安全租屋環境",
          iconClass: "security-icon",
        },
      ];

      const featuredListings = [
        {
          id: 1,
          title: "中大湖畔雙人套房",
          price: 8000,
          distance: 0.8,
          roomType: "套房",
          rating: 4.5,
          reviews: 28,
          photo:
            "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        },
        {
          id: 2,
          title: "松苑學生宿舍",
          price: 6500,
          distance: 1.2,
          roomType: "雅房",
          rating: 4.2,
          reviews: 45,
          photo:
            "https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        },
        {
          id: 3,
          title: "中壢區精品公寓",
          price: 12000,
          distance: 2.5,
          roomType: "整層出租",
          rating: 4.8,
          reviews: 17,
          photo:
            "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        },
        {
          id: 4,
          title: "中央舒適單人套房",
          price: 7500,
          distance: 1.0,
          roomType: "套房",
          rating: 4.0,
          reviews: 32,
          photo:
            "https://images.unsplash.com/photo-1554995207-c18c203602cb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        },
      ];

      const testimonials = [
        {
          name: "王小明",
          department: "資訊工程學系 大三",
          avatar: "https://randomuser.me/api/portraits/men/32.jpg",
          content:
            "這平台幫我省下了很多尋找租屋的時間，介面直覺又好用，真的是學生租屋的好幫手！",
        },
        {
          name: "林小華",
          department: "企業管理學系 大四",
          avatar: "https://randomuser.me/api/portraits/women/44.jpg",
          content:
            "評價功能真的很實用，讓我避開了很多問題房源，也找到了性價比超高的房子。",
        },
        {
          name: "陳小傑",
          department: "電機工程學系 研一",
          avatar: "https://randomuser.me/api/portraits/men/67.jpg",
          content:
            "地圖搜尋功能太棒了！一眼就能看出哪些地方生活機能好，還能直接比較通勤時間。",
        },
      ];

      const quickSearch = () => {
        // 應用搜尋過濾條件
        store.commit("APPLY_FILTERS", { searchQuery: searchQuery.value });
        // 導航到租屋列表頁
        store.dispatch("navigateTo", "accommodation-list");
      };

      const viewListing = (listing) => {
        store.commit("SET_SELECTED_ACCOMMODATION", listing);
        store.dispatch("navigateTo", "accommodation-list");
      };

      return {
        searchQuery,
        features,
        featuredListings,
        testimonials,
        quickSearch,
        viewListing,
      };
    },
  };
</script>

<style scoped>
  .home-page {
    width: 100%;
    height: 100%;
    overflow-y: auto;
    scroll-behavior: smooth;
  }

  /* 英雄區塊 */
  .hero-section {
    height: 100vh;
    position: relative;
    background-image: url("https://images.unsplash.com/photo-1574362848149-11496d93a7c7?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80");
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: white;
  }

  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.7));
  }

  .hero-content {
    position: relative;
    z-index: 2;
    max-width: 800px;
    padding: 0 20px;
  }

  .hero-content h1 {
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 20px;
    text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  }

  .hero-content p {
    font-size: 1.2rem;
    margin-bottom: 30px;
    line-height: 1.6;
  }

  .search-container {
    display: flex;
    max-width: 600px;
    margin: 0 auto;
    border-radius: 50px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    overflow: hidden;
  }

  .search-input {
    flex: 1;
    position: relative;
    background: white;
  }

  .search-icon {
    position: absolute;
    top: 50%;
    left: 20px;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23999"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>');
  }

  .search-input input {
    width: 100%;
    height: 60px;
    border: none;
    padding: 0 20px 0 50px;
    font-size: 16px;
    outline: none;
  }

  .search-button {
    padding: 0 30px;
    background: linear-gradient(
      135deg,
      var(--primary-color),
      var(--secondary-color)
    );
    color: white;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .search-button:hover {
    background: linear-gradient(
      135deg,
      var(--secondary-color),
      var(--primary-color)
    );
  }

  .wave-divider {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
  }

  /* 特色版塊 */
  .features-section {
    padding: 80px 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .feature-card {
    background: white;
    padding: 30px;
    border-radius: 16px;
    box-shadow: var(--card-shadow);
    transition: all 0.3s ease;
    text-align: center;
  }

  .feature-card:hover {
    transform: translateY(-10px);
  }

  .feature-icon {
    width: 70px;
    height: 70px;
    margin: 0 auto 20px;
    border-radius: 50%;
    background: var(--light-gray);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .feature-card h3 {
    margin-bottom: 15px;
    font-size: 1.3rem;
    color: var(--primary-color);
  }

  .feature-card p {
    color: #666;
    line-height: 1.6;
  }

  /* 推薦房源輪播 */
  .featured-listings {
    padding: 80px 20px;
    background-color: var(--light-gray);
  }

  .featured-listings h2 {
    text-align: center;
    margin-bottom: 40px;
    font-size: 2rem;
    color: var(--text-color);
  }

  .listings-carousel {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding: 20px 0;
    scroll-snap-type: x mandatory;
    scrollbar-width: none;
  }

  .listings-carousel::-webkit-scrollbar {
    display: none;
  }

  .listing-card {
    flex: 0 0 320px;
    scroll-snap-align: start;
    border-radius: 16px;
    overflow: hidden;
    background: white;
    box-shadow: var(--card-shadow);
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .listing-card:hover {
    transform: translateY(-10px);
  }

  .listing-image {
    height: 200px;
    background-size: cover;
    background-position: center;
    position: relative;
  }

  .listing-price {
    position: absolute;
    bottom: 15px;
    right: 15px;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
  }

  .listing-content {
    padding: 20px;
  }

  .listing-content h3 {
    margin-bottom: 10px;
    font-size: 1.2rem;
  }

  .listing-info {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
    font-size: 14px;
    color: #666;
  }

  .listing-rating {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .stars {
    display: flex;
    gap: 2px;
  }

  .star-icon {
    width: 16px;
    height: 16px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23e0e0e0"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>');
  }

  .star-icon.filled {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23ffc107"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/></svg>');
  }

  /* 使用者故事/見證 */
  .testimonials {
    padding: 80px 20px;
  }

  .testimonials h2 {
    text-align: center;
    margin-bottom: 40px;
    font-size: 2rem;
  }

  .testimonial-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .testimonial {
    background: white;
    border-radius: 16px;
    padding: 30px;
    box-shadow: var(--card-shadow);
  }

  .testimonial-content {
    margin-bottom: 20px;
  }

  .testimonial-content p {
    font-style: italic;
    color: #555;
    line-height: 1.6;
  }

  .testimonial-author {
    display: flex;
    align-items: center;
    gap: 15px;
  }

  .author-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-size: cover;
    background-position: center;
  }

  .author-info h4 {
    margin-bottom: 5px;
    font-size: 1.1rem;
  }

  .author-info p {
    color: #666;
    font-size: 14px;
  }

  /* 響應式調整 */
  @media (max-width: 768px) {
    .hero-content h1 {
      font-size: 2.5rem;
    }

    .search-container {
      flex-direction: column;
      border-radius: 16px;
    }

    .search-input input {
      border-radius: 16px 16px 0 0;
    }

    .search-button {
      height: 50px;
      border-radius: 0 0 16px 16px;
    }
  }
</style>
