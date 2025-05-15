<!-- filepath: c:\Users\USER\Desktop\ncu-accommodation-portal\src\views\admin\AdminDashboard.vue -->
<template>
  <div class="admin-dashboard">
    <h1>資料庫管理儀表板</h1>

    <div class="stats-cards">
      <div class="stat-card" v-for="(value, key) in stats.counts" :key="key">
        <h2>{{ formatTitle(key) }}</h2>
        <div class="count">{{ value }}</div>
      </div>
    </div>

    <div class="tabs">
      <button
        v-for="tab in ['tables', 'recent']"
        :key="tab"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab === "tables" ? "資料表管理" : "最近數據" }}
      </button>
    </div>

    <div v-if="activeTab === 'tables'" class="tables-section">
      <h2>資料表列表</h2>
      <div class="tables-container">
        <div
          v-for="table in tables"
          :key="table"
          class="table-item"
          @click="navigateToTable(table)"
        >
          <span class="table-name">{{ table }}</span>
          <span class="table-action">查看 →</span>
        </div>
      </div>
    </div>

    <div v-else class="recent-section">
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
            <button @click="navigateToTable('users')">查看所有用戶</button>
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
            <button @click="navigateToTable('accommodations')">
              查看所有住所
            </button>
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
            <button @click="navigateToTable('sublets')">查看所有轉租</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import { ref, onMounted } from "vue";
  import { useRouter } from "vue-router";
  import apiService from "@/services/api";

  export default {
    setup() {
      const router = useRouter();
      const tables = ref([]);
      const stats = ref({
        counts: {},
        recent_data: {
          users: [],
          accommodations: [],
          sublets: [],
        },
      });
      const activeTab = ref("tables");

      const loadTables = async () => {
        try {
          const response = await apiService.admin.getTables();
          tables.value = response.tables;
        } catch (error) {
          console.error("無法載入資料表:", error);
        }
      };

      const loadDashboardData = async () => {
        try {
          const response = await apiService.admin.getDashboard();
          stats.value = response;
        } catch (error) {
          console.error("無法載入儀表板數據:", error);
        }
      };

      const navigateToTable = (tableName) => {
        router.push(`/admin/tables/${tableName}`);
      };

      const formatTitle = (key) => {
        const titles = {
          users: "用戶",
          accommodations: "住所",
          reviews: "評論",
          sublets: "轉租",
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
        loadTables();
        loadDashboardData();
      });

      return {
        tables,
        stats,
        activeTab,
        navigateToTable,
        formatTitle,
        formatDate,
      };
    },
  };
</script>

<style scoped>
  .admin-dashboard {
    padding: 20px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .stats-cards {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
  }

  .stat-card {
    background-color: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    text-align: center;
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

  .tabs {
    display: flex;
    margin-bottom: 20px;
    border-bottom: 1px solid #ddd;
  }

  .tabs button {
    background: none;
    border: none;
    padding: 10px 20px;
    font-size: 1rem;
    cursor: pointer;
    position: relative;
  }

  .tabs button.active {
    font-weight: bold;
    color: #3a86ff;
  }

  .tabs button.active:after {
    content: "";
    position: absolute;
    bottom: -1px;
    left: 0;
    right: 0;
    height: 3px;
    background: #3a86ff;
  }

  .tables-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }

  .table-item {
    background-color: #fff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .table-item:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
  }

  .table-name {
    font-weight: 500;
  }

  .table-action {
    color: #3a86ff;
    font-weight: bold;
  }

  .recent-data-container {
    display: flex;
    flex-direction: column;
    gap: 30px;
  }

  .recent-data-card {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }

  .recent-data-card h3 {
    margin: 0;
    padding: 15px 20px;
    background-color: #f8f9fa;
    border-bottom: 1px solid #eee;
  }

  table {
    width: 100%;
    border-collapse: collapse;
  }

  th,
  td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #eee;
  }

  th {
    background-color: #f8f9fa;
    font-weight: 500;
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

  .status.fulfilled,
  .status.expired,
  .status.canceled {
    background-color: #f3f4f6;
    color: #6b7280;
  }

  .card-footer {
    padding: 15px;
    display: flex;
    justify-content: flex-end;
    border-top: 1px solid #eee;
  }

  button {
    padding: 8px 16px;
    background-color: #3a86ff;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }

  button:hover {
    background-color: #2667cc;
  }
</style>
