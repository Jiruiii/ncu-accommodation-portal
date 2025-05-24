<template>
  <div class="admin-dashboard">
    <h1>管理儀表板</h1>

    <!-- 統計卡片 -->
    <div class="stats-cards">
      <div class="stat-card" v-for="(value, key) in stats.counts" :key="key">
        <h2>{{ formatTitle(key) }}</h2>
        <div class="count">{{ value }}</div>
      </div>
    </div>

    <!-- 最近數據區域 -->
    <div class="recent-section">
      <div class="section-header">
        <h2>最近數據</h2>
      </div>
      
      <div class="recent-data-container">
        <div class="recent-data-card">
          <h3>最近註冊用戶</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>用戶名</th>
                <th>Email</th>
                <th>註冊時間</th>
                <th>角色</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in stats.recent_data.users" :key="user.id">
                <td>{{ user.id }}</td>
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>{{ user.role }}</td>
              </tr>
            </tbody>
          </table>
          <div class="card-footer">
            <router-link to="/admin/users" class="view-all-btn">查看所有用戶</router-link>
          </div>
        </div>

        <div class="recent-data-card">
          <h3>最近添加的住所</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>標題</th>
                <th>地址</th>
                <th>創建時間</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="acc in stats.recent_data.accommodations" :key="acc.id">
                <td>{{ acc.id }}</td>
                <td>{{ acc.title }}</td>
                <td>{{ acc.address }}</td>
                <td>{{ formatDate(acc.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="card-footer">
            <router-link to="/admin/tables/accommodations" class="view-all-btn">查看所有住所</router-link>
          </div>
        </div>

        <div class="recent-data-card">
          <h3>最近添加的轉租</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>標題</th>
                <th>狀態</th>
                <th>創建時間</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="sublet in stats.recent_data.sublets" :key="sublet.id">
                <td>{{ sublet.id }}</td>
                <td>{{ sublet.title }}</td>
                <td>
                  <span :class="['status', sublet.status]">{{
                    sublet.status
                  }}</span>
                </td>
                <td>{{ formatDate(sublet.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="card-footer">
            <router-link to="/admin/tables/sublets" class="view-all-btn">查看所有轉租</router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 待處理舉報預覽 -->
    <div class="pending-reports-section">
      <div class="section-header">
        <h2>待處理舉報</h2>
        <router-link to="/admin/reports" class="view-all-btn">查看所有舉報</router-link>
      </div>
      
      <div class="reports-preview" v-if="!loadingReports">
        <div v-if="pendingReports.length === 0" class="no-reports">
          沒有待處理的舉報
        </div>
        <div v-else class="report-card" v-for="report in pendingReports.slice(0, 3)" :key="report.id">
          <div class="report-header">
            <div class="report-type">
              {{ report.content_type === 'comment' ? '評論舉報' : '回覆舉報' }}
            </div>
            <div class="report-status pending">待處理</div>
          </div>
          <div class="report-content">
            <div class="report-info">
              <div><strong>舉報時間:</strong> {{ formatDate(report.created_at) }}</div>
              <div><strong>原因:</strong> {{ report.reasons.join(', ') }}</div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="loading-reports">
        載入舉報中...
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import apiService from "@/services/api";
import MessageService from "@/services/MessageService";

export default {
  setup() {
    const stats = ref({
      counts: {},
      recent_data: {
        users: [],
        accommodations: [],
        sublets: [],
      },
    });
    
    // 舉報相關狀態
    const pendingReports = ref([]);
    const loadingReports = ref(false);

    const loadDashboardData = async () => {
      try {
        const response = await apiService.admin.getDashboard();
        stats.value = response;
      } catch (error) {
        console.error("無法載入儀表板數據:", error);
        MessageService.error("無法載入儀表板數據");
      }
    };

    const loadPendingReports = async () => {
      try {
        loadingReports.value = true;
        const params = {
          page: 1,
          per_page: 3,
          status: 'pending'
        };
        
        const response = await apiService.admin.getReports(params);
        
        if (response.success) {
          pendingReports.value = response.reports;
        } else {
          MessageService.error("載入舉報失敗");
        }
      } catch (error) {
        console.error("無法載入舉報:", error);
        MessageService.error("無法載入舉報數據");
      } finally {
        loadingReports.value = false;
      }
    };

    const formatTitle = (key) => {
      const titles = {
        users: "用戶",
        accommodations: "住所",
        reviews: "評論",
        sublets: "轉租",
        reports: "舉報",
      };

      return titles[key] || key;
    };

    const formatDate = (dateString) => {
      if (!dateString) return "N/A";

      const date = new Date(dateString);
      return new Intl.DateTimeFormat("zh-TW", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      }).format(date);
    };

    onMounted(() => {
      loadDashboardData();
      loadPendingReports();
    });

    return {
      stats,
      pendingReports,
      loadingReports,
      formatTitle,
      formatDate
    };
  },
};
</script>

<style scoped>
.admin-dashboard {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

h1 {
  margin: 0 0 20px 0;
  font-size: 1.8rem;
  color: #2d3748;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #2d3748;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
}

.stat-card h2 {
  margin: 0;
  font-size: 1rem;
  color: #666;
}

.stat-card .count {
  font-size: 2.5rem;
  font-weight: bold;
  margin: 10px 0;
  color: #3a86ff;
}

.recent-section,
.pending-reports-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.recent-data-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.recent-data-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.recent-data-card h3 {
  margin: 0;
  padding: 15px 20px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
  font-size: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: 500;
  color: #4a5568;
}

tr:hover {
  background-color: #f8f9fa;
}

.status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.status.active {
  background-color: #e6f7ee;
  color: #0e9f6e;
}

.status.pending {
  background-color: #fef3c7;
  color: #d97706;
}

.card-footer {
  padding: 15px;
  display: flex;
  justify-content: flex-end;
  border-top: 1px solid #eee;
}

.view-all-btn {
  padding: 8px 16px;
  background-color: #3a86ff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  text-decoration: none;
  display: inline-block;
}

.view-all-btn:hover {
  background-color: #2667cc;
}

.reports-preview {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.report-card {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.report-header {
  display: flex;
  justify-content: space-between;
  padding: 12px 15px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #eee;
}

.report-type {
  font-weight: 500;
}

.report-status {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.report-content {
  padding: 15px;
}

.report-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.no-reports {
  padding: 20px;
  text-align: center;
  color: #718096;
  background-color: #f9fafb;
  border-radius: 8px;
  border: 1px dashed #e2e8f0;
}

.loading-reports {
  padding: 20px;
  text-align: center;
  color: #718096;
}
</style>
