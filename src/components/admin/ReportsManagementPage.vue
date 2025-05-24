<template>
    <div class="reports-management-page">
      <div class="page-header">
        <h1>舉報管理</h1>
        <div class="filter-controls">
          <select v-model="reportFilter" class="report-filter">
            <option value="all">全部舉報</option>
            <option value="pending">待處理</option>
            <option value="reviewed">已審核</option>
            <option value="resolved">已解決</option>
            <option value="rejected">已拒絕</option>
          </select>
        </div>
      </div>
      
      <div class="reports-list" v-if="!loadingReports">
        <div v-if="reports.length === 0" class="no-reports">
          沒有符合條件的舉報
        </div>
        <div v-else class="report-card" v-for="report in reports" :key="report.id">
          <div class="report-header">
            <div class="report-type">
              {{ report.content_type === 'comment' ? '評論舉報' : '回覆舉報' }}
            </div>
            <div :class="['report-status', report.status]">
              {{ getReportStatusText(report.status) }}
            </div>
          </div>
          <div class="report-content">
            <div class="report-info">
              <div><strong>舉報者ID:</strong> {{ report.reporter_id }}</div>
              <div><strong>內容ID:</strong> {{ report.content_id }}</div>
              <div><strong>原因:</strong> {{ report.reasons.join(', ') }}</div>
              <div v-if="report.description"><strong>描述:</strong> {{ report.description }}</div>
              <div><strong>舉報時間:</strong> {{ formatDate(report.created_at) }}</div>
            </div>
            <div class="report-actions">
              <button 
                v-if="report.status === 'pending'"
                @click="handleReportAction(report.id, 'reviewed')" 
                class="review-btn"
              >
                標記為已審核
              </button>
              <button 
                v-if="['pending', 'reviewed'].includes(report.status)"
                @click="handleReportAction(report.id, 'resolved', true)" 
                class="resolve-btn"
              >
                解決並刪除內容
              </button>
              <button 
                v-if="['pending', 'reviewed'].includes(report.status)"
                @click="handleReportAction(report.id, 'resolved', false)" 
                class="resolve-btn light"
              >
                解決但保留內容
              </button>
              <button 
                v-if="['pending', 'reviewed'].includes(report.status)"
                @click="handleReportAction(report.id, 'rejected')" 
                class="reject-btn"
              >
                拒絕舉報
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="loading-reports">
        載入舉報中...
      </div>
      
      <div class="reports-pagination" v-if="reportsTotalPages > 1">
        <button 
          @click="reportsPage = reportsPage - 1" 
          :disabled="reportsPage === 1"
        >
          上一頁
        </button>
        <span>{{ reportsPage }} / {{ reportsTotalPages }}</span>
        <button 
          @click="reportsPage = reportsPage + 1" 
          :disabled="reportsPage === reportsTotalPages"
        >
          下一頁
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, onMounted, watch } from "vue";
  import apiService from "@/services/api";
  import MessageService from "@/services/MessageService";
  
  export default {
    setup() {
      const reports = ref([]);
      const reportsPage = ref(1);
      const reportsTotalPages = ref(1);
      const reportFilter = ref("all");
      const loadingReports = ref(false);
  
      // 獲取舉報狀態文字
      const getReportStatusText = (status) => {
        const statusMap = {
          pending: "待處理",
          reviewed: "已審核",
          resolved: "已解決",
          rejected: "已拒絕"
        };
        return statusMap[status] || status;
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
  
      const loadReports = async () => {
        try {
          loadingReports.value = true;
          const params = {
            page: reportsPage.value,
            per_page: 10
          };
          
          if (reportFilter.value !== "all") {
            params.status = reportFilter.value;
          }
          
          const response = await apiService.admin.getReports(params);
          
          if (response.success) {
            reports.value = response.reports;
            reportsTotalPages.value = response.pages;
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
  
      const handleReportAction = async (reportId, status, deleteContent = false) => {
        try {
          const response = await apiService.admin.updateReportStatus(reportId, {
            status,
            delete_content: deleteContent
          });
          
          if (response.success) {
            MessageService.success(response.message || "舉報狀態已更新");
            // 重新載入舉報列表
            loadReports();
          } else {
            MessageService.error(response.error || "更新舉報狀態失敗");
          }
        } catch (error) {
          console.error("處理舉報失敗:", error);
          MessageService.error("處理舉報失敗: " + (error.message || "未知錯誤"));
        }
      };
  
      // 監聽舉報頁碼和過濾條件變化
      watch([reportsPage, reportFilter], () => {
        loadReports();
      });
  
      onMounted(() => {
        loadReports();
      });
  
      return {
        reports,
        reportsPage,
        reportsTotalPages,
        reportFilter,
        loadingReports,
        formatDate,
        getReportStatusText,
        handleReportAction
      };
    }
  };
  </script>
  
  <style scoped>
  .reports-management-page {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    padding: 20px;
  }
  
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
  }
  
  .page-header h1 {
    margin: 0;
    font-size: 1.5rem;
    color: #2d3748;
  }
  
  .report-filter {
    padding: 8px 12px;
    border-radius: 4px;
    border: 1px solid #ddd;
    font-size: 0.9rem;
  }
  
  .reports-list {
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .report-card {
    border: 1px solid #eee;
    border-radius: 8px;
    overflow: hidden;
    transition: box-shadow 0.3s ease;
  }
  
  .report-card:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
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
  
  .report-status.pending {
    background-color: #fef3c7;
    color: #d97706;
  }
  
  .report-status.reviewed {
    background-color: #ebf5ff;
    color: #3182ce;
  }
  
  .report-status.resolved {
    background-color: #e6f7ee;
    color: #0e9f6e;
  }
  
  .report-status.rejected {
    background-color: #fee2e2;
    color: #ef4444;
  }
  
  .report-content {
    padding: 15px;
  }
  
  .report-info {
    margin-bottom: 15px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 10px;
  }
  
  .report-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .review-btn {
    background-color: #3182ce;
  }
  
  .resolve-btn {
    background-color: #0e9f6e;
  }
  
  .resolve-btn.light {
    background-color: #10b981;
  }
  
  .reject-btn {
    background-color: #ef4444;
  }
  
  button {
    padding: 8px 16px;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: opacity 0.2s;
  }
  
  button:hover:not(:disabled) {
    opacity: 0.9;
  }
  
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .no-reports {
    padding: 40px 20px;
    text-align: center;
    color: #718096;
    font-size: 1rem;
    background-color: #f9fafb;
    border-radius: 8px;
    border: 1px dashed #e2e8f0;
  }
  
  .loading-reports {
    padding: 20px;
    text-align: center;
    color: #718096;
  }
  
  .reports-pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 20px;
    gap: 15px;
  }
  
  .reports-pagination button {
    padding: 5px 10px;
    background-color: #3a86ff;
  }
  
  .reports-pagination span {
    color: #4a5568;
  }
  </style>