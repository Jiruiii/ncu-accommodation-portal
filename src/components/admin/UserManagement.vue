<template>
  <div class="user-management">
    <div class="page-header">
      <h1>用戶管理</h1>
      <!-- 移除新增管理員按鈕 -->
    </div>

    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.value"
        @click="activeTab = tab.value"
        :class="{ active: activeTab === tab.value }"
      >
        {{ tab.label }}
        <span class="badge" v-if="tab.count !== undefined">{{
          tab.count
        }}</span>
      </button>
    </div>

    <div class="filters">
      <div class="search-box">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜尋用戶..."
          @input="handleSearch"
        />
        <span class="material-symbols-outlined">search</span>
      </div>

      <div class="filter-actions">
        <select v-model="sortBy" @change="loadUsers">
          <option value="created_at">註冊日期</option>
          <option value="last_login">最後登入</option>
          <option value="username">用戶名</option>
        </select>

        <select v-model="sortDirection" @change="loadUsers">
          <option value="desc">降序</option>
          <option value="asc">升序</option>
        </select>
      </div>
    </div>

    <div class="users-table">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>用戶名</th>
            <th>電子郵件</th>
            <th>角色</th>
            <th>狀態</th>
            <th>註冊日期</th>
            <th>最後登入</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in filteredUsers" :key="user.user_id">
            <td>{{ user.user_id }}</td>
            <td>
              <div class="user-info">
                <span class="avatar" v-if="user.profile_image">
                  <img :src="user.profile_image" :alt="user.username" />
                </span>
                <span class="avatar" v-else>
                  {{ getInitials(user.username) }}
                </span>
                <span>{{ user.username }}</span>
              </div>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span :class="['role-badge', getRoleClass(user.user_role)]">
                {{ formatRole(user.user_role) }}
              </span>
            </td>
            <td>
              <span
                :class="[
                  'status-badge',
                  user.is_active ? 'active' : 'inactive',
                ]"
              >
                {{ user.is_active ? "活躍" : "停用" }}
              </span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>{{ formatDate(user.last_login) }}</td>
            <td class="actions">
              <!-- 只有超級管理員可以編輯用戶角色 -->
              <button
                v-if="isSuperUser"
                @click="openEditModal(user)"
                class="edit-btn"
                title="編輯用戶"
              >
                <span class="material-symbols-outlined">edit</span>
              </button>

              <!-- 所有管理員都可以啟用/禁用用戶 -->
              <button
                @click="toggleUserStatus(user)"
                :class="[
                  'toggle-btn',
                  user.is_active ? 'deactivate' : 'activate',
                ]"
                :title="user.is_active ? '停用帳號' : '啟用帳號'"
              >
                <span class="material-symbols-outlined">
                  {{ user.is_active ? "block" : "check_circle" }}
                </span>
              </button>

              <!-- 刪除按鈕只對超級管理員顯示 -->
              <button
                v-if="isSuperUser"
                @click="openDeleteModal(user)"
                class="delete-btn"
                title="刪除用戶"
              >
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>

          <tr v-if="filteredUsers.length === 0">
            <td colspan="8" class="no-data">
              <div v-if="loading">
                <div class="spinner"></div>
                載入中...
              </div>
              <div v-else>沒有找到符合條件的用戶</div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button
        :disabled="currentPage === 1"
        @click="changePage(currentPage - 1)"
      >
        <span class="material-symbols-outlined">navigate_before</span>
      </button>

      <span>{{ currentPage }} / {{ totalPages }}</span>

      <button
        :disabled="currentPage === totalPages"
        @click="changePage(currentPage + 1)"
      >
        <span class="material-symbols-outlined">navigate_next</span>
      </button>
    </div>

    <!-- 編輯用戶模態框 - 主要用於權限管理 -->
    <div v-if="showEditModal" class="modal-overlay">
      <div class="modal-container">
        <div class="modal-header">
          <h2>編輯用戶權限</h2>
          <button @click="showEditModal = false" class="close-btn">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="modal-body">
          <form @submit.prevent="updateUser">
            <div class="form-group">
              <label>用戶資訊</label>
              <div class="user-detail-box">
                <div class="user-detail">
                  <strong>用戶名:</strong> {{ editingUser.username }}
                </div>
                <div class="user-detail">
                  <strong>郵箱:</strong> {{ editingUser.email }}
                </div>
              </div>
            </div>

            <!-- 角色選擇 - 只有超級管理員可以修改 -->
            <div class="form-group">
              <label for="edit-role">角色</label>
              <select
                id="edit-role"
                v-model="editingUser.user_role"
                :disabled="!isSuperUser"
                required
              >
                <option
                  value="superuser"
                  v-if="
                    isSuperUser && currentUser.user_id !== editingUser.user_id
                  "
                >
                  超級管理員
                </option>
                <option value="admin">系統管理員</option>
                <option value="moderator">內容審核員</option>
                <option value="student">學生</option>
                <option value="landlord">房東</option>
              </select>
              <span class="permission-hint" v-if="!isSuperUser">
                只有超級管理員可以修改用戶角色
              </span>
            </div>

            <div class="form-group">
              <label for="edit-status">帳號狀態</label>
              <select id="edit-status" v-model="editingUser.is_active">
                <option :value="true">活躍</option>
                <option :value="false">停用</option>
              </select>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                @click="showEditModal = false"
                class="cancel-btn"
              >
                取消
              </button>
              <button type="submit" class="submit-btn">更新權限</button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 刪除確認模態框 -->
    <div v-if="showDeleteModal" class="modal-overlay">
      <div class="modal-container modal-sm">
        <div class="modal-header">
          <h2>刪除用戶</h2>
          <button @click="showDeleteModal = false" class="close-btn">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <div class="modal-body">
          <p class="confirmation-message">
            確定要刪除用戶 <strong>{{ userToDelete.username }}</strong
            >？此操作不可逆。
          </p>

          <div class="danger-zone">
            <div class="checkbox-group">
              <input
                type="checkbox"
                id="confirm-delete"
                v-model="deleteConfirmed"
              />
              <label for="confirm-delete">我確認要永久刪除此用戶</label>
            </div>
          </div>

          <div class="modal-footer">
            <button
              type="button"
              @click="showDeleteModal = false"
              class="cancel-btn"
            >
              取消
            </button>
            <button
              type="button"
              @click="deleteUser"
              class="delete-btn"
              :disabled="!deleteConfirmed"
            >
              刪除用戶
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, computed, onMounted, watch } from "vue";
  import apiService from "@/services/api";

  export default {
    setup() {
      // 狀態變數
      const users = ref([]);
      const loading = ref(true);
      const currentPage = ref(1);
      const totalPages = ref(1);
      const totalUsers = ref(0);
      const searchQuery = ref("");
      const activeTab = ref("all");
      const sortBy = ref("created_at");
      const sortDirection = ref("desc");

      // 模態框狀態
      const showCreateModal = ref(false);
      const showEditModal = ref(false);
      const showDeleteModal = ref(false);
      const showResetPassword = ref(false);
      const deleteConfirmed = ref(false);

      const currentUser = ref({
        user_id: null,
        user_role: ''
      });

      // 用戶資料
      const newUser = ref({
        username: "",
        email: "",
        password: "",
        confirmPassword: "",
        user_role: "admin",
        phone: "",
      });

      const editingUser = ref({});
      const userToDelete = ref({});

      // 標籤頁
      const tabs = computed(() => [
        { label: "所有用戶", value: "all", count: totalUsers.value },
        { label: "管理員", value: "admin,superuser" },
        { label: "學生", value: "student" },
        { label: "房東", value: "landlord" },
        { label: "已停用", value: "inactive" },
      ]);

      // 根據當前標籤和搜索過濾用戶
      const filteredUsers = computed(() => {
        let filtered = [...users.value];

        // 按標籤過濾
        if (activeTab.value !== "all") {
          if (activeTab.value === "inactive") {
            filtered = filtered.filter((user) => !user.is_active);
          } else if (activeTab.value === "admin,superuser") {
            // 特殊處理管理員標籤，包含 admin 和 superuser 角色
            filtered = filtered.filter(
              (user) =>
                (user.user_role === "admin" ||
                  user.user_role === "superuser") &&
                user.is_active
            );
          } else {
            // 其他標籤正常過濾
            filtered = filtered.filter(
              (user) => user.user_role === activeTab.value && user.is_active
            );
          }
        }

        // 按搜索詞過濾
        if (searchQuery.value.trim()) {
          const query = searchQuery.value.toLowerCase();
          filtered = filtered.filter(
            (user) =>
              user.username.toLowerCase().includes(query) ||
              user.email.toLowerCase().includes(query)
          );
        }

        return filtered;
      });

      const getCurrentUser = async () => {
        try {
          const userStr = sessionStorage.getItem('user');
          if (userStr) {
            currentUser.value = JSON.parse(userStr);
          } else {
            // 如果本地存儲中沒有用戶信息，嘗試從API獲取
            try {
              const response = await apiService.auth.status();
              if (response.authenticated) {
                currentUser.value = response.user;
              }
            } catch (error) {
              console.error("獲取用戶狀態失敗:", error);
            }
          }
        } catch (error) {
          console.error("獲取當前用戶信息失敗:", error);
        }
      };

      const isSuperUser = computed(() => {
        return currentUser.value.user_role === 'superuser';
      });

      // 載入用戶數據
      const loadUsers = async () => {
        loading.value = true;
        try {
          const params = {
            page: currentPage.value,
            per_page: 10,
            sort_by: sortBy.value,
            sort_direction: sortDirection.value,
          };

          // 只有當標籤值是特定值時才添加參數
          if (activeTab.value !== "all" && activeTab.value !== "inactive") {
            params.role = activeTab.value;
          }

          if (activeTab.value === "inactive") {
            params.status = "inactive";
          }

          const response = await apiService.admin.getUsers(params);
          if (response && response.items) {
            users.value = response.items;
            totalUsers.value = response.total || 0;
            totalPages.value = response.pages || 1;
          } else {
            users.value = [];
            console.error("API 返回了意外的數據格式");
          }
        } catch (error) {
          console.error("載入用戶失敗:", error);
          users.value = []; // 清空數據以防顯示舊數據
        } finally {
          loading.value = false;
        }
      };

      // 搜索處理函數
      const handleSearch = () => {
        currentPage.value = 1;
        loadUsers();
      };

      // 分頁處理
      const changePage = (page) => {
        currentPage.value = page;
        loadUsers();
      };

      // 模態框控制
      const openCreateModal = () => {
        // 重置表單
        newUser.value = {
          username: "",
          email: "",
          password: "",
          confirmPassword: "",
          user_role: "admin",
          phone: "",
        };
        showCreateModal.value = true;
      };

      const openEditModal = (user) => {
        editingUser.value = { ...user };
        showResetPassword.value = false;
        showEditModal.value = true;
      };

      const openDeleteModal = (user) => {
        userToDelete.value = user;
        deleteConfirmed.value = false;
        showDeleteModal.value = true;
      };

      // 用戶操作
      const createUser = async () => {
        // 驗證密碼
        if (newUser.value.password !== newUser.value.confirmPassword) {
          alert("密碼不一致");
          return;
        }

        // 驗證密碼強度
        const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        if (!passwordPattern.test(newUser.value.password)) {
          alert("密碼至少需要8位，且包含字母和數字");
          return;
        }

        try {
          const userData = { ...newUser.value };
          delete userData.confirmPassword;

          await apiService.admin.createUser(userData);
          showCreateModal.value = false;
          loadUsers();
          alert("用戶創建成功");
        } catch (error) {
          console.error("創建用戶失敗:", error);
          alert(`創建用戶失敗: ${error.message}`);
        }
      };

      const updateUser = async () => {
        try {
          const userData = { ...editingUser.value };

          // 如果選擇重設密碼且有輸入新密碼
          if (showResetPassword.value && userData.new_password) {
            // 驗證密碼強度
            const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
            if (!passwordPattern.test(userData.new_password)) {
              alert("新密碼至少需要8位，且包含字母和數字");
              return;
            }
            userData.password = userData.new_password;
          }

          // 刪除不需要的欄位
          delete userData.new_password;

          await apiService.admin.updateUser(userData.user_id, userData);
          showEditModal.value = false;
          loadUsers();
          alert("用戶資料已更新");
        } catch (error) {
          console.error("更新用戶失敗:", error);
          alert(`更新用戶失敗: ${error.message}`);
        }
      };

      const toggleUserStatus = async (user) => {
        try {
          const newStatus = !user.is_active;
          await apiService.admin.updateUser(user.user_id, {
            is_active: newStatus,
          });

          // 更新本地用戶數據
          user.is_active = newStatus;
          alert(`用戶已${newStatus ? "啟用" : "停用"}`);
        } catch (error) {
          console.error("更新用戶狀態失敗:", error);
          alert(`操作失敗: ${error.message}`);
        }
      };

      const deleteUser = async () => {
        if (!deleteConfirmed.value) return;

        try {
          await apiService.admin.deleteUser(userToDelete.value.user_id);
          showDeleteModal.value = false;
          loadUsers();
          alert("用戶已刪除");
        } catch (error) {
          console.error("刪除用戶失敗:", error);
          alert(`刪除失敗: ${error.message}`);
        }
      };

      // 輔助格式化函數
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

      const formatRole = (role) => {
        const roles = {
          superuser: "超級管理員",
          admin: "系統管理員",
          moderator: "內容審核員",
          student: "學生",
          landlord: "房東",
        };
        return roles[role] || role;
      };

      const getRoleClass = (role) => {
        return role.toLowerCase();
      };

      const getInitials = (name) => {
        if (!name) return "";
        return name
          .split(" ")
          .map((n) => n[0])
          .join("")
          .toUpperCase()
          .substring(0, 2);
      };

      // 當標籤或排序改變時重新載入數據
      watch([activeTab, sortBy, sortDirection], () => {
        currentPage.value = 1;
        loadUsers();
      });

      onMounted(() => {
        loadUsers();
        getCurrentUser();
      });

      return {
        users,
        filteredUsers,
        loading,
        currentPage,
        totalPages,
        totalUsers,
        searchQuery,
        activeTab,
        tabs,
        sortBy,
        sortDirection,
        showCreateModal,
        showEditModal,
        showDeleteModal,
        showResetPassword,
        deleteConfirmed,
        newUser,
        editingUser,
        userToDelete,
        loadUsers,
        handleSearch,
        changePage,
        openCreateModal,
        openEditModal,
        openDeleteModal,
        createUser,
        updateUser,
        toggleUserStatus,
        deleteUser,
        formatDate,
        formatRole,
        getRoleClass,
        getInitials,
        isSuperUser,
        currentUser,
      };
    },
  };
</script>

<style scoped>
  .user-management {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }

  h1 {
    margin: 0;
    font-size: 24px;
    font-weight: 600;
  }

  .create-button {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background-color: #0ca678;
    color: white;
    border: none;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .create-button:hover {
    background-color: #099268;
  }

  .tabs {
    display: flex;
    border-bottom: 1px solid #e2e8f0;
    margin-bottom: 24px;
    overflow-x: auto;
    padding-bottom: 1px;
  }

  .tabs button {
    padding: 10px 20px;
    background: none;
    border: none;
    font-size: 14px;
    font-weight: 500;
    color: #4a5568;
    cursor: pointer;
    position: relative;
    white-space: nowrap;
  }

  .tabs button.active {
    color: #3a86ff;
    font-weight: 600;
  }

  .tabs button.active::after {
    content: "";
    position: absolute;
    bottom: -1px;
    left: 0;
    width: 100%;
    height: 3px;
    background-color: #3a86ff;
  }

  .badge {
    display: inline-block;
    padding: 2px 6px;
    background-color: #f1f5f9;
    color: #64748b;
    border-radius: 12px;
    font-size: 12px;
    margin-left: 5px;
  }

  .filters {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 10px;
  }

  .search-box {
    position: relative;
    max-width: 300px;
  }

  .search-box input {
    padding: 10px 16px 10px 36px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
    width: 100%;
  }

  .search-box input:focus {
    outline: none;
    border-color: #3a86ff;
    box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
  }

  .search-box .material-symbols-outlined {
    position: absolute;
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    color: #94a3b8;
    font-size: 18px;
  }

  .filter-actions {
    display: flex;
    gap: 10px;
  }

  .filter-actions select {
    padding: 10px 16px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
    background-color: white;
    cursor: pointer;
  }

  .filter-actions select:focus {
    outline: none;
    border-color: #3a86ff;
    box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
  }

  .users-table {
    overflow-x: auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
  }

  table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
  }

  thead {
    background-color: #f8fafc;
  }

  th {
    padding: 16px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
  }

  td {
    padding: 16px;
    border-bottom: 1px solid #f1f5f9;
  }

  tbody tr:hover {
    background-color: #f8fafc;
  }

  .user-info {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: #e2e8f0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    overflow: hidden;
  }

  .avatar img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .role-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .role-badge.admin {
    background-color: #ede9fe;
    color: #7c3aed;
  }

  .role-badge.moderator {
    background-color: #e0f2fe;
    color: #0ea5e9;
  }

  .role-badge.student {
    background-color: #e0f2fe;
    color: #0284c7;
  }

  .role-badge.landlord {
    background-color: #fef3c7;
    color: #d97706;
  }

  .role-badge.superuser {
    background-color: #fee2e2;
    color: #dc2626;
    font-weight: 600;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }

  .status-badge.active {
    background-color: #dcfce7;
    color: #16a34a;
  }

  .status-badge.inactive {
    background-color: #fee2e2;
    color: #ef4444;
  }

  .actions {
    display: flex;
    gap: 8px;
  }

  .actions button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 4px;
    border: none;
    background-color: #f8fafc;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  .actions button:hover {
    background-color: #e2e8f0;
  }

  .edit-btn {
    color: #3a86ff;
  }

  .toggle-btn.deactivate {
    color: #ef4444;
  }

  .toggle-btn.activate {
    color: #16a34a;
  }

  .delete-btn {
    color: #ef4444;
  }

  .no-data {
    text-align: center;
    padding: 40px 0;
    color: #64748b;
  }

  .spinner {
    width: 24px;
    height: 24px;
    border: 3px solid rgba(58, 134, 255, 0.3);
    border-radius: 50%;
    border-top-color: #3a86ff;
    animation: spin 1s linear infinite;
    margin: 0 auto 10px;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .pagination {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 16px;
  }

  .pagination button {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    border-radius: 4px;
    border: 1px solid #e2e8f0;
    background-color: white;
    cursor: pointer;
    transition: all 0.2s;
  }

  .pagination button:hover:not(:disabled) {
    background-color: #f8fafc;
    border-color: #cbd5e1;
  }

  .pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  /* 模態框樣式 */
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-container {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
  }

  .modal-sm {
    max-width: 450px;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    border-bottom: 1px solid #e2e8f0;
  }

  .modal-header h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
  }

  .close-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #64748b;
    padding: 4px;
    border-radius: 4px;
    display: flex;
    align-items: center;
  }

  .close-btn:hover {
    background-color: #f1f5f9;
  }

  .modal-body {
    padding: 24px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    font-size: 14px;
    color: #334155;
  }

  .form-group input,
  .form-group select {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 14px;
    color: #1e293b;
  }

  .form-group input:focus,
  .form-group select:focus {
    outline: none;
    border-color: #3a86ff;
    box-shadow: 0 0 0 2px rgba(58, 134, 255, 0.2);
  }

  .password-hint {
    display: block;
    font-size: 12px;
    color: #64748b;
    margin-top: 4px;
  }

  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 16px;
    margin-top: 16px;
    border-top: 1px solid #f1f5f9;
  }

  .modal-footer button {
    padding: 10px 16px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .cancel-btn {
    background-color: #f1f5f9;
    color: #334155;
    border: none;
  }

  .cancel-btn:hover {
    background-color: #e2e8f0;
  }

  .submit-btn {
    background-color: #3a86ff;
    color: white;
    border: none;
  }

  .submit-btn:hover {
    background-color: #2667cc;
  }

  .delete-btn {
    background-color: #ef4444;
    color: white;
    border: none;
  }

  .delete-btn .material-symbols-outlined {
    color: red;
  }

  .delete-btn:hover:not(:disabled) {
    background-color: #dc2626;
  }

  .delete-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  .reset-password-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .reset-password-toggle input[type="checkbox"] {
    width: auto;
  }

  .confirmation-message {
    margin-bottom: 20px;
    line-height: 1.5;
  }

  .danger-zone {
    background-color: #fee2e2;
    border-radius: 4px;
    padding: 16px;
    margin-bottom: 20px;
  }

  .checkbox-group {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .checkbox-group input[type="checkbox"] {
    width: 16px;
    height: 16px;
  }
</style>
