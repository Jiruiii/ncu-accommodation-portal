 <template>
  <div class="home-page">
    <!-- 全屏背景視頻/圖片區 -->
    <div class="hero-section">
      <div class="overlay"></div>
      <div class="hero-content">
        <h1>中央大學校外外宿網</h1>
          <p>整合式的校外住宿資訊平台，讓你的找房體驗更輕鬆</p>
          <div class="search-container" style="border-radius: 8px;">
            <div class="search-input">
              <i class="search-icon"></i>
              <input
                type="text"
                placeholder="一站式找房，讓住宿不再煩惱"
                readonly
                style="border-radius: 0; height: 50px; cursor: default; pointer-events: none;"
              />
            </div>
            <div class="search-button" style="border-radius: 0;" @click="navigateToLogin">立即開始</div>
        </div>
      </div>
</div>

<!-- 介紹版塊 -->
<div class="intro-section">
  <div class="intro-content">
    <div class="intro-text">
      <h2>為中央大學學生解決租屋困擾</h2>
      <p>每年開學季，找房成為許多學生最大的挑戰。我們針對中央大學學生租屋痛點，提供完整解決方案。</p>
      <ul class="intro-points">
        <li><i class="check-icon"></i> 改善資訊集中與查詢效率</li>
        <li><i class="check-icon"></i> 提供即時更新與透明資訊</li>
        <li><i class="check-icon"></i> 增設評價與回饋機制</li>
        <li><i class="check-icon"></i> 集中轉租資訊降低詐騙風險</li>
      </ul>
      <button class="learn-more-btn">了解更多</button>
    </div>
  </div>
  
  <div class="solution-cards">
    <div class="solution-card">
      <div class="solution-icon verify-icon"></div>
      <h3>房源驗證制度</h3>
      <p>每個房源都經過實地訪查，確保資訊真實可靠，杜絕詐騙風險。</p>
    </div>
    <div class="solution-card">
      <div class="solution-icon compare-icon"></div>
      <h3>價格對比分析</h3>
      <p>智能分析周邊房價，讓你清楚了解市場行情，避免租金陷阱。</p>
    </div>
    <div class="solution-card">
      <div class="solution-icon community-icon"></div>
      <h3>社區評分系統</h3>
      <p>整合周邊生活機能、安全、交通等多維度評分，幫助選擇理想社區。</p>
    </div>
    <div class="solution-card">
      <div class="solution-icon support-icon"></div>
      <h3>租屋諮詢服務</h3>
      <p>提供專業租屋建議，從合約審查到糾紛處理，全程為學生把關。</p>
    </div>
  </div>
</div>

<!-- 統計資訊區 -->
<div class="stats-container" style="background-image: url('https://images.unsplash.com/photo-1518481852452-9415b262eba4?ixlib=rb-1.2.1&auto=format&fit=crop&w=1500&q=80'); background-size: cover; background-position: center; position: relative; padding: 80px 20px; min-height: 300px;">
  <div class="stats-overlay" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7);"></div>
  <div class="stat-item" style="position: relative; z-index: 2; color: white;">
    <h2>{{ clients }}</h2>
    <p>租屋用戶</p>
  </div>
  <div class="stat-item" style="position: relative; z-index: 2; color: white;">
    <h2>{{ listings }}</h2>
    <p>房源數量</p>
  </div>
  <div class="stat-item" style="position: relative; z-index: 2; color: white;">
    <h2>{{ inquiries }}</h2>
    <p>聯絡詢問次數</p>
  </div>
  <div class="stat-item" style="position: relative; z-index: 2; color: white;">
    <h2>{{ agents }}</h2>
    <p>合作房仲</p>
  </div>
</div>

<!-- 服務內容 -->
<div class="features-section">
  <div class="section-header">
    <h2 class="features-title">服務內容</h2>
    <div class="section-underline"></div>
  </div>
  <div class="feature-card" v-for="(feature, idx) in features" :key="idx">
    <div class="feature-icon" :class="feature.iconClass"></div>
    <h3>{{ feature.title }}</h3>
    <p>{{ feature.description }}</p>
  </div>
</div>

<!-- 本月精選輪播 -->
<div class="featured-listings">
  <div class="section-header">
    <h2>本月精選</h2>
    <div class="section-underline"></div>
  </div>
  
  <div class="listing-carousel-wrapper" style="position: relative; overflow: hidden; padding: 40px 0;">
    <button class="carousel-arrow prev-arrow" @click="prevListing" style="position: absolute; left: 10px; top: 50%; transform: translateY(-50%); z-index: 10;">
      <i class="arrow-icon left"></i>
    </button>
    
    <div class="listings-carousel" ref="listingContainer">
      <div
        class="listing-card"
        v-for="(listing, index) in featuredListings"
        :key="listing.id"
        @click="viewListing(listing)"
        :class="{ 'active': currentListing === index, 'prev': currentListing === (index + 1) % featuredListings.length, 'next': currentListing === (index - 1 + featuredListings.length) % featuredListings.length }"
        :style="{
          transform: getCardTransform(index),
          opacity: getCardOpacity(index),
          zIndex: getCardZIndex(index),
          transition: 'all 0.8s ease-in-out'
        }"
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
            <span><i class="location-icon"></i>{{ listing.distance }}km 至中央大學</span>
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
    
    <button class="carousel-arrow next-arrow" @click="nextListing" style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); z-index: 10;">
      <i class="arrow-icon right"></i>
    </button>
  </div>
  
  <div class="carousel-dots">
    <span 
      v-for="(_, index) in featuredListings" 
      :key="index" 
      :class="['dot', currentListing === index ? 'active' : '']"
      @click="goToListing(index)"
    ></span>
  </div>
</div>

<!-- 使用者心得 -->
<div class="testimonials">
  <div class="section-header">
    <h2>使用心得</h2>
    <div class="section-underline"></div>
  </div>
  <div class="testimonial-carousel">
    <button class="carousel-arrow prev-arrow" @click="prevTestimonial">
      <i class="arrow-icon left"></i>
    </button>
    
    <div class="testimonial-container" ref="testimonialContainer">
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
            <span class="author-role">學生</span>
          </div>
        </div>
      </div>
    </div>
    
    <button class="carousel-arrow next-arrow" @click="nextTestimonial">
      <i class="arrow-icon right"></i>
    </button>
    
    <div class="carousel-dots">
      <span 
        v-for="(_, index) in testimonials" 
        :key="index" 
        :class="['dot', currentTestimonial === index ? 'active' : '']"
        @click="goToTestimonial(index)"
      ></span>
    </div>
  </div>
</div>

<!-- 常見問題 -->
<div class="faq-section">
  <div class="section-header">
    <h2>常見問題</h2>
    <div class="section-underline"></div>
  </div>
  <div class="faq-container">
    <div 
      class="faq-item" 
      v-for="(item, index) in faqs" 
      :key="index"
      :class="{ 'active': item.isOpen }"
      @click="toggleFaq(index)"
    >
      <div class="faq-question">
        <h3>{{ item.question }}</h3>
        <div class="faq-icon"></div>
      </div>
      <div class="faq-answer" v-show="item.isOpen">
        <p>{{ item.answer }}</p>
      </div>
    </div>
  </div>
</div>

<!-- 聯絡我們 -->
<div class="contact-section">
  <div class="section-header">
    <h2>聯絡我們</h2>
    <div class="section-underline"></div>
  </div>
  
  <div class="contact-container">
    <!-- 左側：聯絡資訊 -->
    <div class="contact-info">
      <div class="info-header">
        <h3 class="info-title">聯絡資訊</h3>
      </div>
      
      <p class="contact-intro">
        有任何關於租屋、網站使用或合作提案的問題，歡迎隨時聯繫我們。
        我們的團隊將在24小時內回覆您的疑問，為您提供專業的租屋建議與協助。
      </p>
      
      <div class="contact-method">
        <div class="contact-icon">
          <i class="email-icon"></i>
        </div>
        <div class="contact-detail">
          <h4>電子郵件</h4>
          <p>accommodation@ncu.edu.tw</p>
        </div>
            </div>
            
            <div class="contact-method">
        <div class="contact-icon">
          <i class="phone-icon"></i>
        </div>
        <div class="contact-detail">
          <h4>電話</h4>
          <p>(03) 422-7151 #57282</p>
        </div>
            </div>
            
            <div class="contact-method">
        <div class="contact-icon">
          <i class="location-pin"></i>
        </div>
        <div class="contact-detail">
          <h4>地址</h4>
          <p>32001 桃園市中壢區中大路300號<br>學務處住宿服務組</p>
        </div>
            </div>
            
            <div class="contact-method">
        <div class="contact-icon">
          <i class="social-icon"></i>
        </div>
        <div class="contact-detail">
          <h4>社群媒體</h4>
          <p>@ncu_accommodation</p>
        </div>
            </div>
      
    </div>
    
    <!-- 右側：聯絡表單 -->
    <div class="contact-form-container">
      <form class="contact-form" @submit.prevent="submitForm">
        <div class="form-group">
          <label for="name">姓名</label>
          <input 
            type="text" 
            id="name" 
            v-model="contactForm.name" 
            placeholder="請輸入您的姓名" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="email">電子郵件</label>
          <input 
            type="email" 
            id="email" 
            v-model="contactForm.email" 
            placeholder="請輸入您的電子郵件" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="subject">主題</label>
          <input 
            type="text" 
            id="subject" 
            v-model="contactForm.subject" 
            placeholder="請輸入訊息主題" 
            required
          />
        </div>
        
        <div class="form-group">
          <label for="message">訊息</label>
          <textarea 
            id="message" 
            v-model="contactForm.message" 
            placeholder="請輸入您的訊息內容" 
            required
            rows="5"
          ></textarea>
        </div>
        
        <button type="submit" class="submit-btn">發送訊息</button>
      </form>
    </div>
  </div>
</div>

<!-- 頁尾 -->
</div>
</template>

<script>
  import { ref, onMounted, onUnmounted, watch, nextTick } from "vue";
  import { useStore } from "vuex";
  import { useRouter } from "vue-router";

  export default {
    name: "HomePage",
    setup() {
      const store = useStore();
      const router = useRouter();
      
      const searchQuery = ref("");
      
      // 統計資訊 (目標值)
      const clientsTarget = 232;
      const listingsTarget = 521;
      const inquiriesTarget = 1453;
      const agentsTarget = 32;
      
      // 用於動畫的ref值
      const clients = ref(0);
      const listings = ref(0);
      const inquiries = ref(0);
      const agents = ref(0);

      // 聯絡表單數據
      const contactForm = ref({
        name: "",
        email: "",
        subject: "",
        message: ""
      });

      const navigateToLogin = () => {
        router.push("/login");
      };

      // 提交聯絡表單
      const submitForm = () => {
        // 這裡可以添加表單驗證
        console.log("提交表單數據:", contactForm.value);
        
        // 成功提交後顯示提示
        alert("感謝您的訊息！我們會盡快回覆您。");
        
        // 重置表單
        contactForm.value = {
          name: "",
          email: "",
          subject: "",
          message: ""
        };
      };

      // 常見問題
      const faqs = ref([
        {
          question: "如何開始在此平台尋找房源？",
          answer: "您可以使用首頁的搜尋功能輸入關鍵詞，或直接瀏覽推薦房源。我們的地圖功能也可以幫助您依照地理位置尋找理想房源。",
          isOpen: false
        },
        {
          question: "如何確認房源資訊的真實性？",
          answer: "我們所有列出的房源都經過實地訪查與身分驗證。此外，您也可以查看其他學生對房源的評價和評分，以確保房源品質。",
          isOpen: false
        },
        {
          question: "需要支付任何費用才能使用此平台嗎？",
          answer: "不需要，本平台對中央大學學生完全免費。我們的目標是為學生提供便利的租屋資訊，不收取任何中介費或服務費。",
          isOpen: false
        },
        {
          question: "如果遇到租屋糾紛該怎麼辦？",
          answer: "我們提供租屋諮詢服務，您可以透過網站的「幫助中心」聯繫我們。我們有專業人員協助處理租屋糾紛和問題。",
          isOpen: false
        },
        {
          question: "如何與房東聯繫？",
          answer: "每個房源頁面都有「聯繫房東」按鈕，點擊後可發送訊息或查看聯繫方式。我們建議透過平台進行初步溝通，以確保安全。",
          isOpen: false
        },
        {
          question: "什麼是「學生評價系統」？",
          answer: "這是我們平台的特色功能，曾經入住的學生可以對房源進行評價和評分，包括環境、房東態度、設備等多個維度，幫助其他學生做出更明智的決定。",
          isOpen: false
        },
        {
          question: "如何舉報可疑的房源資訊？",
          answer: "在每個房源頁面底部有「舉報」按鈕，您可以選擇舉報原因並提交。我們的審核團隊會在24小時內處理您的舉報。",
          isOpen: false
        },
        {
          question: "平台上的房源資訊多久更新一次？",
          answer: "我們的系統每天都會更新房源狀態。一旦房源出租，系統會立即標記為「已出租」。我們也定期聯繫房東確認資訊的準確性。",
          isOpen: false
        }
      ]);

      // 服務內容
      const features = [
        {
          title: "租屋列表",
          description: "整合來自各平台的租屋資訊，統一格式便於比較，快速篩選合適房源。",
          iconClass: "integration-icon",
        },
        {
          title: "地圖搜尋",
          description: "直觀顯示房源位置、學校距離以及周邊便利設施，讓搜尋過程更加便捷。",
          iconClass: "map-icon",
        },
        {
          title: "我的收藏",
          description: "收藏您喜愛的房源，隨時查看並比較，快速有效做出最佳選擇。",
          iconClass: "review-icon",
        },
        {
          title: "轉租專區",
          description: "提供專屬管道集中轉租資訊，並有防詐騙機制保障您的租賃安全。",
          iconClass: "security-icon",
        },
      ];

      //本月精選
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
        {
          id: 5,
          title: "桃園區豪華雙人套房",
          price: 9800,
          distance: 3.2,
          roomType: "雙人套房",
          rating: 4.7,
          reviews: 41,
          photo:
            "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        },
        {
          id: 6,
          title: "近老街溪捷運站精裝套房",
          price: 8500,
          distance: 1.5,
          roomType: "單人套房",
          rating: 4.5,
          reviews: 37,
          photo:
            "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60",
        },
      ];

      // 本月精選輪播
      const currentListing = ref(0);
      const listingContainer = ref(null);
      const listingAutoplayInterval = ref(null);
      // 設定切換是否進行中，防止快速連續點擊
      const isTransitioning = ref(false);

      // 卡片樣式計算函數 - 調整間距讓視覺更平衡
      const getCardTransform = (index) => {
        const total = featuredListings.length;
        const currentIdx = currentListing.value;
        
        // 計算卡片相對於當前顯示卡片的位置偏移
        let diff = (index - currentIdx + total) % total;
        if (diff > total/2) diff -= total;
        
        // 根據位置偏移計算位置，縮小間距
        if (diff === 0) {
          // 當前卡片 (中心位置)
          return 'translateX(0) scale(1.1)';
        } else if (diff === 1 || diff === -total+1) {
          // 右邊卡片，縮小間距
          return 'translateX(110%) scale(0.85)';
        } else if (diff === -1 || diff === total-1) {
          // 左邊卡片，縮小間距
          return 'translateX(-110%) scale(0.85)';
        } else if (diff > 0) {
          // 右邊其他卡片 (隱藏)
          return 'translateX(220%) scale(0.7)';
        } else {
          // 左邊其他卡片 (隱藏)
          return 'translateX(-220%) scale(0.7)';
        }
      };

      // 計算卡片的透明度
      const getCardOpacity = (index) => {
        const total = featuredListings.length;
        const currentIdx = currentListing.value;
        
        // 計算最短距離
        let diff = Math.abs((index - currentIdx + total) % total);
        if (diff > total/2) diff = total - diff;
        
        if (diff === 0) return 1;  // 當前卡片
        if (diff === 1) return 0.7; // 左右相鄰卡片，提高透明度
        return 0; // 其他卡片暫時隱藏
      };

      // 計算卡片的z-index值
      const getCardZIndex = (index) => {
        const total = featuredListings.length;
        const currentIdx = currentListing.value;
        
        if (index === currentIdx) return 10; // 當前卡片最前
        
        // 計算最短距離
        let diff = Math.abs((index - currentIdx + total) % total);
        if (diff > total/2) diff = total - diff;
        
        return 10 - diff; // 距離越近，z-index越大
      };

      // 放慢切換速度，確保一致性
      const nextListing = () => {
        if (isTransitioning.value) return;
        isTransitioning.value = true;
        
        currentListing.value = (currentListing.value + 1) % featuredListings.length;
        
        // 設定切換完成後的延遲
        setTimeout(() => {
          isTransitioning.value = false;
        }, 800); // 延遲時間與CSS過渡時間相同
      };

      const prevListing = () => {
        if (isTransitioning.value) return;
        isTransitioning.value = true;
        
        currentListing.value = (currentListing.value - 1 + featuredListings.length) % featuredListings.length;
        
        // 設定切換完成後的延遲
        setTimeout(() => {
          isTransitioning.value = false;
        }, 800); // 延遲時間與CSS過渡時間相同
      };

      const goToListing = (index) => {
        if (isTransitioning.value) return;
        isTransitioning.value = true;
        
        currentListing.value = index;
        
        // 設定切換完成後的延遲
        setTimeout(() => {
          isTransitioning.value = false;
        }, 800);
      };

      // 開始自動輪播本月精選，放慢自動切換速度
      const startListingAutoplay = () => {
        stopListingAutoplay(); // 確保不會有多個計時器
        listingAutoplayInterval.value = setInterval(() => {
          if (!isTransitioning.value) {
            nextListing();
          }
        }, 5000); // 每5秒切換一次，延長停留時間
      };

      // 停止自動輪播本月精選
      const stopListingAutoplay = () => {
        if (listingAutoplayInterval.value) {
          clearInterval(listingAutoplayInterval.value);
        }
      };

      // 使用者心得
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
        {
          name: "張雅婷",
          department: "心理學系 大二",
          avatar: "https://randomuser.me/api/portraits/women/28.jpg",
          content:
            "我很喜歡這個平台的學生評價系統，能看到前租客的真實經驗分享，讓我對房源有更多了解。",
        },
        {
          name: "李俊宏",
          department: "機械工程學系 大四",
          avatar: "https://randomuser.me/api/portraits/men/22.jpg",
          content:
            "平台提供的租屋諮詢服務真的很幫助，在簽約前解答了我很多法律相關的疑問，讓我更有信心。",
        }
      ];

      // 使用者見證輪播功能
      const currentTestimonial = ref(0);
      const testimonialContainer = ref(null);
      const autoplayInterval = ref(null);

      const nextTestimonial = () => {
        if (currentTestimonial.value < testimonials.length - 1) {
          currentTestimonial.value++;
        } else {
          currentTestimonial.value = 0;
        }
        scrollToTestimonial(currentTestimonial.value);
      };

      const prevTestimonial = () => {
        if (currentTestimonial.value > 0) {
          currentTestimonial.value--;
        } else {
          currentTestimonial.value = testimonials.length - 1;
        }
        scrollToTestimonial(currentTestimonial.value);
      };

      const goToTestimonial = (index) => {
        currentTestimonial.value = index;
        scrollToTestimonial(index);
      };

      const scrollToTestimonial = (index) => {
        if (testimonialContainer.value) {
          const scrollAmount = testimonialContainer.value.clientWidth * index;
          testimonialContainer.value.scrollTo({
            left: scrollAmount,
            behavior: 'smooth'
          });
        }
      };

      // 開始自動輪播
      const startAutoplay = () => {
        stopAutoplay(); // 確保不會有多個計時器
        autoplayInterval.value = setInterval(() => {
          nextTestimonial();
        }, 5000); // 每5秒切換一次
      };

      // 停止自動輪播
      const stopAutoplay = () => {
        if (autoplayInterval.value) {
          clearInterval(autoplayInterval.value);
        }
      };

      // 監聽當前testimonial變化，確保正確滾動
      watch(currentTestimonial, (newVal) => {
        scrollToTestimonial(newVal);
      });

      // 設置懸停時暫停輪播，離開時恢復輪播
      onMounted(() => {
        startAutoplay();
        startListingAutoplay();
        
        // 為使用者心得容器添加懸停事件
        if (testimonialContainer.value) {
          testimonialContainer.value.addEventListener('mouseenter', stopAutoplay);
          testimonialContainer.value.addEventListener('mouseleave', startAutoplay);
        }
        
        // 為本月精選容器添加懸停事件
        if (listingContainer.value) {
          listingContainer.value.addEventListener('mouseenter', stopListingAutoplay);
          listingContainer.value.addEventListener('mouseleave', startListingAutoplay);
        }
      });
      
      // 組件卸載時清理
      onUnmounted(() => {
        stopAutoplay();
        stopListingAutoplay();
        
        // 移除事件監聽器
        if (testimonialContainer.value) {
          testimonialContainer.value.removeEventListener('mouseenter', stopAutoplay);
          testimonialContainer.value.removeEventListener('mouseleave', startAutoplay);
        }
        
        if (listingContainer.value) {
          listingContainer.value.removeEventListener('mouseenter', stopListingAutoplay);
          listingContainer.value.removeEventListener('mouseleave', startListingAutoplay);
        }
      });

      // FAQ切換功能
      const toggleFaq = (index) => {
        faqs.value[index].isOpen = !faqs.value[index].isOpen;
      };

      // 數字動畫函數
      const animateCount = (target, current, setter) => {
        const duration = 2000; // 動畫總時間(毫秒)
        const steps = 50; // 動畫總步數
        const stepTime = duration / steps; // 每步的時間
        const increment = target / steps; // 每步增加的數值
        let currentStep = 0;
        
        const timer = setInterval(() => {
          currentStep++;
          if (currentStep >= steps) {
            setter(target);
            clearInterval(timer);
          } else {
            setter(Math.round(increment * currentStep));
          }
        }, stepTime);
      };

      // 觀察器，當元素進入視野時觸發動畫
      const observeStats = () => {
        const observer = new IntersectionObserver((entries) => {
          entries.forEach(entry => {
            if (entry.isIntersecting) {
              // 開始動畫
              animateCount(clientsTarget, clients.value, val => clients.value = val);
              animateCount(listingsTarget, listings.value, val => listings.value = val);
              animateCount(inquiriesTarget, inquiries.value, val => inquiries.value = val);
              animateCount(agentsTarget, agents.value, val => agents.value = val);
              // 只觸發一次
              observer.disconnect();
            }
          });
        }, { threshold: 0.1 });

        // 觀察統計區域
        setTimeout(() => {
          const statsElement = document.querySelector('.stats-container');
          if (statsElement) observer.observe(statsElement);
        }, 100);
      };

      // 在組件掛載後設置觀察器
      onMounted(() => {
        observeStats();
        // 確保容器已經掛載後才能操作
        nextTick(() => {
          // 初始化輪播，設置第一個testimonial的位置
          if (testimonialContainer.value) {
            testimonialContainer.value.scrollLeft = 0;
          }
        });
      });

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
        currentTestimonial,
        testimonialContainer,
        nextTestimonial,
        prevTestimonial,
        navigateToLogin,
        goToTestimonial,
        // 本月精選輪播
        currentListing,
        listingContainer,
        nextListing,
        prevListing,
        goToListing,
        getCardTransform,
        getCardOpacity,
        getCardZIndex,
        quickSearch,
        viewListing,
        isTransitioning,
        // 統計資訊 (動態值)
        clients,
        listings,
        inquiries,
        agents,
        // FAQs
        faqs,
        toggleFaq,
        // 聯絡表單
        contactForm,
        submitForm
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

  /* 介紹版塊 */
  .intro-section {
    padding: 80px 20px;
    background-color: #f9f9f9;
    display: flex;
    flex-wrap: wrap;
    max-width: 1200px;
    margin: 0 auto;
    gap: 30px;
  }

  .intro-content {
    flex: 1 1 400px;
    display: flex;
    align-items: center;
  }

  .intro-text {
    max-width: 100%;
  }

  .intro-text h2 {
    font-size: 2.2rem;
    margin-bottom: 20px;
    color: var(--primary-color);
    font-weight: 700;
  }

  .intro-text p {
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 25px;
    color: #555;
  }

  .intro-points {
    list-style: none;
    padding: 0;
    margin-bottom: 30px;
  }

  .intro-points li {
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    font-size: 1.05rem;
    color: #444;
  }

  .check-icon {
    display: inline-block;
    width: 22px;
    height: 22px;
    margin-right: 10px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234CAF50"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>');
    background-size: contain;
  }

  .learn-more-btn {
    padding: 12px 28px;
    background: var(--primary-color);
    color: white;
    border: none;
    border-radius: 30px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  }

  .learn-more-btn:hover {
    background: var(--secondary-color);
    transform: translateY(-3px);
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  }

  .solution-cards {
    flex: 1 1 600px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 25px;
  }

  .solution-card {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
  }

  .solution-card:hover {
    transform: translateY(-8px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.12);
  }

  .solution-icon {
    width: 60px;
    height: 60px;
    margin-bottom: 20px;
    border-radius: 50%;
    background-color: rgba(var(--primary-rgb), 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .verify-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234CAF50"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm-2 16l-4-4 1.41-1.41L10 14.17l6.59-6.59L18 9l-8 8z"/></svg>');
    background-size: 32px;
    background-position: center;
    background-repeat: no-repeat;
  }

  .compare-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232196F3"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>');
    background-size: 32px;
    background-position: center;
    background-repeat: no-repeat;
  }

  .community-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FF9800"><path d="M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zm-8 0c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zm0 2c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zm8 0c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z"/></svg>');
    background-size: 32px;
    background-position: center;
    background-repeat: no-repeat;
  }

  .support-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%239C27B0"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>');
    background-size: 32px;
    background-position: center;
    background-repeat: no-repeat;
  }

  .solution-card h3 {
    font-size: 1.2rem;
    margin-bottom: 15px;
    color: var(--primary-color);
  }

  .solution-card p {
    font-size: 0.95rem;
    line-height: 1.6;
    color: #666;
  }

  @media (max-width: 992px) {
    .intro-section {
      flex-direction: column;
    }
    
    .solution-cards {
      grid-template-columns: repeat(2, 1fr);
    }
  }

  @media (max-width: 576px) {
    .solution-cards {
      grid-template-columns: 1fr;
    }
  }

  /* 服務內容版塊 */
  .features-section {
    padding: 80px 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .section-header {
    grid-column: 1 / -1;
    text-align: center;
    margin-bottom: 40px;
    position: relative;
  }

  .features-title {
    font-size: 2rem;
    color: var(--text-color);
    font-weight: 700;
    margin-bottom: 15px;
  }

  .section-underline {
    width: 80px;
    height: 4px;
    background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
    border-radius: 2px;
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
    background: rgba(var(--primary-rgb), 0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    background-size: 35px;
    background-position: center;
    background-repeat: no-repeat;
  }

  .integration-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%234CAF50"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-7-2h2V7h-4v2h2z"/></svg>');
  }

  .map-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232196F3"><path d="M20.5 3l-.16.03L15 5.1 9 3 3.36 4.9c-.21.07-.36.25-.36.48V20.5c0 .28.22.5.5.5l.16-.03L9 18.9l6 2.1 5.64-1.9c.21-.07.36-.25.36-.48V3.5c0-.28-.22-.5-.5-.5zM15 19l-6-2.11V5l6 2.11V19z"/></svg>');
  }

  .review-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FF9800"><path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/><path d="M0 0h24v24H0z" fill="none"/></svg>');
  }

  .security-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%239C27B0"><path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z"/></svg>');
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

  /* 本月精選板塊 */
  .featured-listings {
    padding: 80px 20px;
    background-color: var(--light-gray);
    max-width: 1200px;
    margin: 0 auto;
  }

  .featured-listings .section-header {
    margin-bottom: 40px;
  }

  .featured-listings h2 {
    font-size: 2rem;
    color: var(--text-color);
    font-weight: 700;
    margin-bottom: 15px;
  }

  .listing-carousel-wrapper {
    position: relative;
    width: 100%;
    overflow: hidden;
    margin: 0 auto;
  }

  .listings-carousel {
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
    height: 420px;
    perspective: 1000px;
  }

  .listing-card {
    border-radius: 16px;
    overflow: hidden;
    background: white;
    box-shadow: var(--card-shadow);
    position: absolute;
    width: 320px;
    height: 350px;
    transition: all 0.8s ease-in-out;
    cursor: pointer;
  }

  .listing-card.active {
    transform: translateX(0) scale(1.1);
    opacity: 1;
    z-index: 10;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  }

  .listing-card.prev {
    transform: translateX(-120%) scale(0.85);
    opacity: 0.7;
    z-index: 5;
  }

  .listing-card.next {
    transform: translateX(120%) scale(0.85);
    opacity: 0.7;
    z-index: 5;
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

  .carousel-arrow {
    border: none;
    background-color: white;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
    z-index: 20;
    transition: all 0.3s ease;
  }

  .carousel-arrow:hover {
    background-color: var(--primary-color);
  }

  .carousel-arrow:hover .arrow-icon {
    border-color: white;
  }

  .carousel-dots {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 20px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #ddd;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .dot.active {
    background-color: var(--primary-color);
    transform: scale(1.3);
  }

  /* 使用者心得板塊 */
  .testimonials {
    padding: 80px 20px;
    background-color: #f9f9f9;
    position: relative;
  }

  .testimonials h2 {
    text-align: center;
    margin-bottom: 15px;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
  }

  .testimonial-carousel {
    position: relative;
    max-width: 1000px;
    margin: 0 auto;
    padding: 20px 0;
  }

  .testimonial-container {
    display: flex;
    overflow: hidden;
    scroll-behavior: smooth;
    margin: 0 auto;
    width: 100%;
  }

  .testimonial {
    min-width: 100%;
    flex: 0 0 auto;
    background: white;
    border-radius: 16px;
    padding: 35px;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
    transition: all 0.5s ease;
    text-align: center;
    box-sizing: border-box;
  }

  .testimonial-content {
    margin-bottom: 25px;
  }

  .testimonial-content p {
    font-style: italic;
    color: #555;
    line-height: 1.7;
    font-size: 1.1rem;
  }

  .testimonial-author {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 15px;
  }

  .author-avatar {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background-size: cover;
    background-position: center;
    border: 3px solid var(--primary-color);
    box-shadow: 0 5px 10px rgba(0, 0, 0, 0.1);
  }

  .author-info {
    text-align: center;
  }

  .author-info h4 {
    margin-bottom: 5px;
    font-size: 1.2rem;
    color: var(--primary-color);
  }

  .author-info p {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 5px;
  }

  .author-role {
    display: inline-block;
    background-color: rgba(var(--primary-rgb), 0.1);
    color: var(--primary-color);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
  }

  .carousel-arrow {
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background-color: white;
    border: none;
    cursor: pointer;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
  }

  .carousel-arrow:hover {
    background-color: var(--primary-color);
  }

  .carousel-arrow:hover .arrow-icon {
    border-color: white;
  }

  .prev-arrow {
    left: 10px;
  }

  .next-arrow {
    right: 10px;
  }

  .arrow-icon {
    width: 12px;
    height: 12px;
    border-top: 2px solid #666;
    border-right: 2px solid #666;
    transition: border-color 0.3s ease;
  }

  .arrow-icon.left {
    transform: rotate(-135deg);
  }

  .arrow-icon.right {
    transform: rotate(45deg);
  }

  .carousel-dots {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 25px;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background-color: #ddd;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .dot.active {
    background-color: var(--primary-color);
    transform: scale(1.3);
  }

  @media (max-width: 768px) {
    .testimonials {
      padding: 60px 15px;
    }
    
    .testimonial-carousel {
      padding: 10px 0;
      width: calc(100% - 20px);
      margin: 0 auto;
    }
    
    .testimonial {
      padding: 25px 15px;
      border-radius: 12px;
      min-width: 100%;
      width: 100%;
    }
    
    .testimonial-content p {
      font-size: 0.95rem;
      line-height: 1.6;
    }
    
    .testimonial-author {
      gap: 10px;
    }
    
    .author-avatar {
      width: 60px;
      height: 60px;
    }
    
    .author-info h4 {
      font-size: 1.1rem;
    }
    
    .author-info p {
      font-size: 0.85rem;
    }
    
    .carousel-arrow {
      width: 36px;
      height: 36px;
    }
  }

  @media (max-width: 480px) {
    .testimonials h2 {
      font-size: 1.7rem;
    }
    
    .testimonial-carousel {
      width: 100%;
    }
    
    .testimonial {
      padding: 20px 12px;
      width: 100%;
    }
    
    .testimonial-content p {
      font-size: 0.9rem;
    }
    
    .author-avatar {
      width: 50px;
      height: 50px;
    }
    
    .author-info h4 {
      font-size: 1rem;
    }
    
    .prev-arrow {
      left: 5px;
    }
    
    .next-arrow {
      right: 5px;
    }
    
    .carousel-arrow {
      width: 32px;
      height: 32px;
      background-color: rgba(255, 255, 255, 0.9);
    }
  }

  /* 常見問題 */
  .faq-section {
    padding: 80px 20px;
    max-width: 1000px;
    margin: 0 auto;
  }

  .faq-section h2 {
    text-align: center;
    margin-bottom: 15px;
    font-size: 2rem;
    color: var(--text-color);
    font-weight: 700;
  }

  .faq-container {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 40px;
  }

  .faq-item {
    background: white;
    border-radius: 10px;
    box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    transition: all 0.3s ease;
  }

  .faq-item.active {
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  }

  .faq-question {
    padding: 20px 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    background-color: white;
    transition: background-color 0.3s ease;
  }

  .faq-item:hover .faq-question {
    background-color: #f8f8f8;
  }

  .faq-item.active .faq-question {
    border-bottom: 1px solid #eee;
  }

  .faq-question h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: #333;
    margin: 0;
  }

  .faq-icon {
    width: 20px;
    height: 20px;
    position: relative;
    transition: transform 0.3s ease;
  }

  .faq-icon:before, .faq-icon:after {
    content: '';
    position: absolute;
    background-color: var(--primary-color);
    transition: all 0.3s ease;
  }

  .faq-icon:before {
    width: 100%;
    height: 2px;
    top: 50%;
    left: 0;
    transform: translateY(-50%);
  }

  .faq-icon:after {
    width: 2px;
    height: 100%;
    left: 50%;
    top: 0;
    transform: translateX(-50%);
  }

  .faq-item.active .faq-icon:after {
    transform: translateX(-50%) rotate(90deg);
    opacity: 0;
  }

  .faq-answer {
    padding: 0 25px 20px;
    line-height: 1.6;
    color: #666;
    font-size: 1rem;
  }

  .faq-answer p {
    margin: 0;
    padding-top: 15px;
  }

  @media (max-width: 768px) {
    .faq-section {
      padding: 60px 15px;
    }
    
    .faq-question {
      padding: 15px 20px;
    }
    
    .faq-question h3 {
      font-size: 1rem;
    }
    
    .faq-answer {
      padding: 0 20px 15px;
      font-size: 0.95rem;
    }
  }
  /* 聯絡我們 */
  .contact-section {
    padding: 80px 20px;
    background-color: #f9f9f9;
    max-width: 1200px;
    margin: 0 auto;
  }

  .contact-section h2 {
    text-align: center;
    font-size: 2rem;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 15px;
  }

  .contact-container {
    display: flex;
    margin-top: 40px;
    flex-wrap: wrap;
    gap: 30px;
  }

  .contact-info {
    flex: 1 1 350px;
    padding: 30px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }

  .info-header {
    text-align: left;
    margin-bottom: 20px;
  }

  .info-title {
    font-size: 1.8rem;
    color: var(--primary-color);
    font-weight: 700;
    margin-bottom: 10px;
  }

  .contact-intro {
    font-size: 0.95rem;
    color: #777;
    margin-bottom: 30px;
    line-height: 1.6;
  }

  .contact-method {
    display: flex;
    align-items: center;
    margin-bottom: 25px;
    cursor: pointer;
    transition: transform 0.3s ease;
  }

  .contact-method:hover {
    transform: translateX(5px);
  }

  .contact-icon {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background-color: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 15px;
    flex-shrink: 0;
    transition: all 0.3s ease;
  }

  .contact-method:hover .contact-icon {
    background-color: var(--primary-color);
    transform: scale(1.1);
    box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
  }

  .contact-method:hover .email-icon,
  .contact-method:hover .phone-icon,
  .contact-method:hover .location-pin,
  .contact-method:hover .social-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FFFFFF"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>');
  }

  .email-icon {
    display: inline-block;
    width: 24px;
    height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232196F3"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg>');
    background-size: contain;
    transition: all 0.3s ease;
  }

  .phone-icon {
    display: inline-block;
    width: 24px;
    height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232196F3"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>');
    background-size: contain;
    transition: all 0.3s ease;
  }

  .contact-method:hover .phone-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FFFFFF"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>');
  }

  .location-pin {
    display: inline-block;
    width: 24px;
    height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232196F3"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>');
    background-size: contain;
    transition: all 0.3s ease;
  }

  .contact-method:hover .location-pin {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FFFFFF"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/></svg>');
  }

  .social-icon {
    display: inline-block;
    width: 24px;
    height: 24px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%232196F3"><path d="M12 2.04c-5.5 0-10 4.49-10 10.02 0 5 3.66 9.15 8.44 9.9v-7H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.89 3.78-3.89 1.09 0 2.23.19 2.23.19v2.47h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.45 2.9h-2.33v7a10 10 0 0 0 8.44-9.9c0-5.53-4.5-10.02-10-10.02z"/></svg>');
    background-size: contain;
    transition: all 0.3s ease;
  }

  .contact-method:hover .social-icon {
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23FFFFFF"><path d="M12 2.04c-5.5 0-10 4.49-10 10.02 0 5 3.66 9.15 8.44 9.9v-7H7.9v-2.9h2.54V9.85c0-2.51 1.49-3.89 3.78-3.89 1.09 0 2.23.19 2.23.19v2.47h-1.26c-1.24 0-1.63.77-1.63 1.56v1.88h2.78l-.45 2.9h-2.33v7a10 10 0 0 0 8.44-9.9c0-5.53-4.5-10.02-10-10.02z"/></svg>');
  }

  .contact-detail {
    flex: 1;
  }

  .contact-detail h4 {
    font-size: 1.1rem;
    margin-bottom: 5px;
    color: var(--primary-color);
    transition: all 0.3s ease;
  }

  .contact-method:hover .contact-detail h4 {
    color: var(--secondary-color);
    transform: translateY(-2px);
  }

  .contact-detail p {
    color: #666;
    line-height: 1.5;
    transition: color 0.3s ease;
  }

  .contact-method:hover .contact-detail p {
    color: #333;
  }

  .contact-form-container {
    flex: 1 1 450px;
    background: white;
    border-radius: 16px;
    padding: 30px;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }

  .contact-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .form-group {
    display: flex;
    flex-direction: column;
  }

  .form-group label {
    margin-bottom: 8px;
    font-weight: 600;
    color: #444;
  }

  .form-group input,
  .form-group textarea {
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
  }

  .form-group input:focus,
  .form-group textarea:focus {
    border-color: var(--primary-color);
    outline: none;
  }

  .submit-btn {
    background: var(--primary-color);
    color: white;
    border: none;
    padding: 14px 25px;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 10px;
    align-self: flex-start;
  }

  .submit-btn:hover {
    background: var(--secondary-color);
    transform: translateY(-3px);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }

  @media (max-width: 768px) {
    .contact-container {
      flex-direction: column;
    }
    
    .contact-form-container,
    .contact-info {
      width: 100%;
    }
  }


  /* 統計數字*/
  .stats-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 30px;
    width: 100%;
    margin: 40px 0;
    padding: 60px 20px;
    background-color: #f4f4f4;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    text-align: center;
  }

  .stat-item {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    flex: 0 1 150px;
    margin: 0 20px;
  }

  .stat-item h2 {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 10px;
    color: #ffffff;
  }

  .stat-item p {
    font-size: 1.2rem;
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
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
    
    /* Hide stats container on mobile */
    .stats-container {
      display: none;
    }
  }

  
</style>