<template>
    <div class="verification-status-page">
      <div class="status-header">
        <h1>認證狀態</h1>
        <div class="status-badge" :class="statusClass">
          {{ statusText }}
        </div>
      </div>
      
      <div class="status-card">
        <div class="status-timeline">
          <div
            v-for="(step, index) in timeline"
            :key="index"
            class="timeline-item"
            :class="{ completed: step.completed, current: step.current }"
          >
            <div class="timeline-marker">
              <i v-if="step.completed" class="fa-solid fa-check"></i>
              <i v-else-if="step.current && status === 'rejected'" class="fa-solid fa-times"></i>
              <i v-else-if="step.current" class="fa-solid fa-spinner fa-pulse"></i>
              <span v-else></span>
            </div>
            <div class="timeline-content">
              <div class="timeline-title">{{ step.title }}</div>
              <div class="timeline-date" v-if="step.date">{{ step.date }}</div>
              <div class="timeline-description">{{ step.description }}</div>
            </div>
          </div>
        </div>
        
        <div v-if="status === 'rejected'" class="rejection-details">
          <h3>審核未通過原因</h3>
          <p>{{ rejectionReason }}</p>
          <div class="reapply-notice">
            <p>您可以根據上述原因修正資料後重新提交認證申請。</p>
            <button @click="goToVerification" class="reapply-btn">重新申請</button>
          </div>
        </div>
        
        <div v-if="status === 'pending'" class="status-notice">
          <p>您的申請正在審核中，我們將盡快處理並將結果通知您。</p>
          <p>平均審核時間為 1-3 個工作日，請耐心等待。</p>
        </div>
        
        <div v-if="status === 'approved'" class="status-notice success">
          <p>恭喜！您已完成房東認證。</p>
          <p>您現在可以發布房源並使用所有房東功能。</p>
          <button @click="goToDashboard" class="dashboard-btn">前往房東中心</button>
        </div>
      </div>
      
      <div v-if="status === 'pending' || status === 'approved'" class="application-summary">
        <h2>申請資料摘要</h2>
        
        <div class="summary-section">
          <h3>基本資料</h3>
          <div class="summary-item">
            <span class="summary-label">姓名</span>
            <span class="summary-value">{{ applicationData.realName }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">聯絡電話</span>
            <span class="summary-value">{{ applicationData.phone }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">電子郵件</span>
            <span class="summary-value">{{ applicationData.email }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">申請日期</span>
            <span class="summary-value">{{ applicationData.applyDate }}</span>
          </div>
        </div>
        
        <div class="summary-section">
          <h3>房產資訊</h3>
          <div class="summary-item">
            <span class="summary-label">房屋類型</span>
            <span class="summary-value">{{ applicationData.propertyTypes.join(", ") }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">所在區域</span>
            <span class="summary-value">{{ applicationData.propertyArea }}</span>
          </div>
        </div>
      </div>
      
      <div class="status-actions">
        <button @click="goBack" class="back-btn">返回</button>
        <button
          v-if="status === 'pending'"
          @click="cancelApplication"
          class="cancel-btn"
        >
          取消申請
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue';
  import { useRouter } from 'vue-router';
//   import apiService from '@/services/api';
  
  export default {
    name: 'VerificationStatusPage',
    setup() {
      const router = useRouter();
      const status = ref('pending'); // pending, approved, rejected
      const rejectionReason = ref('');
      const applicationData = ref({
        realName: '王大明',
        phone: '0912345678',
        email: 'example@gmail.com',
        applyDate: '2025-05-15',
        propertyTypes: ['套房', '雅房'],
        propertyArea: '中壢區'
      });
      
      // 審核狀態文字和CSS類別
      const statusText = computed(() => {
        switch (status.value) {
          case 'approved': return '已認證';
          case 'rejected': return '未通過';
          default: return '審核中';
        }
      });
      
      const statusClass = computed(() => {
        switch (status.value) {
          case 'approved': return 'approved';
          case 'rejected': return 'rejected';
          default: return 'pending';
        }
      });
      
      // 時間線
      const timeline = computed(() => {
        const result = [
          {
            title: '提交申請',
            date: '2025-05-15',
            description: '您已成功提交房東認證申請',
            completed: true,
            current: false
          },
          {
            title: '資料審核',
            date: status.value !== 'pending' ? '2025-05-16' : '',
            description: status.value === 'pending' 
              ? '我們正在審核您提供的資料'
              : '您的資料已完成審核',
            completed: status.value !== 'pending',
            current: status.value === 'pending'
          },
          {
            title: '認證結果',
            date: status.value === 'approved' ? '2025-05-16' : '',
            description: getStatusDescription(),
            completed: status.value === 'approved',
            current: status.value === 'rejected'
          }
        ];
        
        return result;
      });
      
      // 獲取狀態描述
      function getStatusDescription() {
        switch (status.value) {
          case 'approved': 
            return '恭喜！您已通過房東認證';
          case 'rejected': 
            return '很抱歉，您的認證申請未通過，請查看原因';
          default:
            return '我們將通知您最終的認證結果';
        }
      }
      
      // 獲取認證狀態數據
      const fetchVerificationStatus = async () => {
        try {
          // 正式環境使用 API 請求
          // const response = await apiService.landlord.getVerificationStatus();
          // status.value = response.status;
          // rejectionReason.value = response.rejectionReason || '';
          // applicationData.value = response.applicationData || {};
          
          // 模擬數據 - 隨機選擇一個狀態
          const statuses = ['pending', 'approved', 'rejected'];
          status.value = statuses[Math.floor(Math.random() * statuses.length)];
          
          if (status.value === 'rejected') {
            rejectionReason.value = '提供的身份證明文件不清晰，無法驗證您的身份。請重新上傳更清晰的照片，確保所有資訊可見。';
          }
        } catch (error) {
          console.error('獲取認證狀態失敗:', error);
          // 默認使用 pending 狀態
          status.value = 'pending';
        }
      };
      
      // 導航功能
      const goBack = () => {
        router.back();
      };
      
      const goToVerification = () => {
        router.push('/landlord/verification');
      };
      
      const goToDashboard = () => {
        router.push('/landlord/dashboard');
      };
      
      // 取消申請
      const cancelApplication = async () => {
        if (!confirm('確定要取消認證申請嗎？取消後將需要重新提交申請。')) {
          return;
        }
        
        try {
          // await apiService.landlord.cancelVerification();
          alert('申請已取消');
          router.push('/profile');
        } catch (error) {
          console.error('取消申請失敗:', error);
          alert('取消申請失敗，請稍後再試');
        }
      };
      
      onMounted(() => {
        fetchVerificationStatus();
      });
      
      return {
        status,
        statusText,
        statusClass,
        timeline,
        rejectionReason,
        applicationData,
        goBack,
        goToVerification,
        goToDashboard,
        cancelApplication
      };
    }
  };
  </script>
  
  <style scoped>
  .verification-status-page {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
    overflow-y: auto;
    height: calc(100vh - 80px);
  }
  
  .status-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
  }
  
  .status-header h1 {
    font-size: 2rem;
    color: #333;
    margin: 0;
  }
  
  .status-badge {
    padding: 8px 15px;
    border-radius: 20px;
    font-weight: 500;
  }
  
  .status-badge.approved {
    background-color: rgba(76, 175, 80, 0.1);
    color: #4caf50;
  }
  
  .status-badge.pending {
    background-color: rgba(255, 152, 0, 0.1);
    color: #ff9800;
  }
  
  .status-badge.rejected {
    background-color: rgba(244, 67, 54, 0.1);
    color: #f44336;
  }
  
  .status-card {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 30px;
    margin-bottom: 30px;
  }
  
  .status-timeline {
    position: relative;
    margin-bottom: 30px;
  }
  
  .status-timeline::before {
    content: '';
    position: absolute;
    top: 0;
    bottom: 0;
    left: 15px;
    width: 2px;
    background-color: #e0e0e0;
  }
  
  .timeline-item {
    position: relative;
    padding-left: 45px;
    margin-bottom: 30px;
  }
  
  .timeline-item:last-child {
    margin-bottom: 0;
  }
  
  .timeline-marker {
    position: absolute;
    left: 0;
    top: 0;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #e0e0e0;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1;
    color: #999;
  }
  
  .timeline-item.completed .timeline-marker {
    background-color: #4caf50;
    color: white;
  }
  
  .timeline-item.current .timeline-marker {
    background-color: #ff9800;
    color: white;
  }
  
  .timeline-item.current.rejected .timeline-marker {
    background-color: #f44336;
  }
  
  .timeline-title {
    font-weight: 600;
    color: #333;
    margin-bottom: 5px;
  }
  
  .timeline-date {
    font-size: 0.85rem;
    color: #999;
    margin-bottom: 5px;
  }
  
  .timeline-description {
    color: #666;
  }
  
  .timeline-item.completed .timeline-title {
    color: #4caf50;
  }
  
  .timeline-item.current .timeline-title {
    color: #ff9800;
  }
  
  .rejection-details {
    background-color: #fff8e1;
    border-left: 4px solid #ffc107;
    padding: 15px;
    margin-top: 20px;
    border-radius: 4px;
  }
  
  .rejection-details h3 {
    font-size: 1.1rem;
    color: #f57c00;
    margin: 0 0 10px 0;
  }
  
  .rejection-details p {
    color: #555;
    margin: 0 0 15px 0;
  }
  
  .reapply-notice {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 4px;
    margin-top: 15px;
  }
  
  .reapply-notice p {
    margin: 0 0 10px 0;
  }
  
  .status-notice {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
    padding: 15px;
    margin-top: 20px;
    border-radius: 4px;
  }
  
  .status-notice p {
    color: #555;
    margin: 0 0 10px 0;
  }
  
  .status-notice p:last-child {
    margin-bottom: 0;
  }
  
  .status-notice.success {
    background-color: #e8f5e9;
    border-left: 4px solid #4caf50;
  }
  
  .application-summary {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 30px;
    margin-bottom: 30px;
  }
  
  .application-summary h2 {
    font-size: 1.5rem;
    margin: 0 0 20px 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
    color: #333;
  }
  
  .summary-section {
    margin-bottom: 20px;
  }
  
  .summary-section h3 {
    font-size: 1.1rem;
    margin: 0 0 15px 0;
    color: #333;
  }
  
  .summary-item {
    display: flex;
    margin-bottom: 10px;
  }
  
  .summary-label {
    width: 100px;
    font-weight: 500;
    color: #555;
  }
  
  .summary-value {
    flex: 1;
    color: #333;
  }
  
  .status-actions {
    display: flex;
    gap: 15px;
  }
  
  .back-btn,
  .cancel-btn,
  .reapply-btn,
  .dashboard-btn {
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: 500;
    border: none;
    cursor: pointer;
  }
  
  .back-btn {
    background-color: #f5f5f5;
    color: #333;
  }
  
  .back-btn:hover {
    background-color: #e0e0e0;
  }
  
  .cancel-btn {
    background-color: #f44336;
    color: white;
  }
  
  .cancel-btn:hover {
    background-color: #d32f2f;
  }
  
  .reapply-btn,
  .dashboard-btn {
    background-color: #4caf50;
    color: white;
    display: inline-block;
  }
  
  .reapply-btn:hover,
  .dashboard-btn:hover {
    background-color: #388e3c;
  }
  
  @media (max-width: 768px) {
    .verification-status-page {
      padding: 20px 15px;
    }
    
    .status-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
    
    .status-card,
    .application-summary {
      padding: 20px;
    }
    
    .summary-item {
      flex-direction: column;
    }
    
    .summary-label {
      width: 100%;
      margin-bottom: 5px;
    }
  }
  </style>