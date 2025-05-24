<template>
  <div class="profile-page">
    <div class="profile-header">
      <div class="profile-avatar">
        <img :src="avatarUrl" alt="用戶頭像" />
        <button
          class="edit-avatar-btn"
          @click="triggerFileInput"
          :disabled="isUploading"
        >
          <i class="fa-solid fa-camera" v-if="!isUploading"></i>
          <i class="fa-solid fa-spinner fa-spin" v-else></i>
        </button>
        <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept="image/*"
          @change="uploadAvatar"
        />
        <div v-if="uploadError" class="upload-error">{{ uploadError }}</div>
      </div>

      <div class="profile-info">
        <h1>
          {{ user.username }}
          <span class="verified" v-if="user.is_verified">✓ 已驗證</span>
        </h1>
        <div class="profile-meta">
          <div>
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="#666" d="M20,4H4C2.9,4,2,4.9,2,6v12c0,1.1,0.9,2,2,2h16c1.1,0,2-0.9,2-2V6C22,4.9,21.1,4,20,4z M20,8l-8,5L4,8V6l8,5l8-5V8z"/>
            </svg>
            {{ user.email }}
          </div>
          <div v-if="user.phone">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="#666" d="M17,19H7V5H17M17,1H7C5.89,1 5,1.89 5,3V21A2,2 0 0,0 7,23H17A2,2 0 0,0 19,21V3C19,1.89 18.1,1 17,1Z"/>
            </svg>
            {{ user.phone }}
          </div>
          <div v-if="user.school_email">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="#666" d="M12,3L1,9L12,15L21,10.09V17H23V9M5,13.18V17.18L12,21L19,17.18V13.18L12,17L5,13.18Z"/>
            </svg>
            {{ user.school_email }}
          </div>
          <!-- 保留管理員角色標記 -->
          <div v-if="isAdmin" class="admin-badge">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="#b91c1c" d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.1 14.8,9.5V11C15.4,11 16,11.6 16,12.3V15.8C16,16.4 15.4,17 14.7,17H9.2C8.6,17 8,16.4 8,15.7V12.2C8,11.6 8.6,11 9.2,11V9.5C9.2,8.1 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,9.5V11H13.5V9.5C13.5,8.7 12.8,8.2 12,8.2Z"/>
            </svg>
            {{ user.user_role === "superuser" ? "超級管理員" : "管理員" }}
          </div>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout">
        <span class="material-symbols-outlined"> logout </span>登出
      </button>
      <button
        v-if="isAdmin"
        class="admin-dashboard-btn"
        @click="goToAdminDashboard"
      >
        <i>⚙️</i> 進入管理後台
      </button>
    </div>

    <div class="profile-content">
      <!-- 保留現有的選項卡導航 -->
      <div class="profile-navbar">
        <div
          v-for="tab in tabs"
          :key="tab.id"
          :class="['nav-item', { active: activeTab === tab.id }]"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
          <span v-if="tab.id === 'verify'" class="verification-badge"
            >驗證</span
          >
        </div>
      </div>

      <!-- 保留現有的內容部分，各選項卡內容 -->
      <div v-if="activeTab === 'verify'" class="student-verification">
        <div class="section-header">
          <h2>學生身分認證</h2>
          <span class="verification-status verified">已驗證</span>
        </div>

        <div class="verification-details">
          <div class="verification-item">
            <div class="verification-label">學校</div>
            <div class="verification-content">國立中央大學</div>
          </div>
          <div class="verification-item">
            <div class="verification-label">學號</div>
            <div class="verification-content">110XXXXX</div>
          </div>
          <div class="verification-item">
            <div class="verification-label">系所</div>
            <div class="verification-content">資訊工程學系</div>
          </div>
          <div class="verification-item">
            <div class="verification-label">驗證日期</div>
            <div class="verification-content">2024/03/15</div>
          </div>
        </div>

        <div class="verification-renewal">
          <div class="renewal-info">
            <i class="info-icon">ℹ️</i>
            <span>學生身分驗證有效期為一年，將於 2025/03/15 到期</span>
          </div>
          <button class="renew-btn">更新驗證</button>
        </div>
      </div>

      <!-- 我的租屋資訊 -->
      <div v-if="activeTab === 'housing'" class="housing-info">
        <div class="section-header">
          <h2>目前租屋</h2>
        </div>

        <div class="current-housing">
          <div class="property-card">
            <img
              src="https://picsum.photos/id/1039/600/300"
              alt="房屋照片"
              class="property-image"
            />
            <div class="property-details">
              <h3>優質學生套房 - 中央大學旁</h3>
              <div class="address">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="#EA4335" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                </svg>
                中壢區中大路300號附近
              </div>
              <div class="lease-details">
                <div><strong>租期：</strong>2024/01/01 - 2025/12/31</div>
                <div><strong>月租：</strong>NT$ 8,000</div>
                <div><strong>押金：</strong>NT$ 16,000</div>
              </div>
              <div class="landlord">
                <img
                  src="https://randomuser.me/api/portraits/men/42.jpg"
                  alt="房東頭像"
                  class="landlord-avatar"
                />
                <div>
                  <div class="landlord-name">張先生</div>
                  <div class="landlord-contact">0912-345-678</div>
                </div>
                <button class="contact-btn" @click="showContactModal = true">
                  聯絡房東
                </button>
              </div>
            </div>
          </div>

          <div v-if="showContactModal" class="modal-overlay" @click="showContactModal = false">
          <div class="modal-container" @click.stop>
            <div class="modal-header">
              <h3>房東聯絡資訊</h3>
              <button class="modal-close" @click="showContactModal = false">&times;</button>
            </div>
            <div class="modal-body">
              <div class="contact-info-item">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="#666" d="M17,19H7V5H17M17,1H7C5.89,1 5,1.89 5,3V21A2,2 0 0,0 7,23H17A2,2 0 0,0 19,21V3C19,1.89 18.1,1 17,1Z"/>
                </svg>
                <span>手機：0912-345-678</span>
              </div>
              <div class="contact-info-item">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="#666" d="M20,4H4C2.9,4,2,4.9,2,6v12c0,1.1,0.9,2,2,2h16c1.1,0,2-0.9,2-2V6C22,4.9,21.1,4,20,4z M20,8l-8,5L4,8V6l8,5l8-5V8z"/>
                </svg>
                <span>Email：landlord@example.com</span>
              </div>
              <div class="contact-info-item">
                <svg viewBox="0 0 24 24" width="16" height="16">
                  <path fill="#666" d="M12,21.35L10.55,20.03C5.4,15.36 2,12.27 2,8.5C2,5.41 4.42,3 7.5,3C9.24,3 10.91,3.81 12,5.08C13.09,3.81 14.76,3 16.5,3C19.58,3 22,5.41 22,8.5C22,12.27 18.6,15.36 13.45,20.03L12,21.35Z"/>
                </svg>
                <span>Line ID：landlord_123</span>
              </div>
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

        <div class="section-header">
          <h2>報修紀錄</h2>
        </div>

        <div class="maintenance-history">
          <div class="maintenance-item">
            <div class="maintenance-status resolved">已解決</div>
            <div class="maintenance-header">
              <h3>冷氣故障</h3>
              <div class="maintenance-date">2024/04/05</div>
            </div>
            <div class="maintenance-details">
              <p>冷氣開機後無法正常製冷，可能是需要添加冷媒。</p>
              <div class="maintenance-photos">
                <img
                  src="https://picsum.photos/id/100/100/100"
                  alt="故障照片"
                />
                <img
                  src="https://picsum.photos/id/101/100/100"
                  alt="故障照片"
                />
              </div>
            </div>
            <div class="maintenance-response">
              <div class="response-header">房東回覆：</div>
              <p>已安排冷氣技師於 4/7 上午 10:00 前往維修，請確保有人在家。</p>
            </div>
            <div class="maintenance-resolution">
              <div class="resolution-header">解決方案：</div>
              <p>已完成冷媒添加及系統清潔，冷氣已恢復正常運作。</p>
            </div>
          </div>

          <div class="maintenance-item">
            <div class="maintenance-status pending">處理中</div>
            <div class="maintenance-header">
              <h3>浴室排水堵塞</h3>
              <div class="maintenance-date">2024/05/01</div>
            </div>
            <div class="maintenance-details">
              <p>浴室排水口排水緩慢，洗澡時容易積水。</p>
              <div class="maintenance-photos">
                <img
                  src="https://picsum.photos/id/102/100/100"
                  alt="故障照片"
                />
              </div>
            </div>
            <div class="maintenance-response">
              <div class="response-header">房東回覆：</div>
              <p>已記錄，將於近日安排水電師傅查看。</p>
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
            <img
              src="https://picsum.photos/id/1033/300/180"
              alt="房屋照片"
              class="post-image"
            />
            <div class="post-details"></div>
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
          <img
            src="https://picsum.photos/id/1036/300/180"
            alt="房屋照片"
            class="post-image"
          />
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

      <!-- 我的帳戶設置 -->
      <div v-if="activeTab === 'settings'" class="account-settings">
        <!-- 帳戶安全區塊 -->
        <settings-section title="帳戶安全">
          <!-- Portal 綁定 -->
          <settings-item label="中央大學 Portal">
            <div class="field-action-group">
              <editable-field
                :value="user.has_portal_id ? '已綁定' : '未綁定'"
                :editable="false"
                :show-badge="user.has_portal_id"
                badge="已驗證"
                badge-type="verified"
              >
                <template v-slot:editor></template>
              </editable-field>
              <button
                :class="[
                  'settings-btn',
                  user.has_portal_id ? 'danger-btn' : '',
                ]"
                @click="bindPortalAccount"
                :disabled="isProcessingPortal"
              >
                {{ user.has_portal_id ? "取消綁定" : "立即綁定" }}
              </button>
            </div>
          </settings-item>

          <!-- 電子郵件 -->
          <settings-item label="電子郵件">
            <div class="field-action-group">
              <editable-field
                ref="emailField"
                :value="user.email"
                :display-value="user.email"
                :editable="true"
                edit-button-text="修改"
                :show-badge="true"
                :badge="user.is_email_verified ? '已驗證' : '未驗證'"
                field-label="電子郵件"
                modal-title="修改電子郵件"
                :show-verification-warning="user.is_email_verified"
                :badge-type="user.is_email_verified ? 'verified' : 'unverified'"
                @save="handleShowEmailChange"
              >
              </editable-field>
              <button
                v-if="!user.is_email_verified"
                class="settings-btn verify-btn"
                @click="showEmailVerificationModal = true"
              >
                驗證郵箱
              </button>
            </div>
          </settings-item>

          <!-- 校園郵箱 -->
          <settings-item label="校園郵箱">
            <span v-if="user.school_email">{{ user.school_email }}</span>
            <span v-else>未綁定</span>
          </settings-item>

          <!-- 手機號碼 -->
          <settings-item label="手機號碼">
            <div class="field-action-group">
              <editable-field
                ref="phoneField"
                :value="user.phone"
                :display-value="user.phone || '尚未設置'"
                :editable="true"
                :edit-button-text="user.phone ? '修改' : '設置'"
                :show-badge="false"
                :badge="user.is_phone_verified ? '已驗證' : '未驗證'"
                field-label="手機號碼"
                modal-title="修改手機號碼"
                :badge-type="user.is_phone_verified ? 'verified' : 'unverified'"
                @save="handleShowPhoneChange"
              >
              </editable-field>
              <!-- <button
                v-if="user.phone && !user.is_phone_verified"
                class="settings-btn verify-btn"
                @click="showPhoneVerificationModal = true"
              >
                驗證手機
              </button> -->
            </div>
          </settings-item>

          <!-- 密碼 -->
          <settings-item label="密碼">
            <div class="password-field">
              <div class="masked-password">••••••••</div>
              <button
                class="settings-btn highlight"
                @click="showPasswordModal = true"
              >
                修改密碼
              </button>
            </div>
          </settings-item>
        </settings-section>

        <div class="settings-section">
          <h2>通知設定</h2>

          <div class="settings-item">
            <div class="settings-label">電子郵件通知</div>
            <div class="settings-content">
              <label class="switch">
                <input type="checkbox" checked />
                <span class="slider"></span>
              </label>
            </div>
          </div>

          <div class="settings-item">
            <div class="settings-label">APP推播通知</div>
            <div class="settings-content">
              <label class="switch">
                <input type="checkbox" checked />
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
                <input type="checkbox" />
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
                <input type="checkbox" checked />
                <span class="slider"></span>
              </label>
            </div>
          </div>
          </div>

          <!-- 添加小幫手功能 -->
          <div class="user-assistant">
              <h2>租屋小幫手</h2>
            <div class="assistant-feature">
          <div class="feature-icon">
            <svg viewBox="0 0 24 24" width="24" height="24">
              <path fill="#3b82f6" d="M21,19V20H3V19L5,17V11C5,7.9 7.03,5.17 10,4.29C10,4.19 10,4.1 10,4A2,2 0 0,1 12,2A2,2 0 0,1 14,4C14,4.1 14,4.19 14,4.29C16.97,5.17 19,7.9 19,11V17L21,19M14,21A2,2 0 0,1 12,23A2,2 0 0,1 10,21"/>
            </svg>
          </div>
          <div class="feature-content">
            <h4>租約到期提醒</h4>
            <p>您的租約將於 45 天後到期，建議您盡快聯繫房東討論續約事宜。</p>
            <button class="feature-action-btn">聯繫房東</button>
          </div>
        </div>
          <div class="assistant-feature">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path fill="#3b82f6" d="M12,2A7,7 0 0,0 5,9C5,11.38 6.19,13.47 8,14.74V17A1,1 0 0,0 9,18H15A1,1 0 0,0 16,17V14.74C17.81,13.47 19,11.38 19,9A7,7 0 0,0 12,2M9,21A1,1 0 0,0 10,22H14A1,1 0 0,0 15,21V20H9V21Z"/>
              </svg>
            </div>
            <div class="feature-content">
              <h4>租屋建議</h4>
              <p>根據您的搜尋歷史，我們推薦您查看近中央大學的 3 間新上架套房。</p>
              <button class="feature-action-btn">查看推薦</button>
            </div>
          </div>
        </div>

        <!-- 在帳戶設置中也添加管理員面板的項目 -->
        <div class="settings-section" v-if="isAdmin">
          <h2>管理員功能</h2>

          <div class="admin-features">
            <div class="admin-feature-card">
              <div class="admin-feature-icon">⚙️</div>
              <div class="admin-feature-content">
                <h3>系統管理</h3>
                <p>進入管理後台查看系統狀態、管理用戶和查看數據庫紀錄。</p>
                <button @click="goToAdminDashboard" class="admin-feature-btn">
                  進入後台
                </button>
              </div>
            </div>
          </div>

          <div class="admin-login-history">
            <h3>最近登入記錄</h3>
            <div class="login-history-item">
              <div class="login-time">{{ formatDate(new Date()) }}</div>
              <div class="login-device">Chrome 瀏覽器 - Windows 10</div>
              <div class="login-ip">127.0.0.1</div>
              <div class="login-status success">成功</div>
            </div>
          </div>
        </div>

        <div class="danger-zone">
          <h2>危險區域</h2>
          <p>請注意：刪除帳戶將永久移除您的所有資料，包括租屋記錄、聊天紀錄等。此操作無法復原。</p>
          <button class="danger-btn" @click="deleteAccount">
            <svg viewBox="0 0 24 24" width="16" height="16">
              <path fill="currentColor" d="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z"/>
            </svg>
            刪除帳戶
          </button>
        </div>

        <!-- 電子郵件驗證彈窗 -->
        <email-verification-modal
          :show="showEmailVerificationModal"
          :email="user.email"
          @close="showEmailVerificationModal = false"
          @verification-success="handleEmailVerificationSuccess"
        />

        <!-- 手機驗證彈窗 -->
        <phone-verification-modal
          :show="showPhoneVerificationModal"
          :phone="user.phone"
          @close="showPhoneVerificationModal = false"
          @verification-success="handlePhoneVerificationSuccess"
        />

        <password-change-modal
          :show="showPasswordModal"
          @close="showPasswordModal = false"
          @success="handlePasswordChangeSuccess"
          @forgot-password="showForgotPasswordModal = true"
        />

        <forgot-password-modal
          :show="showForgotPasswordModal"
          @close="showForgotPasswordModal = false"
          :user-email="user.email"
        />
      </div>

      <ChatRoom v-if="activeTab === 'chatroom'" />
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, reactive } from "vue";
  import { useRouter } from "vue-router";
  import { useStore } from "vuex";
  import apiService from "@/services/api";
  import EmailVerificationModal from "@/components/verification/EmailVerificationModal.vue";
  import PhoneVerificationModal from "@/components/verification/PhoneVerificationModal.vue";
  import EditableField from "@/components/common/EditableField.vue";
  import SettingsSection from "@/components/profile/SettingsSection.vue";
  import SettingsItem from "@/components/profile/SettingsItem.vue";
  import PasswordChangeModal from "@/components/profile/PasswordChangeModal.vue";
  import ForgotPasswordModal from "@/components/profile/ForgotPasswordModal.vue";
  import ChatRoom from "@/components/ChatRoom.vue";

  export default {
    name: "ProfilePage",
    components: {
      EmailVerificationModal,
      PhoneVerificationModal,
      EditableField,
      SettingsSection,
      SettingsItem,
      PasswordChangeModal,
      ForgotPasswordModal,
      ChatRoom,
    },
    setup() {
      const store = useStore();
      const router = useRouter();

      const activeTab = ref("housing");

      const loading = ref(true);
      const error = ref(null);

      const showEditModal = ref(false);
      const showPasswordModal = ref(false);
      const showForgotPasswordModal = ref(false);
      const showBindPortalModal = ref(false);
      const showEmailVerificationModal = ref(false);
      const showPhoneVerificationModal = ref(false);

      const isProcessingPortal = ref(false);

      const fileInput = ref(null);
      const isUploading = ref(false);
      const uploadError = ref(null);

      const showContactModal = ref(false);

      const user = computed(() => store.getters["user/currentUser"]);
      const isAdmin = computed(() => store.getters["user/isAdmin"]);
      const avatarUrl = computed(() => store.getters["user/avatarUrl"]);

      const fetchUserData = async () => {
        try {
          loading.value = true;
          error.value = null;
          await store.dispatch("user/fetchUserProfile");
        } catch (err) {
          console.error("獲取用戶資料失敗:", err);
          error.value = "獲取資料失敗，請稍後重試";
        } finally {
          loading.value = false;
        }
      };

      // 觸發文件選擇對話框
      const triggerFileInput = () => {
        fileInput.value.click();
      };

      // 上傳頭像
      const uploadAvatar = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        try {
          isUploading.value = true;
          uploadError.value = null;

          const formData = new FormData();
          formData.append("image", file);

          // 使用 user 模組的 updateProfileImage action
          const profileImage = await store.dispatch(
            "user/updateProfileImage",
            formData
          );

          if (profileImage) {
            // 強制刷新頭像顯示
            const timestamp = new Date().getTime();
            // 注意：這裡不再需要手動處理頭像 URL，使用 avatarUrl 計算屬性即可
          } else {
            uploadError.value = "上傳失敗，請稍後再試";
          }
        } catch (error) {
          console.error("上傳頭像失敗:", error);
          uploadError.value = error.message || "上傳失敗，請稍後再試";
        } finally {
          isUploading.value = false;
          event.target.value = "";
        }
      };

      // 個人資料編輯表單
      const editForm = reactive({
        username: "",
        email: "",
        phone: "",
      });

      // 密碼修改表單
      const passwordForm = reactive({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });

      // 確定标签應該顯示哪些
      const tabs = computed(() => {
        const baseTabs = [
          { id: "housing", name: "我的租屋資訊" },
          { id: "settings", name: "帳戶設置" },
          { id: "chatroom", name: "聊天室" },
        ];

        // 如果用户有發佈權限則添加「我的發布」標籤
        if (["landlord", "admin", "superuser"].includes(user.value.user_role)) {
          baseTabs.splice(1, 0, { id: "posts", name: "我的發布" });
        }

        return baseTabs;
      });

      // 計算屬性：格式化用戶全名
      const fullName = computed(() => {
        return user.value.username || "未知用戶";
      });

      // 計算屬性：學生資訊
      const studentInfo = computed(() => {
        if (user.value.has_portal_id) {
          return "國立中央大學學生";
        }
        return null;
      });

      // 格式化日期的方法
      const formatDate = (dateString) => {
        if (!dateString) return "從未";

        const date = new Date(dateString);
        return new Intl.DateTimeFormat("zh-TW", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        }).format(date);
      };

      // 導航到管理後台
      const goToAdminDashboard = () => {
        router.push("/admin");
      };

      // 開啟編輯個人資料模態框
      const openEditModal = () => {
        // 確保表單數據與當前用戶數據一致
        editForm.username = user.value.username || "";
        editForm.email = user.value.email || "";
        editForm.phone = user.value.phone || "";
        editForm.bio = user.value.bio || "";
        showEditModal.value = true;
      };

      // 綁定 Portal 帳號
      const bindPortalAccount = async () => {
        if (user.value.has_portal_id) {
          // 用戶已綁定 Portal，執行解除綁定操作
          if (
            !confirm("確定要解除 Portal 綁定嗎？這將移除您的學生身分認證。")
          ) {
            return; // 用戶取消操作
          }

          isProcessingPortal.value = true;

          try {
            const response = await apiService.users.unbindPortal();

            if (response && response.success) {
              await store.dispatch("user/updateProfile", {
                has_portal_id: false,
                school_email: null,
              });
            } else {
              throw new Error(response.message || "解除綁定失敗");
            }
          } catch (err) {
            console.error("解除綁定 Portal 失敗:", err);
            alert(`解除綁定失敗: ${err.message || "未知錯誤"}`);
          } finally {
            isProcessingPortal.value = false;
          }
        } else {
          // 導向 Portal 授權頁面
          isProcessingPortal.value = true;
          window.location.href = apiService.auth.portal.getBindingUrl();
        }
      };

      // 刪除帳戶
      const deleteAccount = async () => {
        if (!confirm("您確定要刪除帳戶嗎？此操作不可恢復！")) {
          return;
        }

        const password = prompt("請輸入您的密碼以確認刪除帳戶");
        if (!password) return;

        try {
          await apiService.users.deleteAccount({ password });
          alert("帳戶已成功刪除");
          await store.dispatch("user/logout");
          router.push("/login");
        } catch (err) {
          console.error("刪除帳戶失敗:", err);
          alert(`刪除失敗: ${err.message || "未知錯誤"}`);
        }
      };

      const handleEmailVerificationSuccess = () => {
        store.dispatch("user/updateProfile", {
          is_email_verified: true,
        });
      };

      const handlePhoneVerificationSuccess = () => {
        store.dispatch("user/updateProfile", {
          is_phone_verified: true,
        });
      };

      const handleShowEmailChange = async (newValue, callbacks = {}) => {
        const tempNewEmail = newValue;

        // 驗證電子郵件格式
        if (!tempNewEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(tempNewEmail)) {
          if (callbacks.error) callbacks.error("請輸入有效的電子郵件地址");
          return;
        }

        try {
          const response = await apiService.users.updateEmail(tempNewEmail);

          if (response.success) {
            await store.dispatch("user/updateProfile", {
              email: tempNewEmail,
              is_email_verified: false,
            });

            if (callbacks.success) callbacks.success();
          } else {
            if (callbacks.error)
              callbacks.error(response.message || "更新電子郵件失敗");
          }
        } catch (error) {
          console.error("更新電子郵件失敗:", error);
          if (callbacks.error) callbacks.error();
        }
      };

      const handleShowPhoneChange = async (newValue, callbacks = {}) => {
        const tempNewPhone = newValue;

        // 驗證手機號碼格式
        if (!tempNewPhone || !/^09\d{8}$/.test(tempNewPhone)) {
          if (callbacks.error)
            callbacks.error("請輸入有效的手機號碼（格式：09xxxxxxxx）");
          return;
        }

        try {
          const response = await apiService.users.updatePhone(tempNewPhone);

          if (response.success) {
            await store.dispatch("user/updateProfile", {
              phone: tempNewPhone,
              is_phone_verified: false,
            });

            // 通知 EditableField 儲存成功
            if (callbacks.success) callbacks.success();
          } else {
            if (callbacks.error)
              callbacks.error(response.message || "更新手機號碼失敗");
          }
        } catch (error) {
          console.error("更新手機號碼失敗:", error);
          if (callbacks.error)
            callbacks.error(error.message || "更新失敗，請稍後再試");
        }
      };

      const handleShowPasswordChange = (newValue, callbacks = {}) => {
        showPasswordModal.value = true;
        if (callbacks.success) callbacks.success();
      };

      const handlePasswordChangeSuccess = () => {
        showPasswordModal.value = false;
      };

      const handleLogout = async () => {
        try {
          await store.dispatch("user/logout");
          router.push("/login");
        } catch (error) {
          console.error("登出失敗:", error);
        }
      };

      const goToLogin = () => {
        router.push("/login");
      };

      onMounted(() => {
        fetchUserData();
      });

      return {
        activeTab,
        tabs,
        user,
        isAdmin,
        fullName,
        studentInfo,
        formatDate,
        loading,
        isProcessingPortal,
        error,
        showEditModal,
        showPasswordModal,
        showBindPortalModal,
        showEmailVerificationModal,
        showPhoneVerificationModal,
        showForgotPasswordModal,
        editForm,
        passwordForm,
        openEditModal,
        fileInput,
        avatarUrl,
        triggerFileInput,
        uploadAvatar,
        uploadError,
        isUploading,
        bindPortalAccount,
        deleteAccount,
        goToAdminDashboard,
        goToLogin,
        handleEmailVerificationSuccess,
        handlePhoneVerificationSuccess,
        handlePasswordChangeSuccess,
        handleShowEmailChange,
        handleShowPhoneChange,
        handleShowPasswordChange,
        showContactModal,
      };
    },
  };
</script>

<style scoped>
  /* 保留現有樣式 */
  .profile-page {
    margin: 0 auto;
    padding: 30px 20px;
    background-color: #f9f9f9;
    min-height: 100vh;
    overflow-y: auto;
    scrollbar-width: thin;
    scrollbar-color: #c1c1c1 #f1f1f1;
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
    background-color: #c4e1ff;
    color: white;
    border: none;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
  }

  i {
    color: black;
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
    gap: 8px;
    color: #666;
  }

  .profile-meta svg {
    min-width: 16px;
    height: 16px;
  }

  .logout-btn {
    position: absolute;
    top: 30px;
    right: 30px;
    padding: 10px 20px;
    background-color: #dc3545;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .logout-btn:hover {
    background-color: #c82333;
  }
  
  .logout-btn .material-symbols-outlined {
    font-size: 1.2rem;
    margin-right: 8px;
    display: inline-flex;
    vertical-align: middle;
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

  .maintenance-history {
  display: grid;
  gap: 20px;
  padding: 10px 0;
}

.maintenance-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
  position: relative;
}

.maintenance-status {
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.maintenance-status.resolved {
  background-color: #dcfce7;
  color: #15803d;
}

.maintenance-status.pending {
  background-color: #fff7ed;
  color: #c2410c;
}

.maintenance-header {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  margin-bottom: 15px;
  padding-right: 100px;
}

.maintenance-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #1e293b;
}

.maintenance-date {
  color: #64748b;
  font-size: 0.9rem;
}

.maintenance-details {
  padding: 15px 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
}

.maintenance-details p {
  margin: 0 0 15px 0;
  color: #475569;
  line-height: 1.5;
}

.maintenance-photos {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 5px 0;
}

.maintenance-photos img {
  width: 100px;
  height: 100px;
  object-fit: cover;
  border-radius: 8px;
  transition: transform 0.2s;
  cursor: pointer;
}

.maintenance-photos img:hover {
  transform: scale(1.05);
}

.maintenance-response,
.maintenance-resolution {
  margin-top: 15px;
}

.response-header,
.resolution-header {
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.maintenance-response p,
.maintenance-resolution p {
  color: #475569;
  line-height: 1.5;
  margin: 0;
}

  @media (max-width: 768px) {
  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 20px;
  }

  .profile-avatar {
    margin-right: 0;
    margin-bottom: 20px;
  }

  .profile-meta {
    justify-content: center;
  }

  .edit-profile-btn {
    position: static;
    margin-top: 20px;
    width: 100%;
  }

  .admin-dashboard-btn {
    position: static;
    margin-top: 10px;
    width: 100%;
  }

  .property-card {
    flex-direction: column;
  }

  .property-image {
    width: 100%;
    height: 200px;
  }

  .property-details {
    padding: 15px;
  }

  .landlord {
    flex-wrap: wrap;
    gap: 10px;
  }

  .contact-btn {
    width: 100%;
    margin-top: 10px;
  }

  /* 危險區塊 */
  .danger-zone {
    padding: 20px;
    margin: 20px 0;
  }
  
  .danger-btn {
    width: 100%;
    justify-content: center;
  }


  .assistant-feature {
    flex-direction: column;
    align-items: flex-start;
    padding: 12px;
  }

  .feature-icon {
    margin-bottom: 12px;
  }

  .maintenance-item {
    padding: 15px;
  }

  .maintenance-status {
    position: static;
    display: inline-block;
    margin-bottom: 10px;
  }

  .maintenance-header {
    flex-direction: column;
    padding-right: 0;
  }

  .maintenance-photos {
    flex-wrap: wrap;
  }

  .maintenance-photos img {
    width: calc(50% - 5px);
    height: 120px;
  }
}

@media (max-width: 480px) {
  .profile-meta {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }

  .profile-info h1 {
    font-size: 1.5rem;
    flex-direction: column;
    align-items: center;
  }

  .verified {
    margin-top: 5px;
  }

  .lease-details {
    flex-direction: column;
    gap: 10px;
  }

  .landlord {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }

  .landlord-avatar {
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  .settings-btn,
  .field-action-group button {
    width: auto;  /* 改為自動寬度 */
    align-self: flex-end;  /* 靠右對齊 */
  }
  
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
    content: "";
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

  .field-action-group {
    display: flex;
    align-items: center;
    gap: 20px;
    width: 100%;
  }

  .field-action-group .editable-field {
    flex: 1;
    margin-right: 10px;
  }

  .field-action-group button {
    white-space: nowrap; /* 確保按鈕文字不換行 */
    min-width: 80px; /* 設置最小寬度 */
    justify-content: center;
  }

  .verify-btn {
    background-color: #4caf50;
    color: white;
    white-space: nowrap;
    min-width: 80px;
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .verify-btn:hover {
    background-color: #43a047;
    transform: translateY(-1px);
  }

  .settings-btn {
    height: 32px;
    background-color: #007bff;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0 15px;
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
    font-size: 0.9rem;
  }

.address svg {
  min-width: 16px;
  height: 16px;
}

  .password-field {
    display: flex;
    align-items: center;
    gap: 20px;
    width: 100%;
  }

  .masked-password {
    flex: 1;
    letter-spacing: 2px;
    font-weight: bold;
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
    transition: all 0.3s ease; /* 添加過渡效果 */
    position: relative; /* 為點擊效果添加定位 */
    overflow: hidden; /* 防止漣漪效果溢出 */
  }


  /* 租屋操作按鈕樣式優化 */
.lease-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 15px;
  padding: 20px 0;
}

.contact-btn:hover {
  background-color: #0056b3; /* 深一點的藍色 */
  transform: translateY(-2px); /* 輕微上浮 */
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2); /* 添加陰影 */
}

/* 點擊效果 */
.contact-btn:active {
  transform: translateY(0); /* 回到原位 */
  box-shadow: 0 2px 6px rgba(0, 123, 255, 0.1); /* 縮小陰影 */
  background-color: #0050a6; /* 更深的藍色 */
}

/* 添加漣漪效果 */
.contact-btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.3s, height 0.3s;
}

.contact-btn:active::after {
  width: 200px;
  height: 200px;
}

.action-btn {
  padding: 15px 20px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #EBF3FE 0%, #E0EEFE 100%);
  color: #1565C0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* 懸浮效果 */
.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(21, 101, 192, 0.15);
  filter: brightness(1.05);
}

.action-btn.report,
.action-btn.extend,
.action-btn.terminate,
.action-btn.receipt {
  background: linear-gradient(135deg, #EBF3FE 0%, #E0EEFE 100%);
  color: #1565C0;
}



/* 響應式設計 */

@media (max-width: 480px) {
  /* 個人資料頭部 */
  .profile-meta {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }

  .profile-info h1 {
    font-size: 1.5rem;
    flex-direction: column;
    align-items: center;
  }

  .verified {
    margin-top: 5px;
  }

  /* 租屋操作按鈕 */
  .lease-actions {
    grid-template-columns: 1fr;
  }

  /* 租屋詳情 */
  .lease-details {
    flex-direction: column;
    gap: 10px;
  }

  /* 房東資訊 */
  .landlord {
    flex-direction: column;
    text-align: center;
  }

  .landlord-avatar {
    margin: 0 auto 10px;
  }

  /* 設置欄位 */
  .field-action-group {
    flex-direction: column;
    gap: 10px;
  }

  .settings-btn,
  .field-action-group button {
    width: 100%;
  }

  /* 危險區域 */
  .danger-zone {
    padding: 15px;
    margin: 15px 0;
  }

  .danger-btn {
    width: 100%;
  }

  /* 歷史記錄項目 */
  .history-item {
    flex-direction: column;
    gap: 10px;
    padding: 15px;
  }

  .history-date {
    width: 100%;
  }

  /* 管理員功能 */
  .admin-features {
    grid-template-columns: 1fr;
  }

  .login-history-item {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }

  .login-time,
  .login-device,
  .login-ip {
    width: 100%;
  }

  .landlord {
    flex-direction: row;  /* 改為水平排列 */
    align-items: center;
    justify-content: flex-start;  /* 左對齊 */
    text-align: left;  /* 文字左對齊 */
    gap: 12px;  /* 元素之間的間距 */
  }

  .landlord-avatar {
    margin: 0;  /* 移除原本的 margin */
    width: 40px;  /* 稍微縮小頭像 */
    height: 40px;
  }

  .contact-btn {
    margin: 0;  /* 移除原本的 margin */
    padding: 8px 12px;  /* 稍微縮小按鈕 */
    font-size: 0.9rem;  /* 稍微縮小文字 */
    white-space: nowrap;  /* 防止文字換行 */
  }

  .landlord > div {
    flex: 1;  /* 讓中間的文字資訊可以自適應寬度 */
    min-width: 0;  /* 防止文字溢出 */
  }

  .landlord-name,
  .landlord-contact {
    text-align: left;  /* 確保文字左對齊 */
  }
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

  .history-address,
  .history-rent {
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
    background-color: #c4e1ff;
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
    padding: 35px;
    max-width: 900px;
    margin: 0 auto;
  }

  .settings-section {
    background: #ffffff;
    border-radius: 12px;
    padding: 25px;
    margin-bottom: 30px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

.settings-section h2 {
  font-size: 1.5rem;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #eef2f7;
  font-weight: 600;
  color: #2c3e50;
}

.settings-item {
  display: flex;
  align-items: flex-start;
  padding: 20px 0;
  border-bottom: 1px solid #f5f7fa;
  gap: 15px;
}

  .settings-item:last-child {
    border-bottom: none;
  }

  .settings-item:hover {
    background-color: #f8fafc;
  }

  .settings-label {
    width: 180px;
    font-weight: 600;
    color: #374151;
    font-size: 0.95rem;
  }

  .settings-content {
    flex: 1;
    display: flex;
    align-items: center;
    gap: 20px;
  }

  /* 開關按鈕樣式優化 */
  .switch {
    position: relative;
    display: inline-block;
    width: 52px;
    height: 26px;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #e5e7eb;
    transition: 0.3s;
    border-radius: 34px;
  }

  .slider:before {
    position: absolute;
    content: "";
    height: 18px;
    width: 18px;
    left: 4px;
    bottom: 4px;
    background-color: white;
    transition: 0.3s;
    border-radius: 50%;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }

  input:checked + .slider {
    background-color: #3b82f6;
  }

  input:checked + .slider:before {
    transform: translateX(26px);
  }

  /* 下拉選單樣式優化 */
  .settings-select {
    padding: 10px 15px;
    border-radius: 8px;
    border: 1px solid #e2e8f0;
    width: 200px;
    font-size: 0.95rem;
    color: #4b5563;
    background-color: white;
    transition: all 0.2s ease;
  }

  .settings-select:hover {
    border-color: #cbd5e1;
  }

  .settings-select:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  /* 按鈕樣式優化 */
  .settings-btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .settings-btn.highlight {
    background-color: #3b82f6;
    color: white;
  }

  .settings-btn.highlight:hover {
    background-color: #2563eb;
    transform: translateY(-1px);
  }

  .settings-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

/* 租屋小幫手樣式優化 */
.user-assistant {
  background: linear-gradient(145deg, #ffffff, #f8f9fa);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.user-assistant h2 {
  font-size: 1.5rem;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #eef2f7;
  font-weight: 600;
  color: #2c3e50;
}

.assistant-feature {
  display: flex;
  gap: 16px;
  padding: 16px;
  background: white;
  border-radius: 12px;
  margin-bottom: 16px;
  transition: transform 0.3s ease;
}

.assistant-feature:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
}

.feature-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: #f0f9ff;
  border-radius: 12px;
  font-size: 24px;
}

.feature-content {
  flex: 1;
}

.feature-content h4 {
  margin: 0 0 8px 0;
  color: #1e40af;
  font-size: 1.1rem;
}

.feature-content p {
  color: #64748b;
  margin: 0 0 12px 0;
  line-height: 1.5;
}

.feature-action-btn {
  background: transparent;
  color: #3b82f6;
  border: 1px solid #3b82f6;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.feature-action-btn:hover {
  background: #3b82f6;
  color: white;
  transform: translateY(-1px);
}

/* 危險區域 */
.danger-zone {
  margin-top: 40px;
  padding: 30px;
  background: #fff5f5;
  border-radius: 12px;
  border: 2px solid #fecaca;
  position: relative;
}

.danger-zone h2 {
  font-size: 1.5rem;
  margin-bottom: 25px;
  padding-bottom: 15px;
  border-bottom: 2px solid #eef2f7;
  font-weight: 600;
  color: #dc2626;
}

.danger-zone p {
  color: #666;
  margin-bottom: 20px;
  font-size: 0.95rem;
  line-height: 1.5;
}

.danger-btn {
  background-color: #dc2626;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.danger-btn:hover {
  background-color: #b91c1c;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.2);
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
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-left: auto;
    transition: background-color 0.2s;
  }

  .settings-btn.highlight {
    background-color: #007bff;
    color: white;
  }

  .settings-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
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
    transition: 0.4s;
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
    transition: 0.4s;
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

  .danger-btn {
    background-color: #dc3545;
    padding: 5px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    margin-left: auto;
    transition: background-color 0.2s;
  }

  .danger-btn:hover {
    background-color: #c82333;
  }

  /* 添加管理員相關樣式 */
  .admin-badge {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #b91c1c;
    font-weight: 500;
    background-color: rgba(185, 28, 28, 0.1);
    padding: 4px 12px;
    border-radius: 6px;
  }

  .admin-badge svg {
    min-width: 16px;
    height: 16px;
  }

  .admin-dashboard-btn {
    position: absolute;
    top: 75px;
    right: 30px;
    padding: 10px 20px;
    background-color: #b91c1c;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 5px;
    transition: background-color 0.2s;
  }

  .admin-dashboard-btn:hover {
    background-color: #991b1b;
  }

  .admin-features {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
  }

  .admin-feature-card {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 20px;
    display: flex;
    align-items: flex-start;
    gap: 15px;
    transition: transform 0.2s, box-shadow 0.2s;
  }

  .admin-feature-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  }

  .admin-feature-icon {
    font-size: 2rem;
    background-color: #f0f0f0;
    width: 50px;
    height: 50px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .admin-feature-content {
    flex: 1;
  }

  .admin-feature-content h3 {
    margin: 0 0 10px 0;
    font-size: 1.2rem;
  }

  .admin-feature-content p {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 15px;
  }

  .admin-feature-btn {
    background-color: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .admin-feature-btn:hover {
    background-color: #0056b3;
  }

  .admin-login-history {
    margin-top: 30px;
  }

  .admin-login-history h3 {
    font-size: 1.1rem;
    margin-bottom: 15px;
  }

  .login-history-item {
    display: flex;
    align-items: center;
    padding: 12px 15px;
    background-color: #f8f9fa;
    border-radius: 6px;
    margin-bottom: 10px;
  }

  .login-time {
    width: 180px;
    font-weight: 500;
  }

  .login-device {
    flex: 1;
  }

  .login-ip {
    width: 120px;
    color: #666;
  }

  .login-status {
    width: 60px;
    text-align: center;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.85rem;
  }

  .login-status.success {
    background-color: #d1fae5;
    color: #047857;
  }

  .login-status.failed {
    background-color: #fee2e2;
    color: #b91c1c;
  }

  .loading-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-right: 5px;
  }

  .modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  animation: fadeIn 0.3s ease;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.contact-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 12px;
  transition: background-color 0.2s ease;
}

.contact-info-item:hover {
  background: #f0f0f0;
}

.contact-info-item:last-child {
  margin-bottom: 0;
}

/* 動畫效果 */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
