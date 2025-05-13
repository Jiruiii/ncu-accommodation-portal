<template>
  <div class="profile-page">
    <!-- 保留現有的個人資料頭部 -->
    <div class="profile-header">
      <div class="profile-avatar">
        <img
          :src="
            user.profile_image ||
            'https://randomuser.me/api/portraits/women/65.jpg'
          "
          alt="用戶頭像"
        />
        <button class="edit-avatar-btn">
          <i>📷</i>
        </button>
        <input
          type="file"
          ref="fileInput"
          style="display: none"
          accept="image/*"
          @change="uploadAvatar"
        />
      </div>
      <div class="profile-info">
        <h1>
          {{ user.username }}
          <span class="verified" v-if="user.is_verified">✓ 已驗證</span>
        </h1>
        <div class="profile-meta">
          <div><i>📧</i> {{ user.email }}</div>
          <div v-if="user.phone"><i>📱</i> {{ user.phone }}</div>
          <div v-if="user.school_email"><i>🏫</i> {{ user.school_email }}</div>
          <!-- 新增管理員或超級管理員角色標記 -->
          <div v-if="isAdmin" class="admin-badge">
            <i>👑</i>
            {{ user.user_role === "superuser" ? "超級管理員" : "管理員" }}
          </div>
        </div>
      </div>
      <button class="edit-profile-btn">編輯個人資料</button>
      <!-- 新增管理員後台入口按鈕 -->
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
              <div class="address"><i>📍</i> 中壢區中大路300號附近</div>
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
      </div>

      <!-- 我的帳戶設置 -->
      <div v-if="activeTab === 'settings'" class="account-settings">
        <div class="settings-section">
          <h2>帳戶安全</h2>
          <div class="settings-item">
            <div class="settings-label">中央大學 Portal 綁定</div>
            <div class="settings-content">
              <span v-if="user.has_portal_id">已綁定</span>
              <span v-else>未綁定</span>
              <span class="verified-tag" v-if="user.has_portal_id"
                >學生身分認證</span
              >
              <button
                class="settings-btn"
                @click="bindPortalAccount"
                :disabled="isProcessingPortal"
              >
                <span v-if="isProcessingPortal" class="loading-spinner"></span>
                {{ user.has_portal_id ? "取消綁定" : "立即綁定" }}
              </button>
            </div>
          </div>

          <div class="settings-item">
            <div class="settings-label">電子郵件</div>
            <div class="settings-content">
              <span>{{ user.email }}</span>
              <button class="settings-btn" @click="showEmailModal = true">
                修改
              </button>
            </div>
          </div>

          <div class="settings-item">
            <div class="settings-label">校園郵箱</div>
            <div class="settings-content">
              <span v-if="user.school_email">{{ user.school_email }}</span>
              <span v-else>未綁定</span>
            </div>
          </div>

          <div class="settings-item">
            <div class="settings-label">手機號碼</div>
            <div class="settings-content">
              <span>{{ user.phone || "尚未設置" }}</span>
              <button class="settings-btn" @click="showPhoneModal = true">
                {{ user.phone ? "修改" : "設置" }}
              </button>
            </div>
          </div>

          <div class="settings-item">
            <div class="settings-label">密碼</div>
            <div class="settings-content">
              <span>••••••••</span>
              <span class="last-updated">定期更新密碼可提高帳戶安全性</span>
              <button class="settings-btn" @click="showPasswordModal = true">
                修改
              </button>
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

          <!-- 添加小幫手功能 -->
          <div class="user-assistant">
            <div class="assistant-header">
              <h3>租屋小幫手</h3>
              <button class="toggle-assistant-btn">開啟</button>
            </div>
            <div class="assistant-feature">
              <div class="feature-icon">🔔</div>
              <div class="feature-content">
                <h4>租約到期提醒</h4>
                <p>
                  您的租約將於 45 天後到期，建議您盡快聯繫房東討論續約事宜。
                </p>
                <button class="feature-action-btn">聯繫房東</button>
              </div>
            </div>
            <div class="assistant-feature">
              <div class="feature-icon">💡</div>
              <div class="feature-content">
                <h4>租屋建議</h4>
                <p>
                  根據您的搜尋歷史，我們推薦您查看近中央大學的 3 間新上架套房。
                </p>
                <button class="feature-action-btn">查看推薦</button>
              </div>
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
          <button class="danger-btn">刪除帳戶</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, reactive } from "vue";
  import { useRouter } from "vue-router";
  import apiService from "@/services/api";

  export default {
    name: "ProfilePage",
    setup() {
      const router = useRouter();
      const activeTab = ref("housing");
      const loading = ref(true);
      const error = ref(null);
      const showEditModal = ref(false);
      const showPasswordModal = ref(false);
      const showBindPortalModal = ref(false);
      const isProcessingPortal = ref(false);

      // 個人資料編輯表單
      const editForm = reactive({
        username: "",
        email: "",
        phone: "",
        bio: "",
      });

      // 密碼修改表單
      const passwordForm = reactive({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      });

      const user = ref({
        username: "Loading...",
        email: "Loading...",
        user_role: "",
        is_verified: false,
        phone: "",
        profile_image: null,
        has_portal_id: false,
        school_email: "",
        user_id: null,
      });

      // 確定标签應該顯示哪些
      const tabs = computed(() => {
        const baseTabs = [
          { id: "housing", name: "我的租屋資訊" },
          { id: "settings", name: "帳戶設置" },
        ];

        // 如果用户有發佈權限則添加「我的發布」標籤
        if (["landlord", "admin", "superuser"].includes(user.value.user_role)) {
          baseTabs.splice(1, 0, { id: "posts", name: "我的發布" });
        }

        return baseTabs;
      });

      // 計算屬性：檢查用戶是否為管理員或超級管理員
      const isAdmin = computed(() => {
        return (
          user.value.is_admin ||
          user.value.is_superuser ||
          ["admin", "superuser"].includes(user.value.user_role)
        );
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

      // 導航到用戶管理頁面
      const goToUserManagement = () => {
        router.push("/admin/users");
      };

      // 導航到數據分析頁面
      const goToAnalytics = () => {
        router.push("/admin/analytics");
      };

      // 獲取用戶資料
      const fetchUserData = async () => {
        try {
          loading.value = true;
          error.value = null;

          // 從API獲取用戶資料
          const response = await apiService.users.getProfile();
          console.log("獲取用戶資料:", response);

          if (response && response.user) {
            user.value = response.user;
          } else {
            // 如果API請求沒有返回用戶數據，嘗試從本地存儲獲取
            const userStr = localStorage.getItem("user");
            if (userStr) {
              user.value = JSON.parse(userStr);
            } else {
              error.value = "無法獲取用戶資料";
            }
          }
        } catch (err) {
          console.error("獲取用戶資料失敗:", err);
          error.value = "獲取資料失敗，請稍後重試";

          // 如果API請求失敗，嘗試從本地存儲獲取
          const userStr =
            localStorage.getItem("user") || sessionStorage.getItem("user");
          if (userStr) {
            user.value = JSON.parse(userStr);
          }
        } finally {
          loading.value = false;
        }
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

      // 提交個人資料更新
      const submitProfileUpdate = async () => {
        try {
          const response = await apiService.users.updateProfile({
            username: editForm.username,
            email: editForm.email,
            phone: editForm.phone,
            bio: editForm.bio,
          });

          if (response && response.user) {
            user.value = { ...user.value, ...response.user };
            alert("個人資料已更新");
          }

          showEditModal.value = false;
        } catch (err) {
          console.error("更新個人資料失敗:", err);
          alert(`更新失敗: ${err.message || "未知錯誤"}`);
        }
      };

      // 上傳頭像
      const uploadAvatar = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append("image", file);

        try {
          const response = await apiService.users.uploadProfileImage(formData);

          if (response && response.profile_image) {
            user.value.profile_image = response.profile_image;
            alert("頭像已更新");
          }
        } catch (err) {
          console.error("上傳頭像失敗:", err);
          alert(`上傳失敗: ${err.message || "未知錯誤"}`);
        }
      };

      // 修改密碼
      const changePassword = async () => {
        // 驗證密碼
        if (passwordForm.newPassword !== passwordForm.confirmPassword) {
          alert("兩次輸入的密碼不一致");
          return;
        }

        if (passwordForm.newPassword.length < 8) {
          alert("新密碼長度不得少於8個字符");
          return;
        }

        try {
          await apiService.users.changePassword({
            current_password: passwordForm.currentPassword,
            new_password: passwordForm.newPassword,
          });

          alert("密碼已成功修改");
          showPasswordModal.value = false;

          // 清空表單
          passwordForm.currentPassword = "";
          passwordForm.newPassword = "";
          passwordForm.confirmPassword = "";
        } catch (err) {
          console.error("修改密碼失敗:", err);
          alert(`修改失敗: ${err.message || "未知錯誤"}`);
        }
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
              user.value.has_portal_id = false;
              user.value.school_email = null;

              try {
                const userStr = localStorage.getItem("user");
                if (userStr) {
                  const userData = JSON.parse(userStr);
                  userData.has_portal_id = false;
                  userData.school_email = null;
                  localStorage.setItem("user", JSON.stringify(userData));
                }
              } catch (e) {
                console.error("更新本地存儲失敗:", e);
              }

              alert("已成功解除綁定 Portal 帳號");
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
          localStorage.removeItem("user");
          sessionStorage.removeItem("user");
          router.push("/login");
        } catch (err) {
          console.error("刪除帳戶失敗:", err);
          alert(`刪除失敗: ${err.message || "未知錯誤"}`);
        }
      };

      // 生命週期鉤子
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
        editForm,
        passwordForm,
        openEditModal,
        submitProfileUpdate,
        uploadAvatar,
        changePassword,
        bindPortalAccount,
        deleteAccount,
        goToAdminDashboard,
        goToUserManagement,
        goToAnalytics,
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
    align-items: center;
    gap: 20px;
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

  /* 添加管理員相關樣式 */
  .admin-badge {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #b91c1c;
    font-weight: 500;
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
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
