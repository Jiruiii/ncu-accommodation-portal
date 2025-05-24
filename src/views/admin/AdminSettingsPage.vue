<template>
    <div class="admin-settings-page">
      <h1>系統設置</h1>
      
      <div class="settings-container">
        <!-- 左側標籤導航 -->
        <div class="settings-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id" 
            :class="['tab-btn', { active: activeTab === tab.id }]"
            @click="activeTab = tab.id"
          >
            <span class="material-symbols-outlined">{{ tab.icon }}</span>
            {{ tab.name }}
          </button>
        </div>
        
        <!-- 右側設置內容 -->
        <div class="settings-content">
          <!-- 系統參數設置 -->
          <div v-if="activeTab === 'system'" class="settings-section">
            <h2>系統參數設置</h2>
            
            <div class="settings-card">
              <h3>網站基本設置</h3>
              <div class="form-group">
                <label>網站名稱</label>
                <input type="text" v-model="systemSettings.siteName" />
              </div>
              <div class="form-group">
                <label>聯繫郵箱</label>
                <input type="email" v-model="systemSettings.contactEmail" />
              </div>
              <div class="form-group">
                <label>系統公告</label>
                <textarea v-model="systemSettings.announcement" rows="3"></textarea>
              </div>
              <div class="form-group">
                <label>是否顯示公告</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="showAnnouncement" 
                    v-model="systemSettings.showAnnouncement"
                  />
                  <label for="showAnnouncement"></label>
                </div>
              </div>
            </div>
            
            <div class="settings-card">
              <h3>功能開關</h3>
              <div class="form-group">
                <label>開放用戶註冊</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="allowRegistration" 
                    v-model="systemSettings.allowRegistration"
                  />
                  <label for="allowRegistration"></label>
                </div>
              </div>
              <div class="form-group">
                <label>開放評論功能</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="enableComments" 
                    v-model="systemSettings.enableComments"
                  />
                  <label for="enableComments"></label>
                </div>
              </div>
              <div class="form-group">
                <label>開放轉租功能</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="enableSublets" 
                    v-model="systemSettings.enableSublets"
                  />
                  <label for="enableSublets"></label>
                </div>
              </div>
            </div>
            
            <button class="save-btn" @click="saveSystemSettings">保存系統設置</button>
          </div>
          
          <!-- 用戶審核設置 -->
          <div v-if="activeTab === 'user'" class="settings-section">
            <h2>用戶審核設置</h2>
            
            <div class="settings-card">
              <h3>註冊設置</h3>
              <div class="form-group">
                <label>註冊需要郵箱驗證</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="requireEmailVerification" 
                    v-model="userSettings.requireEmailVerification"
                  />
                  <label for="requireEmailVerification"></label>
                </div>
              </div>
              <div class="form-group">
                <label>必須使用學校郵箱</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="requireSchoolEmail" 
                    v-model="userSettings.requireSchoolEmail"
                  />
                  <label for="requireSchoolEmail"></label>
                </div>
              </div>
              <div class="form-group">
                <label>學校郵箱域名 (用逗號分隔)</label>
                <input type="text" v-model="userSettings.schoolEmailDomains" />
                <small>例如: ncu.edu.tw, cc.ncu.edu.tw</small>
              </div>
            </div>
            
            <div class="settings-card">
              <h3>審核設置</h3>
              <div class="form-group">
                <label>新用戶默認狀態</label>
                <select v-model="userSettings.defaultUserStatus">
                  <option value="active">直接啟用</option>
                  <option value="pending">等待審核</option>
                </select>
              </div>
              <div class="form-group">
                <label>發布內容需要審核</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="moderateContent" 
                    v-model="userSettings.moderateContent"
                  />
                  <label for="moderateContent"></label>
                </div>
              </div>
            </div>
            
            <button class="save-btn" @click="saveUserSettings">保存用戶設置</button>
          </div>
          
          <!-- 內容設置 -->
          <div v-if="activeTab === 'content'" class="settings-section">
            <h2>內容管理設置</h2>
            
            <div class="settings-card">
              <h3>評論設置</h3>
              <div class="form-group">
                <label>每頁顯示評論數</label>
                <input type="number" v-model="contentSettings.commentsPerPage" min="5" max="50" />
              </div>
              <div class="form-group">
                <label>評論需審核後顯示</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="reviewComments" 
                    v-model="contentSettings.reviewComments"
                  />
                  <label for="reviewComments"></label>
                </div>
              </div>
              <div class="form-group">
                <label>評論需包含文字 (不能僅有圖片)</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="requireCommentText" 
                    v-model="contentSettings.requireCommentText"
                  />
                  <label for="requireCommentText"></label>
                </div>
              </div>
            </div>
            
            <div class="settings-card">
              <h3>敏感詞過濾</h3>
              <div class="form-group">
                <label>啟用敏感詞過濾</label>
                <div class="toggle-switch">
                  <input 
                    type="checkbox" 
                    id="enableWordFilter" 
                    v-model="contentSettings.enableWordFilter"
                  />
                  <label for="enableWordFilter"></label>
                </div>
              </div>
              <div class="form-group">
                <label>敏感詞列表 (每行一個)</label>
                <textarea 
                  v-model="contentSettings.sensitiveWords" 
                  rows="5"
                  :disabled="!contentSettings.enableWordFilter"
                ></textarea>
              </div>
              <div class="form-group">
                <label>敏感詞處理方式</label>
                <select 
                  v-model="contentSettings.filterAction"
                  :disabled="!contentSettings.enableWordFilter"
                >
                  <option value="replace">替換為 ***</option>
                  <option value="block">阻止發布</option>
                  <option value="review">標記為需審核</option>
                </select>
              </div>
            </div>
            
            <button class="save-btn" @click="saveContentSettings">保存內容設置</button>
          </div>
          
          <!-- 數據備份與維護 -->
          <div v-if="activeTab === 'backup'" class="settings-section">
            <h2>系統維護與備份</h2>
            
            <div class="settings-card">
              <h3>數據備份</h3>
              <p>備份系統數據庫和上傳的文件，以防數據丟失。</p>
              <div class="action-buttons">
                <button class="primary-btn" @click="startBackup">
                  <span class="material-symbols-outlined">backup</span>
                  創建備份
                </button>
                <button class="secondary-btn" @click="loadBackups">
                  <span class="material-symbols-outlined">restore</span>
                  恢復備份
                </button>
              </div>
              
              <div v-if="backups.length > 0" class="backup-list">
                <h4>最近備份</h4>
                <table>
                  <thead>
                    <tr>
                      <th>備份時間</th>
                      <th>大小</th>
                      <th>操作</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(backup, index) in backups" :key="index">
                      <td>{{ formatDate(backup.date) }}</td>
                      <td>{{ formatSize(backup.size) }}</td>
                      <td>
                        <button class="icon-btn" @click="downloadBackup(backup)">
                          <span class="material-symbols-outlined">download</span>
                        </button>
                        <button class="icon-btn" @click="restoreBackup(backup)">
                          <span class="material-symbols-outlined">restore</span>
                        </button>
                        <button class="icon-btn danger" @click="deleteBackup(backup)">
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            
            <div class="settings-card">
              <h3>系統維護</h3>
              <p>執行系統維護任務，以保持系統運行良好。</p>
              <div class="action-buttons">
                <button class="secondary-btn" @click="clearCache">
                  <span class="material-symbols-outlined">cleaning_services</span>
                  清理緩存
                </button>
                <button class="secondary-btn" @click="optimizeDatabase">
                  <span class="material-symbols-outlined">database</span>
                  優化數據庫
                </button>
                <button class="danger-btn" @click="confirmReset">
                  <span class="material-symbols-outlined">restart_alt</span>
                  重置系統
                </button>
              </div>
            </div>
          </div>
          
          <!-- 系統日誌 -->
          <div v-if="activeTab === 'logs'" class="settings-section">
            <h2>系統日誌</h2>
            
            <div class="settings-card">
              <h3>日誌查看</h3>
              <div class="log-filters">
                <div class="form-group">
                  <label>日誌類型</label>
                  <select v-model="logFilter.type" @change="loadLogs">
                    <option value="all">所有日誌</option>
                    <option value="error">錯誤日誌</option>
                    <option value="access">訪問日誌</option>
                    <option value="admin">管理操作</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>日期範圍</label>
                  <div class="date-range">
                    <input type="date" v-model="logFilter.startDate" @change="loadLogs" />
                    <span>至</span>
                    <input type="date" v-model="logFilter.endDate" @change="loadLogs" />
                  </div>
                </div>
                <button class="secondary-btn" @click="loadLogs">
                  <span class="material-symbols-outlined">refresh</span>
                  刷新
                </button>
                <button class="secondary-btn" @click="downloadLogs">
                  <span class="material-symbols-outlined">download</span>
                  下載日誌
                </button>
              </div>
              
              <div class="log-container">
                <div v-if="loading" class="loading">載入中...</div>
                <div v-else-if="logs.length === 0" class="no-logs">沒有符合條件的日誌</div>
                <div v-else class="log-entries">
                  <div 
                    v-for="(log, index) in logs" 
                    :key="index" 
                    :class="['log-entry', log.level]"
                  >
                    <div class="log-time">{{ formatDateTime(log.timestamp) }}</div>
                    <div class="log-level">{{ log.level.toUpperCase() }}</div>
                    <div class="log-message">{{ log.message }}</div>
                  </div>
                </div>
              </div>
              
              <div v-if="totalLogs > logs.length" class="log-pagination">
                <button 
                  @click="changePage(currentPage - 1)" 
                  :disabled="currentPage === 1"
                >
                  上一頁
                </button>
                <span>第 {{ currentPage }} 頁，共 {{ totalPages }} 頁</span>
                <button 
                  @click="changePage(currentPage + 1)" 
                  :disabled="currentPage === totalPages"
                >
                  下一頁
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 確認對話框 -->
      <div v-if="showConfirmDialog" class="confirm-dialog-overlay">
        <div class="confirm-dialog">
          <h3>{{ confirmDialog.title }}</h3>
          <p>{{ confirmDialog.message }}</p>
          <div class="dialog-buttons">
            <button class="secondary-btn" @click="cancelDialog">取消</button>
            <button 
              class="danger-btn" 
              @click="confirmDialog.confirm"
            >
              確認
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, onMounted } from 'vue';
  import apiService from '@/services/api';
  import MessageService from '@/services/MessageService';
  
  export default {
    setup() {
      // 活動標籤
      const activeTab = ref('system');
      
      // 標籤定義
      const tabs = [
        { id: 'system', name: '系統設置', icon: 'settings' },
        { id: 'user', name: '用戶設置', icon: 'person' },
        { id: 'content', name: '內容設置', icon: 'article' },
        { id: 'backup', name: '備份與維護', icon: 'backup' },
        { id: 'logs', name: '系統日誌', icon: 'receipt_long' }
      ];
      
      // 系統設置
      const systemSettings = reactive({
        siteName: '中央大學住宿資訊平台',
        contactEmail: 'admin@example.com',
        announcement: '',
        showAnnouncement: false,
        allowRegistration: true,
        enableComments: true,
        enableSublets: true
      });
      
      // 用戶設置
      const userSettings = reactive({
        requireEmailVerification: true,
        requireSchoolEmail: true,
        schoolEmailDomains: 'ncu.edu.tw',
        defaultUserStatus: 'active',
        moderateContent: false
      });
      
      // 內容設置
      const contentSettings = reactive({
        commentsPerPage: 20,
        reviewComments: false,
        requireCommentText: true,
        enableWordFilter: false,
        sensitiveWords: '',
        filterAction: 'replace'
      });
      
      // 備份列表
      const backups = ref([]);
      
      // 日誌相關
      const logs = ref([]);
      const loading = ref(false);
      const currentPage = ref(1);
      const totalPages = ref(1);
      const totalLogs = ref(0);
      const logFilter = reactive({
        type: 'all',
        startDate: '',
        endDate: ''
      });
      
      // 確認對話框
      const showConfirmDialog = ref(false);
      const confirmDialog = reactive({
        title: '',
        message: '',
        confirm: () => {}
      });
      
      // 初始化
      onMounted(async () => {
        await loadSettings();
        setDefaultDates();
      });
      
      // 設置默認日期範圍（最近7天）
      const setDefaultDates = () => {
        const today = new Date();
        const sevenDaysAgo = new Date(today);
        sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
        
        logFilter.endDate = formatDateForInput(today);
        logFilter.startDate = formatDateForInput(sevenDaysAgo);
      };
      
      // 載入設置
      const loadSettings = async () => {
        try {
          const response = await apiService.admin.getSettings();
          
          if (response.success) {
            // 填充系統設置
            Object.assign(systemSettings, response.settings.system);
            
            // 填充用戶設置
            Object.assign(userSettings, response.settings.user);
            
            // 填充內容設置
            Object.assign(contentSettings, response.settings.content);
          }
        } catch (error) {
          console.error('載入設置失敗:', error);
          MessageService.error('載入設置失敗，請稍後再試');
        }
      };
      
      // 保存系統設置
      const saveSystemSettings = async () => {
        try {
          const response = await apiService.admin.saveSettings({
            type: 'system',
            settings: systemSettings
          });
          
          if (response.success) {
            MessageService.success('系統設置已保存');
          } else {
            MessageService.error(response.error || '保存設置失敗');
          }
        } catch (error) {
          console.error('保存設置失敗:', error);
          MessageService.error('保存設置失敗，請稍後再試');
        }
      };
      
      // 保存用戶設置
      const saveUserSettings = async () => {
        try {
          const response = await apiService.admin.saveSettings({
            type: 'user',
            settings: userSettings
          });
          
          if (response.success) {
            MessageService.success('用戶設置已保存');
          } else {
            MessageService.error(response.error || '保存設置失敗');
          }
        } catch (error) {
          console.error('保存設置失敗:', error);
          MessageService.error('保存設置失敗，請稍後再試');
        }
      };
      
      // 保存內容設置
      const saveContentSettings = async () => {
        try {
          const response = await apiService.admin.saveSettings({
            type: 'content',
            settings: contentSettings
          });
          
          if (response.success) {
            MessageService.success('內容設置已保存');
          } else {
            MessageService.error(response.error || '保存設置失敗');
          }
        } catch (error) {
          console.error('保存設置失敗:', error);
          MessageService.error('保存設置失敗，請稍後再試');
        }
      };
      
      // 載入備份列表
      const loadBackups = async () => {
        try {
          const response = await apiService.admin.getBackups();
          
          if (response.success) {
            backups.value = response.backups;
          } else {
            MessageService.error(response.error || '載入備份列表失敗');
          }
        } catch (error) {
          console.error('載入備份列表失敗:', error);
          MessageService.error('載入備份列表失敗，請稍後再試');
        }
      };
      
      // 創建備份
      const startBackup = async () => {
        try {
          const response = await apiService.admin.createBackup();
          
          if (response.success) {
            MessageService.success('備份創建成功');
            await loadBackups();
          } else {
            MessageService.error(response.error || '創建備份失敗');
          }
        } catch (error) {
          console.error('創建備份失敗:', error);
          MessageService.error('創建備份失敗，請稍後再試');
        }
      };
      
      // 下載備份
      const downloadBackup = (backup) => {
        window.open(`/api/admin/backups/${backup.id}/download`, '_blank');
      };
      
      // 恢復備份
      const restoreBackup = (backup) => {
        showConfirmDialog.value = true;
        confirmDialog.title = '恢復備份';
        confirmDialog.message = `確定要恢復 ${formatDate(backup.date)} 的備份嗎？這將覆蓋當前的所有數據！`;
        confirmDialog.confirm = async () => {
          try {
            const response = await apiService.admin.restoreBackup(backup.id);
            
            if (response.success) {
              MessageService.success('備份恢復成功，系統將在 5 秒後自動重啟');
              showConfirmDialog.value = false;
              
              // 延遲 5 秒後刷新頁面
              setTimeout(() => {
                window.location.reload();
              }, 5000);
            } else {
              MessageService.error(response.error || '恢復備份失敗');
              showConfirmDialog.value = false;
            }
          } catch (error) {
            console.error('恢復備份失敗:', error);
            MessageService.error('恢復備份失敗，請稍後再試');
            showConfirmDialog.value = false;
          }
        };
      };
      
      // 刪除備份
      const deleteBackup = (backup) => {
        showConfirmDialog.value = true;
        confirmDialog.title = '刪除備份';
        confirmDialog.message = `確定要刪除 ${formatDate(backup.date)} 的備份嗎？此操作不可撤銷！`;
        confirmDialog.confirm = async () => {
          try {
            const response = await apiService.admin.deleteBackup(backup.id);
            
            if (response.success) {
              MessageService.success('備份已刪除');
              await loadBackups();
              showConfirmDialog.value = false;
            } else {
              MessageService.error(response.error || '刪除備份失敗');
              showConfirmDialog.value = false;
            }
          } catch (error) {
            console.error('刪除備份失敗:', error);
            MessageService.error('刪除備份失敗，請稍後再試');
            showConfirmDialog.value = false;
          }
        };
      };
      
      // 清理緩存
      const clearCache = async () => {
        try {
          const response = await apiService.admin.clearCache();
          
          if (response.success) {
            MessageService.success('緩存已清理');
          } else {
            MessageService.error(response.error || '清理緩存失敗');
          }
        } catch (error) {
          console.error('清理緩存失敗:', error);
          MessageService.error('清理緩存失敗，請稍後再試');
        }
      };
      
      // 優化數據庫
      const optimizeDatabase = async () => {
        try {
          const response = await apiService.admin.optimizeDatabase();
          
          if (response.success) {
            MessageService.success('數據庫已優化');
          } else {
            MessageService.error(response.error || '優化數據庫失敗');
          }
        } catch (error) {
          console.error('優化數據庫失敗:', error);
          MessageService.error('優化數據庫失敗，請稍後再試');
        }
      };
      
      // 確認重置系統
      const confirmReset = () => {
        showConfirmDialog.value = true;
        confirmDialog.title = '重置系統';
        confirmDialog.message = '確定要重置系統嗎？這將刪除所有數據，此操作不可撤銷！';
        confirmDialog.confirm = async () => {
          try {
            const response = await apiService.admin.resetSystem();
            
            if (response.success) {
              MessageService.success('系統已重置，將在 5 秒後重新登入');
              showConfirmDialog.value = false;
              
              // 延遲 5 秒後跳轉到登入頁面
              setTimeout(() => {
                window.location.href = '/admin/login';
              }, 5000);
            } else {
              MessageService.error(response.error || '重置系統失敗');
              showConfirmDialog.value = false;
            }
          } catch (error) {
            console.error('重置系統失敗:', error);
            MessageService.error('重置系統失敗，請稍後再試');
            showConfirmDialog.value = false;
          }
        };
      };
      
      // 載入日誌
      const loadLogs = async () => {
        try {
          loading.value = true;
          
          const response = await apiService.admin.getLogs({
            page: currentPage.value,
            type: logFilter.type,
            startDate: logFilter.startDate,
            endDate: logFilter.endDate
          });
          
          if (response.success) {
            logs.value = response.logs;
            totalPages.value = response.pages;
            totalLogs.value = response.total;
          } else {
            MessageService.error(response.error || '載入日誌失敗');
          }
        } catch (error) {
          console.error('載入日誌失敗:', error);
          MessageService.error('載入日誌失敗，請稍後再試');
        } finally {
          loading.value = false;
        }
      };
      
      // 下載日誌
      const downloadLogs = () => {
        const params = new URLSearchParams({
          type: logFilter.type,
          startDate: logFilter.startDate,
          endDate: logFilter.endDate
        });
        
        window.open(`/api/admin/logs/download?${params.toString()}`, '_blank');
      };
      
      // 切換日誌頁碼
      const changePage = (page) => {
        currentPage.value = page;
        loadLogs();
      };
      
      // 取消對話框
      const cancelDialog = () => {
        showConfirmDialog.value = false;
      };
      
      // 格式化日期
      const formatDate = (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('zh-TW', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit'
        }).format(date);
      };
      
      // 格式化日期時間
      const formatDateTime = (dateString) => {
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('zh-TW', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }).format(date);
      };
      
      // 格式化日期為 input 元素的格式 (YYYY-MM-DD)
      const formatDateForInput = (date) => {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
      };
      
      // 格式化檔案大小
      const formatSize = (bytes) => {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
      };
      
      return {
        // 標籤相關
        activeTab,
        tabs,
        
        // 設置相關
        systemSettings,
        userSettings,
        contentSettings,
        
        // 備份相關
        backups,
        
        // 日誌相關
        logs,
        loading,
        currentPage,
        totalPages,
        totalLogs,
        logFilter,
        
        // 確認對話框
        showConfirmDialog,
        confirmDialog,
        
        // 方法
        saveSystemSettings,
        saveUserSettings,
        saveContentSettings,
        loadBackups,
        startBackup,
        downloadBackup,
        restoreBackup,
        deleteBackup,
        clearCache,
        optimizeDatabase,
        confirmReset,
        loadLogs,
        downloadLogs,
        changePage,
        cancelDialog,
        formatDate,
        formatDateTime,
        formatSize
      };
    }
  }
  </script>
  
  <style scoped>
  .admin-settings-page {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  h1 {
    margin-bottom: 20px;
    color: #2d3748;
  }
  
  .settings-container {
    display: flex;
    gap: 25px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  /* 標籤側邊欄 */
  .settings-tabs {
    width: 200px;
    background-color: #f8f9fa;
    padding: 20px 0;
    border-right: 1px solid #e2e8f0;
  }
  
  .tab-btn {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    padding: 12px 20px;
    border: none;
    background: none;
    text-align: left;
    cursor: pointer;
    color: #4a5568;
    transition: background-color 0.2s;
  }
  
  .tab-btn:hover {
    background-color: #edf2f7;
  }
  
  .tab-btn.active {
    background-color: #ebf8ff;
    color: #3182ce;
    font-weight: 500;
    border-right: 3px solid #3182ce;
  }
  
  .tab-btn .material-symbols-outlined {
    font-size: 20px;
  }
  
  /* 設置內容 */
  .settings-content {
    flex: 1;
    padding: 25px;
    overflow-y: auto;
  }
  
  .settings-section {
    max-width: 800px;
  }
  
  h2 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #2d3748;
    font-size: 1.5rem;
  }
  
  .settings-card {
    background-color: #f8fafc;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #e2e8f0;
  }
  
  .settings-card h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #4a5568;
    font-size: 1.1rem;
  }
  
  .form-group {
    margin-bottom: 15px;
    display: flex;
    flex-direction: column;
  }
  
  .form-group:last-child {
    margin-bottom: 0;
  }
  
  .form-group label {
    margin-bottom: 5px;
    color: #4a5568;
    font-weight: 500;
  }
  
  .form-group input[type="text"],
  .form-group input[type="email"],
  .form-group input[type="number"],
  .form-group select,
  .form-group textarea {
    padding: 10px;
    border: 1px solid #cbd5e0;
    border-radius: 4px;
    font-size: 0.9rem;
  }
  
  .form-group select {
    background-color: #fff;
  }
  
  .form-group textarea {
    resize: vertical;
    min-height: 80px;
  }
  
  .form-group small {
    margin-top: 5px;
    color: #718096;
    font-size: 0.8rem;
  }
  
  /* 開關按鈕 */
  .toggle-switch {
    position: relative;
    width: 50px;
    height: 28px;
    margin-top: 5px;
  }
  
  .toggle-switch input {
    opacity: 0;
    width: 0;
    height: 0;
  }
  
  .toggle-switch label {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: #cbd5e0;
    transition: .4s;
    border-radius: 24px;
  }
  
  .toggle-switch label:before {
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
  
  .toggle-switch input:checked + label {
    background-color: #3182ce;
  }
  
  .toggle-switch input:checked + label:before {
    transform: translateX(26px);
  }
  
  .toggle-switch input:disabled + label {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* 按鈕 */
  .save-btn,
  .primary-btn,
  .secondary-btn,
  .danger-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    transition: opacity 0.2s;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  
  .save-btn {
    background-color: #3182ce;
    color: white;
    margin-top: 10px;
  }
  
  .primary-btn {
    background-color: #3182ce;
    color: white;
  }
  
  .secondary-btn {
    background-color: #edf2f7;
    color: #4a5568;
    border: 1px solid #cbd5e0;
  }
  
  .danger-btn {
    background-color: #f56565;
    color: white;
  }
  
  .save-btn:hover,
  .primary-btn:hover,
  .secondary-btn:hover,
  .danger-btn:hover {
    opacity: 0.9;
  }
  
  .action-buttons {
    display: flex;
    gap: 10px;
    margin-top: 15px;
  }
  
  /* 圖標按鈕 */
  .icon-btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 5px;
    border-radius: 4px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }
  
  .icon-btn:hover {
    background-color: #edf2f7;
  }
  
  .icon-btn.danger:hover {
    background-color: #fed7d7;
    color: #e53e3e;
  }
  
  /* 日期範圍 */
  .date-range {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .date-range input {
    flex: 1;
    padding: 8px;
    border: 1px solid #cbd5e0;
    border-radius: 4px;
  }
  
  /* 備份列表 */
  .backup-list {
    margin-top: 20px;
  }
  
  .backup-list h4 {
    margin-bottom: 10px;
    color: #4a5568;
  }
  
  table {
    width: 100%;
    border-collapse: collapse;
  }
  
  th, td {
    padding: 10px 15px;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
  }
  
  th {
    background-color: #f8fafc;
    font-weight: 500;
    color: #4a5568;
  }
  
  /* 日誌 */
  .log-filters {
    display: flex;
    gap: 15px;
    align-items: flex-end;
    margin-bottom: 15px;
    flex-wrap: wrap;
  }
  
  .log-container {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    height: 400px;
    overflow-y: auto;
    background-color: #1a202c;
    color: #f7fafc;
    font-family: monospace;
    font-size: 0.9rem;
  }
  
  .loading, .no-logs {
    padding: 20px;
    text-align: center;
    color: #a0aec0;
  }
  
  .log-entries {
    padding: 10px;
  }
  
  .log-entry {
    padding: 8px 10px;
    border-bottom: 1px solid #2d3748;
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }
  
  .log-entry:last-child {
    border-bottom: none;
  }
  
  .log-time {
    min-width: 180px;
    color: #a0aec0;
  }
  
  .log-level {
    min-width: 70px;
    font-weight: bold;
  }
  
  .log-entry.info .log-level {
    color: #4299e1;
  }
  
  .log-entry.warn .log-level {
    color: #ed8936;
  }
  
  .log-entry.error .log-level {
    color: #f56565;
  }
  
  .log-message {
    flex: 1;
    word-break: break-word;
  }
  
  .log-pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
    margin-top: 15px;
  }
  
  .log-pagination button {
    padding: 8px 12px;
    background-color: #edf2f7;
    border: 1px solid #cbd5e0;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .log-pagination button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* 確認對話框 */
  .confirm-dialog-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .confirm-dialog {
    background-color: white;
    border-radius: 8px;
    padding: 25px;
    width: 400px;
    max-width: 90%;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .confirm-dialog h3 {
    margin-top: 0;
    color: #2d3748;
  }
  
  .confirm-dialog p {
    color: #4a5568;
    margin-bottom: 20px;
  }
  
  .dialog-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  </style>