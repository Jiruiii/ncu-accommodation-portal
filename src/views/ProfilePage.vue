<template>
    <div class="profile-page">
      <div class="profile-header">
        <div class="profile-avatar">
          <img src="https://randomuser.me/api/portraits/women/65.jpg" alt="用戶頭像" />
          <button class="edit-avatar-btn">
            <i>📷</i>
          </button>
        </div>
        <div class="profile-info">
          <h1>王小明 <span class="verified">✓ 已驗證</span></h1>
          <div class="profile-meta">
            <div><i>📧</i> wang123@gmail.com</div>
            <div><i>📱</i> 09XX-XXX-XXX</div>
            <div><i>🏫</i> 中央大學 - 資訊工程學系</div>
          </div>
        </div>
        <button class="edit-profile-btn">編輯個人資料</button>
      </div>
  
      <div class="profile-content">
        <div class="profile-navbar">
          <div 
            v-for="tab in tabs" 
            :key="tab.id"
            :class="['nav-item', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            {{ tab.name }}
          </div>
        </div>
  
        <!-- 我的租屋資訊 -->
        <div v-if="activeTab === 'housing'" class="housing-info">
          <div class="section-header">
            <h2>目前租屋</h2>
          </div>
          
          <div class="current-housing">
            <div class="property-card">
              <img src="https://picsum.photos/id/1039/600/300" alt="房屋照片" class="property-image" />
              <div class="property-details">
                <h3>優質學生套房 - 中央大學旁</h3>
                <div class="address"><i>📍</i> 中壢區中大路300號附近</div>
                <div class="lease-details">
                  <div><strong>租期：</strong>2024/01/01 - 2025/12/31</div>
                  <div><strong>月租：</strong>NT$ 8,000</div>
                  <div><strong>押金：</strong>NT$ 16,000</div>
                </div>
                <div class="landlord">
                  <img src="https://randomuser.me/api/portraits/men/42.jpg" alt="房東頭像" class="landlord-avatar" />
                  <div>
                    <div class="landlord-name">張先生</div>
                    <div class="landlord-contact">0912-345-678</div>
                  </div>
                  <button class="contact-btn">聯絡房東</button>
                </div>
              </div>
            </div>
            
            <div class="lease-actions">
              <button class="action-btn report">報修申請</button>
              <button class="action-btn extend">續約申請</button>
              <button class="action-btn terminate">提前終止</button>
              <button class="action-btn receipt">查看繳費紀錄</button>
            </div>
          </div>
  
          <div class="section-header">
            <h2>租屋歷史</h2>
          </div>
          
          <div class="housing-history">
            <div class="history-item">
              <div class="history-date">2022/01 - 2023/12</div>
              <div class="history-content">
                <div class="history-title">經濟實惠雅房 - 近市區</div>
                <div class="history-address">中壢區榮民路123號</div>
                <div class="history-rent">月租：NT$ 5,500</div>
              </div>
              <div class="rating">
                <div class="stars">★★★★☆</div>
                <div class="rating-text">我的評價</div>
              </div>
            </div>
            
            <div class="history-item">
              <div class="history-date">2021/02 - 2021/12</div>
              <div class="history-content">
                <div class="history-title">中央宿舍 - 學生專案</div>
                <div class="history-address">中壢區中大路300號</div>
                <div class="history-rent">月租：NT$ 7,200</div>
              </div>
              <div class="rating">
                <div class="stars">★★★☆☆</div>
                <div class="rating-text">我的評價</div>
              </div>
            </div>
          </div>
        </div>
  
        <!-- 我的發布 -->
        <div v-if="activeTab === 'posts'" class="my-posts">
          <div class="section-header">
            <h2>我的轉租發布</h2>
            <button class="add-post-btn">+ 新增發布</button>
          </div>
          
          <div class="post-list">
            <div class="post-item">
              <div class="post-status active">上架中</div>
              <img src="https://picsum.photos/id/1033/300/180" alt="房屋照片" class="post-image" />
              <div class="post-details">
                <h3>急轉！中央大學旁套房</h3>
                <div class="post-info">
                  <div><i>📅</i> 發布日期：2023/12/15</div>
                  <div><i>👁️</i> 瀏覽次數：152</div>
                  <div><i>☎️</i> 聯絡人數：5</div>
                </div>
                <div class="post-address"><i>📍</i> 中壢區中大路300號附近</div>
                <div class="post-price">
                  <div class="original">原價：NT$ 8,500/月</div>
                  <div class="transfer">轉租價：NT$ 7,800/月</div>
                </div>
                <div class="post-period">可承租期間：2024/02/01 - 2025/01/31</div>
              </div>
              <div class="post-actions">
                <button class="post-btn edit">編輯</button>
                <button class="post-btn deactivate">下架</button>
                <button class="post-btn delete">刪除</button>
              </div>
            </div>
            
            <div class="post-item">
              <div class="post-status inactive">已下架</div>
              <img src="https://picsum.photos/id/1036/300/180" alt="房屋照片" class="post-image" />
              <div class="post-details">
                <h3>近夜市雅房轉租</h3>
                <div class="post-info">
                  <div><i>📅</i> 發布日期：2023/10/05</div>
                  <div><i>👁️</i> 瀏覽次數：97</div>
                  <div><i>☎️</i> 聯絡人數：3</div>
                </div>
                <div class="post-address"><i>📍</i> 中壢區中央西路二段</div>
                <div class="post-price">
                  <div class="original">原價：NT$ 6,000/月</div>
                  <div class="transfer">轉租價：NT$ 5,500/月</div>
                </div>
                <div class="post-period">可承租期間：2023/11/01 - 2024/10/31</div>
              </div>
              <div class="post-actions">
                <button class="post-btn edit">編輯</button>
                <button class="post-btn activate">重新上架</button>
                <button class="post-btn delete">刪除</button>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 我的帳戶設置 -->
        <div v-if="activeTab === 'settings'" class="account-settings">
          <div class="settings-section">
            <h2>帳戶安全</h2>
            <div class="settings-item">
              <div class="settings-label">電子郵件</div>
              <div class="settings-content">
                <span>wang123@gmail.com</span>
                <span class="verified-tag">已驗證</span>
                <button class="settings-btn">修改</button>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">手機號碼</div>
              <div class="settings-content">
                <span>09XX-XXX-XXX</span>
                <span class="verified-tag">已驗證</span>
                <button class="settings-btn">修改</button>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">密碼</div>
              <div class="settings-content">
                <span>••••••••</span>
                <span class="last-updated">上次更新：30天前</span>
                <button class="settings-btn">修改</button>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">雙重驗證</div>
              <div class="settings-content">
                <span>未啟用</span>
                <button class="settings-btn highlight">啟用</button>
              </div>
            </div>
          </div>
          
          <div class="settings-section">
            <h2>通知設定</h2>
            
            <div class="settings-item">
              <div class="settings-label">電子郵件通知</div>
              <div class="settings-content">
                <label class="switch">
                  <input type="checkbox" checked>
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">APP推播通知</div>
              <div class="settings-content">
                <label class="switch">
                  <input type="checkbox" checked>
                  <span class="slider"></span>
                </label>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">租約到期提醒</div>
              <div class="settings-content">
                <select class="settings-select">
                  <option value="30">提前30天</option>
                  <option value="60">提前60天</option>
                  <option value="90">提前90天</option>
                </select>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">新租屋推薦</div>
              <div class="settings-content">
                <label class="switch">
                  <input type="checkbox">
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <div class="settings-section">
            <h2>隱私設置</h2>
            
            <div class="settings-item">
              <div class="settings-label">個人資料可見度</div>
              <div class="settings-content">
                <select class="settings-select">
                  <option value="public">公開</option>
                  <option value="friends">僅好友</option>
                  <option value="private">僅自己</option>
                </select>
              </div>
            </div>
            
            <div class="settings-item">
              <div class="settings-label">允許他人聯絡</div>
              <div class="settings-content">
                <label class="switch">
                  <input type="checkbox" checked>
                  <span class="slider"></span>
                </label>
              </div>
            </div>
          </div>
          
          <div class="danger-zone">
            <h2>危險區域</h2>
            <button class="danger-btn">刪除帳戶</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "ProfilePage",
    data() {
      return {
        activeTab: 'housing',
        tabs: [
          { id: 'housing', name: '我的租屋資訊' },
          { id: 'posts', name: '我的發布' },
          { id: 'settings', name: '帳戶設置' }
        ]
      };
    }
  };
  </script>
  
  <style scoped>
  .profile-page {
    max-width: 1200px;
    margin: 0 auto;
    padding: 30px 20px;
    background-color: #f9f9f9;
    min-height: 100vh;
  }
  
  .profile-header {
    display: flex;
    align-items: center;
    padding: 30px;
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    margin-bottom: 30px;
    position: relative;
  }
  
  .profile-avatar {
    position: relative;
    margin-right: 30px;
  }
  
  .profile-avatar img {
    width: 120px;
    height: 120px;
    border-radius: 50%;
    object-fit: cover;
    border: 4px solid #f0f0f0;
  }
  
  .edit-avatar-btn {
    position: absolute;
    bottom: 5px;
    right: 5px;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background-color: #007bff;
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }
  
  .profile-info {
    flex: 1;
  }
  
  .profile-info h1 {
    font-size: 2rem;
    margin: 0 0 10px 0;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .verified {
    font-size: 0.85rem;
    color: #28a745;
    background-color: rgba(40, 167, 69, 0.1);
    padding: 4px 8px;
    border-radius: 4px;
  }
  
  .profile-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    color: #666;
  }
  
  .profile-meta div {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .edit-profile-btn {
    position: absolute;
    top: 30px;
    right: 30px;
    padding: 10px 20px;
    background-color: #f0f0f0;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
  }
  
  .edit-profile-btn:hover {
    background-color: #e0e0e0;
  }
  
  .profile-content {
    background-color: white;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    overflow: hidden;
  }
  
  .profile-navbar {
    display: flex;
    border-bottom: 1px solid #eee;
  }
  
  .nav-item {
    padding: 20px 30px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
  }
  
  .nav-item:hover {
    background-color: #f9f9f9;
  }
  
  .nav-item.active {
    color: #007bff;
  }
  
  .nav-item.active::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background-color: #007bff;
  }
  
  /* 我的租屋資訊 */
  .housing-info {
    padding: 30px;
  }
  
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .section-header h2 {
    font-size: 1.5rem;
    margin: 0;
    color: #333;
  }
  
  .current-housing {
    margin-bottom: 40px;
  }
  
  .property-card {
    display: flex;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }
  
  .property-image {
    width: 300px;
    height: 200px;
    object-fit: cover;
  }
  
  .property-details {
    padding: 20px;
    flex: 1;
  }
  
  .property-details h3 {
    margin: 0 0 10px 0;
    font-size: 1.3rem;
  }
  
  .address {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #666;
    margin-bottom: 15px;
  }
  
  .lease-details {
    display: flex;
    gap: 30px;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #eee;
  }
  
  .landlord {
    display: flex;
    align-items: center;
  }
  
  .landlord-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    margin-right: 15px;
  }
  
  .landlord-name {
    font-weight: 500;
    margin-bottom: 5px;
  }
  
  .landlord-contact {
    color: #666;
    font-size: 0.9rem;
  }
  
  .contact-btn {
    margin-left: auto;
    padding: 8px 15px;
    background-color: #007bff;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  
  .lease-actions {
    display: flex;
    gap: 15px;
  }
  
  .action-btn {
    flex: 1;
    padding: 12px 0;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
  }
  
  .report {
    background-color: #f8f9fa;
    color: #343a40;
  }
  
  .extend {
    background-color: #28a745;
    color: white;
  }
  
  .terminate {
    background-color: #dc3545;
    color: white;
  }
  
  .receipt {
    background-color: #17a2b8;
    color: white;
  }
  
  .housing-history {
    margin-top: 20px;
  }
  
  .history-item {
    display: flex;
    padding: 20px;
    border-radius: 8px;
    background-color: #f8f9fa;
    margin-bottom: 15px;
  }
  
  .history-date {
    width: 150px;
    font-weight: 500;
  }
  
  .history-content {
    flex: 1;
  }
  
  .history-title {
    font-weight: 500;
    margin-bottom: 5px;
  }
  
  .history-address, .history-rent {
    color: #666;
    font-size: 0.9rem;
  }
  
  .rating {
    text-align: center;
  }
  
  .stars {
    color: #ffc107;
    font-size: 1.2rem;
    margin-bottom: 5px;
  }
  
  .rating-text {
    font-size: 0.8rem;
    color: #777;
  }
  
  /* 我的發布 */
  .my-posts {
    padding: 30px;
  }
  
  .add-post-btn {
    padding: 8px 15px;
    background-color: #28a745;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  
  .post-list {
    margin-top: 20px;
  }
  
  .post-item {
    display: flex;
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
    position: relative;
  }
  
  .post-status {
    position: absolute;
    top: 15px;
    left: 15px;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 0.8rem;
    font-weight: 500;
  }
  
  .active {
    background-color: #28a745;
    color: white;
  }
  
  .inactive {
    background-color: #6c757d;
    color: white;
  }
  
  .post-image {
    width: 300px;
    height: 180px;
    object-fit: cover;
  }
  
  .post-details {
    padding: 20px;
    flex: 1;
  }
  
  .post-details h3 {
    margin: 0 0 10px 0;
    font-size: 1.2rem;
  }
  
  .post-info {
    display: flex;
    gap: 15px;
    color: #666;
    font-size: 0.85rem;
    margin-bottom: 10px;
  }
  
  .post-address {
    display: flex;
    align-items: center;
    color: #555;
    margin-bottom: 10px;
  }
  
  .post-price {
    display: flex;
    gap: 20px;
    margin-bottom: 10px;
  }
  
  .original {
    color: #666;
    text-decoration: line-through;
  }
  
  .transfer {
    color: #dc3545;
    font-weight: 500;
  }
  
  .post-period {
    color: #555;
    font-size: 0.9rem;
  }
  
  .post-actions {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 20px;
    background-color: #f8f9fa;
  }
  
  .post-btn {
    padding: 8px 20px;
    margin-bottom: 10px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .edit {
    background-color: #17a2b8;
    color: white;
  }
  
  .deactivate {
    background-color: #ffc107;
    color: #212529;
  }
  
  .activate {
    background-color: #28a745;
    color: white;
  }
  
  .delete {
    background-color: #dc3545;
    color: white;
  }
  
  /* 帳戶設置 */
  .account-settings {
    padding: 30px;
  }
  
  .settings-section {
    margin-bottom: 40px;
  }
  
  .settings-section h2 {
    font-size: 1.4rem;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
  }
  
  .settings-item {
    display: flex;
    padding: 15px 0;
    border-bottom: 1px solid #f5f5f5;
  }
  
  .settings-label {
    width: 150px;
    font-weight: 500;
  }
  
  .settings-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 15px;
  }
  
  .verified-tag {
    padding: 2px 8px;
    background-color: rgba(40, 167, 69, 0.1);
    color: #28a745;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  
  .last-updated {
    color: #777;
    font-size: 0.85rem;
  }
  
  .settings-btn {
    padding: 5px 15px;
    background-color: #f0f0f0;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-left: auto;
  }
  
  .settings-btn.highlight {
    background-color: #007bff;
    color: white;
  }
  
  .switch {
    position: relative;
    display: inline-block;
    width: 50px;
    height: 24px;
  }
  
  .switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #ccc;
    transition: .4s;
    border-radius: 24px;
  }
  
  .slider:before {
    position: absolute;
    content: "";
    height: 16px;
    width: 16px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: .4s;
    border-radius: 50%;
  }
  
  input:checked + .slider {
    background-color: #007bff;
  }
  
  input:checked + .slider:before {
    transform: translateX(26px);
  }
  
  .settings-select {
    padding: 8px;
    border-radius: 4px;
    border: 1px solid #ddd;
    width: 180px;
  }
  
  .danger-zone {
    margin-top: 40px;
    padding: 20px;
    background-color: #fff5f5;
    border-radius: 8px;
    border: 1px solid #ffcccc;
  }
  
  .danger-zone h2 {
    color: #dc3545;
    font-size: 1.2rem;
    margin-bottom: 15px;
  }
  
  .danger-btn {
    padding: 10px 20px;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
  }
  </style>