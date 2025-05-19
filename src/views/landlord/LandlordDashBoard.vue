<template>
    <div class="dashboard-container">
      <div class="dashboard-header">
        <h1>房東管理中心</h1>
        <div class="status-indicator" :class="verificationStatusClass">
          <span class="status-dot"></span>
          <span>{{ verificationStatusText }}</span>
        </div>
      </div>
  
      <!-- 認證提醒區塊 - 只在未認證或認證中時顯示 -->
      <div v-if="!isVerified" class="verification-reminder">
        <div class="reminder-content">
          <div class="reminder-icon">
            <i class="fa-solid fa-certificate" v-if="verificationStatus === 'pending'"></i>
            <i class="fa-solid fa-id-card" v-else></i>
          </div>
          <div class="reminder-text">
            <h3>{{ verificationStatus === 'pending' ? '房東認證審核中' : '完成房東認證' }}</h3>
            <p v-if="verificationStatus === 'pending'">
              您的房東認證申請正在審核中，審核通過後即可發布房源。
            </p>
            <p v-else>
              完成房東認證以獲得發布房源、管理租約等特權。認證過程只需幾分鐘。
            </p>
          </div>
          <div class="reminder-action">
            <button
              v-if="verificationStatus === 'pending'"
              class="status-btn"
              @click="checkVerificationStatus"
            >
              查看進度
            </button>
            <router-link
              v-else
              to="/landlord/verification"
              class="verify-btn"
            >
              立即認證
            </router-link>
          </div>
        </div>
      </div>
  
      <!-- 統計數據卡片 -->
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fa-solid fa-home"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.totalProperties }}</h3>
            <p>房源總數</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fa-solid fa-eye"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.totalViews }}</h3>
            <p>總瀏覽量</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fa-solid fa-message"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.newMessages }}</h3>
            <p>新訊息</p>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <i class="fa-solid fa-star"></i>
          </div>
          <div class="stat-content">
            <h3>{{ stats.averageRating }}</h3>
            <p>平均評分</p>
          </div>
        </div>
      </div>
  
      <!-- 主要功能區塊 -->
      <div class="dashboard-main">
        <!-- 房源管理 -->
        <div class="dashboard-section">
          <div class="section-header">
            <h2>我的房源</h2>
            <button
              class="add-btn"
              @click="navigateTo('/landlord/properties/new')"
              :disabled="!isVerified"
            >
              <i class="fa-solid fa-plus"></i> 新增房源
            </button>
          </div>
          
          <div v-if="properties.length > 0" class="property-list">
            <div v-for="property in properties" :key="property.id" class="property-card">
              <div class="property-image">
                <!-- <img :src="property.image || require('@/assets/default-property.jpg')" :alt="property.title"> -->
                <div class="property-badge" :class="property.status">{{ getStatusText(property.status) }}</div>
              </div>
              <div class="property-content">
                <h3>{{ property.title }}</h3>
                <p class="property-address">
                  <i class="fa-solid fa-location-dot"></i> {{ property.address }}
                </p>
                <div class="property-info">
                  <span><i class="fa-solid fa-dollar-sign"></i> {{ property.price }} 元/月</span>
                  <span><i class="fa-solid fa-eye"></i> {{ property.views }} 次瀏覽</span>
                </div>
                <div class="property-actions">
                  <button @click="editProperty(property.id)" class="action-btn edit">
                    <i class="fa-solid fa-edit"></i> 編輯
                  </button>
                  <button @click="togglePropertyStatus(property.id)" class="action-btn" :class="property.status === 'active' ? 'deactivate' : 'activate'">
                    <i :class="property.status === 'active' ? 'fa-solid fa-ban' : 'fa-solid fa-check'"></i>
                    {{ property.status === 'active' ? '下架' : '上架' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <div class="empty-icon">
              <i class="fa-solid fa-home"></i>
            </div>
            <h3>暫無房源</h3>
            <p>您還未發布任何房源，立即新增您的第一個房源！</p>
            <button
              class="add-btn large"
              @click="navigateTo('/landlord/properties/new')"
              :disabled="!isVerified"
            >
              <i class="fa-solid fa-plus"></i> 新增房源
            </button>
            <p v-if="!isVerified" class="empty-hint">
              請先完成房東認證才能發布房源
            </p>
          </div>
        </div>
  
        <!-- 最新訊息 -->
        <div class="dashboard-section">
          <div class="section-header">
            <h2>最新訊息</h2>
            <button class="view-all-btn" @click="navigateTo('/landlord/messages')">
              查看全部
            </button>
          </div>
          
          <div v-if="messages.length > 0" class="message-list">
            <div v-for="message in messages" :key="message.id" class="message-item">
              <div class="message-avatar">
                <img :src="message.senderAvatar || require('@/assets/default-avatar.jpg')" :alt="message.senderName">
              </div>
              <div class="message-content">
                <div class="message-header">
                  <span class="message-sender">{{ message.senderName }}</span>
                  <span class="message-time">{{ formatTime(message.time) }}</span>
                </div>
                <p class="message-property">關於：{{ message.propertyTitle }}</p>
                <p class="message-text">{{ message.content }}</p>
              </div>
            </div>
          </div>
          
          <div v-else class="empty-state">
            <div class="empty-icon">
              <i class="fa-solid fa-message"></i>
            </div>
            <h3>暫無訊息</h3>
            <p>目前沒有任何新訊息。</p>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
  import apiService from '@/services/api';
  
  export default {
    name: 'LandlordDashboard',
    setup() {
      const router = useRouter();
      
      // 房東認證狀態
      const verificationStatus = ref('none'); // none, pending, approved, rejected
      
      // 計算認證狀態文字和CSS類別
      const verificationStatusText = computed(() => {
        switch (verificationStatus.value) {
          case 'approved': return '已認證';
          case 'pending': return '審核中';
          case 'rejected': return '審核未通過';
          default: return '未認證';
        }
      });
      
      const verificationStatusClass = computed(() => {
        switch (verificationStatus.value) {
          case 'approved': return 'verified';
          case 'pending': return 'pending';
          case 'rejected': return 'rejected';
          default: return 'unverified';
        }
      });
      
      const isVerified = computed(() => verificationStatus.value === 'approved');
      
      // 統計數據
      const stats = reactive({
        totalProperties: 0,
        totalViews: 0,
        newMessages: 0,
        averageRating: '0.0',
      });
      
      // 房源列表
      const properties = ref([]);
      
      // 訊息列表
      const messages = ref([]);
      
      // 獲取房東狀態和數據
      const fetchLandlordData = async () => {
        try {
          const response = await apiService.landlord.getDashboard();
          
          if (response) {
            // 更新認證狀態
            verificationStatus.value = response.verificationStatus || 'none';
            
            // 更新統計數據
            stats.totalProperties = response.stats?.totalProperties || 0;
            stats.totalViews = response.stats?.totalViews || 0;
            stats.newMessages = response.stats?.newMessages || 0;
            stats.averageRating = response.stats?.averageRating || '0.0';
            
            // 更新房源列表
            properties.value = response.properties || [];
            
            // 更新訊息列表
            messages.value = response.messages || [];
          }
        } catch (error) {
          console.error('獲取房東數據失敗:', error);
          // 使用模擬數據進行展示
          setupMockData();
        }
      };
      
      // 模擬數據（用於開發和演示）
      const setupMockData = () => {
        verificationStatus.value = 'approved';
        
        stats.totalProperties = 3;
        stats.totalViews = 157;
        stats.newMessages = 2;
        stats.averageRating = '4.7';
        
        properties.value = [
          {
            id: 1,
            title: '中央大學旁舒適套房',
            address: '桃園市中壢區五權里1鄰中大路300號',
            price: 6800,
            views: 87,
            status: 'active',
            image: 'https://i.imgur.com/9NHUoKK.jpg'
          },
          {
            id: 2,
            title: '近中壢夜市雙人套房',
            address: '桃園市中壢區實踐路101號',
            price: 8500,
            views: 45,
            status: 'inactive',
            image: 'https://i.imgur.com/Gj4rtAY.jpg'
          },
          {
            id: 3,
            title: '精緻樓中樓獨立衛浴',
            address: '桃園市中壢區五權里中大路77號',
            price: 7200,
            views: 25,
            status: 'active',
            image: 'https://i.imgur.com/RSA2kVr.jpg'
          }
        ];
        
        messages.value = [
          {
            id: 1,
            senderName: '王小明',
            senderAvatar: 'https://i.pravatar.cc/150?img=32',
            propertyTitle: '中央大學旁舒適套房',
            content: '您好，我想詢問房間是否還有空房？另外想了解一下房租包含水電嗎？',
            time: new Date(new Date().getTime() - 30 * 60000)
          },
          {
            id: 2,
            senderName: '李佳芸',
            senderAvatar: 'https://i.pravatar.cc/150?img=44',
            propertyTitle: '精緻樓中樓獨立衛浴',
            content: '房東您好，我是中央大學的學生，想詢問可以什麼時候去看房？',
            time: new Date(new Date().getTime() - 5 * 3600000)
          }
        ];
      };
      
      // 頁面導航
      const navigateTo = (path) => {
        router.push(path);
      };
      
      // 編輯房源
      const editProperty = (id) => {
        router.push(`/landlord/properties/${id}/edit`);
      };
      
      // 切換房源狀態（上/下架）
      const togglePropertyStatus = async (id) => {
        try {
          const property = properties.value.find(p => p.id === id);
          if (!property) return;
          
          const newStatus = property.status === 'active' ? 'inactive' : 'active';
          
          // API 請求更新狀態
          // await apiService.landlord.updatePropertyStatus(id, newStatus);
          
          // 更新本地狀態
          property.status = newStatus;
        } catch (error) {
          console.error('更新房源狀態失敗:', error);
        }
      };
      
      // 取得狀態文字
      const getStatusText = (status) => {
        switch (status) {
          case 'active': return '上架中';
          case 'inactive': return '已下架';
          case 'pending': return '審核中';
          case 'rejected': return '審核拒絕';
          default: return '未知';
        }
      };
      
      // 查看認證狀態
      const checkVerificationStatus = () => {
        // 可以顯示認證詳情模態框或導航到認證詳情頁面
        router.push('/landlord/verification/status');
      };
      
      // 格式化時間
      const formatTime = (time) => {
        if (!time) return '';
        
        const date = new Date(time);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 60) {
          return `${diffMins} 分鐘前`;
        } else if (diffHours < 24) {
          return `${diffHours} 小時前`;
        } else if (diffDays < 30) {
          return `${diffDays} 天前`;
        } else {
          return `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`;
        }
      };
      
      onMounted(() => {
        fetchLandlordData();
      });
      
      return {
        verificationStatus,
        verificationStatusText,
        verificationStatusClass,
        isVerified,
        stats,
        properties,
        messages,
        navigateTo,
        editProperty,
        togglePropertyStatus,
        getStatusText,
        checkVerificationStatus,
        formatTime
      };
    }
  };
  </script>
  
  <style scoped>
  .dashboard-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 30px 20px;
    overflow-y: auto;
    height: calc(100vh - 80px);
  }
  
  .dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }
  
  .dashboard-header h1 {
    font-size: 2rem;
    color: #333;
    margin: 0;
  }
  
  .status-indicator {
    display: flex;
    align-items: center;
    padding: 8px 15px;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: 500;
  }
  
  .status-indicator .status-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
  }
  
  .status-indicator.verified {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4caf50;
  }
  
  .status-indicator.verified .status-dot {
    background-color: #4caf50;
  }
  
  .status-indicator.pending {
    background-color: rgba(255, 152, 0, 0.1);
    color: #ff9800;
  }
  
  .status-indicator.pending .status-dot {
    background-color: #ff9800;
  }
  
  .status-indicator.rejected {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
  }
  
  .status-indicator.rejected .status-dot {
    background-color: #f44336;
  }
  
  .status-indicator.unverified {
    background-color: rgba(158, 158, 158, 0.1);
    color: #9e9e9e;
  }
  
  .status-indicator.unverified .status-dot {
    background-color: #9e9e9e;
  }
  
  .verification-reminder {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 30px;
    overflow: hidden;
  }
  
  .reminder-content {
    display: flex;
    align-items: center;
    padding: 20px;
  }
  
  .reminder-icon {
    font-size: 2.5rem;
    margin-right: 20px;
    color: #ff9800;
  }
  
  .reminder-text {
    flex: 1;
  }
  
  .reminder-text h3 {
    margin: 0 0 10px 0;
    font-size: 1.2rem;
    color: #333;
  }
  
  .reminder-text p {
    margin: 0;
    color: #666;
  }
  
  .reminder-action {
    margin-left: 20px;
  }
  
  .verify-btn, .status-btn {
    padding: 8px 20px;
    border-radius: 5px;
    font-weight: 500;
    text-decoration: none;
    display: inline-block;
    cursor: pointer;
    border: none;
  }
  
  .verify-btn {
    background-color: #ff9800;
    color: white;
  }
  
  .verify-btn:hover {
    background-color: #f57c00;
  }
  
  .status-btn {
    background-color: #f5f5f5;
    color: #333;
  }
  
  .status-btn:hover {
    background-color: #e0e0e0;
  }
  
  .stat-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 30px;
  }
  
  .stat-card {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    display: flex;
    align-items: center;
  }
  
  .stat-icon {
    width: 50px;
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(76, 175, 80, 0.1);
    border-radius: 10px;
    margin-right: 15px;
    font-size: 1.4rem;
    color: #4caf50;
  }
  
  .stat-card:nth-child(2) .stat-icon {
    background-color: rgba(3, 169, 244, 0.1);
    color: #03a9f4;
  }
  
  .stat-card:nth-child(3) .stat-icon {
    background-color: rgba(255, 152, 0, 0.1);
    color: #ff9800;
  }
  
  .stat-card:nth-child(4) .stat-icon {
    background-color: rgba(156, 39, 176, 0.1);
    color: #9c27b0;
  }
  
  .stat-content h3 {
    margin: 0 0 5px 0;
    font-size: 1.5rem;
    color: #333;
  }
  
  .stat-content p {
    margin: 0;
    color: #666;
    font-size: 0.9rem;
  }
  
  .dashboard-main {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 30px;
  }
  
  .dashboard-section {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 30px;
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
  }
  
  .section-header h2 {
    font-size: 1.3rem;
    color: #333;
    margin: 0;
  }
  
  .add-btn, .view-all-btn {
    padding: 8px 15px;
    border-radius: 5px;
    font-weight: 500;
    cursor: pointer;
    border: none;
  }
  
  .add-btn {
    background-color: #4caf50;
    color: white;
  }
  
  .add-btn:hover:not(:disabled) {
    background-color: #388e3c;
  }
  
  .add-btn:disabled {
    background-color: #a5d6a7;
    cursor: not-allowed;
  }
  
  .add-btn.large {
    padding: 12px 25px;
    font-size: 1rem;
  }
  
  .view-all-btn {
    background-color: #f5f5f5;
    color: #333;
  }
  
  .view-all-btn:hover {
    background-color: #e0e0e0;
  }
  
  .property-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .property-card {
    display: flex;
    border: 1px solid #eee;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .property-image {
    width: 160px;
    height: 120px;
    position: relative;
  }
  
  .property-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .property-badge {
    position: absolute;
    top: 10px;
    left: 10px;
    padding: 5px 10px;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  
  .property-badge.active {
    background-color: rgba(76, 175, 80, 0.9);
    color: white;
  }
  
  .property-badge.inactive {
    background-color: rgba(158, 158, 158, 0.9);
    color: white;
  }
  
  .property-badge.pending {
    background-color: rgba(255, 152, 0, 0.9);
    color: white;
  }
  
  .property-content {
    flex: 1;
    padding: 15px;
    display: flex;
    flex-direction: column;
  }
  
  .property-content h3 {
    margin: 0 0 5px 0;
    font-size: 1.1rem;
    color: #333;
  }
  
  .property-address {
    color: #666;
    font-size: 0.9rem;
    margin: 0 0 10px 0;
  }
  
  .property-info {
    display: flex;
    gap: 15px;
    margin-bottom: 10px;
  }
  
  .property-info span {
    font-size: 0.9rem;
    color: #555;
  }
  
  .property-actions {
    margin-top: auto;
    display: flex;
    gap: 10px;
  }
  
  .action-btn {
    padding: 6px 12px;
    border-radius: 4px;
    border: none;
    font-size: 0.9rem;
    cursor: pointer;
  }
  
  .action-btn.edit {
    background-color: #f5f5f5;
    color: #333;
  }
  
  .action-btn.edit:hover {
    background-color: #e0e0e0;
  }
  
  .action-btn.activate {
    background-color: #4caf50;
    color: white;
  }
  
  .action-btn.activate:hover {
    background-color: #388e3c;
  }
  
  .action-btn.deactivate {
    background-color: #f44336;
    color: white;
  }
  
  .action-btn.deactivate:hover {
    background-color: #d32f2f;
  }
  
  .message-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .message-item {
    display: flex;
    gap: 15px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
  }
  
  .message-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    overflow: hidden;
    flex-shrink: 0;
  }
  
  .message-avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .message-content {
    flex: 1;
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
  }
  
  .message-sender {
    font-weight: 500;
    color: #333;
  }
  
  .message-time {
    font-size: 0.8rem;
    color: #999;
  }
  
  .message-property {
    font-size: 0.85rem;
    color: #666;
    margin: 0 0 5px 0;
  }
  
  .message-text {
    margin: 0;
    color: #555;
    font-size: 0.95rem;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  
  .empty-state {
    text-align: center;
    padding: 30px 20px;
  }
  
  .empty-icon {
    font-size: 3rem;
    color: #ccc;
    margin-bottom: 15px;
  }
  
  .empty-state h3 {
    margin: 0 0 10px 0;
    color: #555;
  }
  
  .empty-state p {
    margin: 0 0 20px 0;
    color: #999;
  }
  
  .empty-hint {
    font-size: 0.85rem;
    color: #ff9800;
    margin-top: 10px;
  }
  
  @media (max-width: 992px) {
    .stat-cards {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .dashboard-main {
      grid-template-columns: 1fr;
    }
  }
  
  @media (max-width: 768px) {
    .dashboard-container {
      padding: 20px 15px;
    }
    
    .reminder-content {
      flex-direction: column;
      text-align: center;
    }
    
    .reminder-icon {
      margin: 0 0 15px 0;
    }
    
    .reminder-text {
      margin-bottom: 15px;
    }
    
    .reminder-action {
      margin: 0;
    }
    
    .property-card {
      flex-direction: column;
    }
    
    .property-image {
      width: 100%;
      height: 180px;
    }
  }
  
  @media (max-width: 576px) {
    .stat-cards {
      grid-template-columns: 1fr;
    }
    
    .dashboard-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
    
    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
  }
  </style>