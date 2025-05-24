<template>
    <div class="comment-management-page">
      <div class="page-header">
        <h1>評論管理</h1>
        <div class="filters">
          <div class="filter-group">
            <label>評分</label>
            <select v-model="filters.rating">
              <option value="">全部評分</option>
              <option value="5">5星</option>
              <option value="4">4星</option>
              <option value="3">3星</option>
              <option value="2">2星</option>
              <option value="1">1星</option>
            </select>
          </div>
          <div class="filter-group">
            <label>住所類型</label>
            <select v-model="filters.accommodationType">
              <option value="">全部類型</option>
              <option value="apartment">公寓</option>
              <option value="house">獨棟</option>
              <option value="dormitory">宿舍</option>
            </select>
          </div>
          <div class="filter-group">
            <label>日期範圍</label>
            <div class="date-range">
              <input 
                type="date" 
                v-model="filters.dateFrom" 
                class="date-input"
                :max="today"
              />
              <span>至</span>
              <input 
                type="date" 
                v-model="filters.dateTo" 
                class="date-input"
                :max="today"
              />
            </div>
          </div>
          <div class="filter-group">
            <label>搜尋</label>
            <div class="search-input">
              <input 
                type="text" 
                v-model="filters.search" 
                placeholder="用戶名稱、內容關鍵字"
              />
              <button class="search-btn" @click="applyFilters">
                <span class="material-symbols-outlined">search</span>
              </button>
            </div>
          </div>
          <button class="reset-filters-btn" @click="resetFilters">
            <span class="material-symbols-outlined">restart_alt</span>
            重置篩選
          </button>
        </div>
      </div>
  
      <div class="comments-container">
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>載入評論中...</p>
        </div>
        
        <div v-else-if="comments.length === 0" class="empty-state">
          <span class="material-symbols-outlined">chat</span>
          <p>沒有符合條件的評論</p>
        </div>
        
        <div v-else class="comments-list">
          <div class="comment-card" v-for="comment in comments" :key="comment.id">
            <div class="comment-header">
              <div class="user-info">
                <img 
                  :src="comment.user_avatar || '/images/default-avatar.jpg'" 
                  alt="用戶頭像"
                  class="user-avatar"
                />
                <div class="user-details">
                  <div class="username">{{ comment.user_name || '使用者#' + comment.user_id }}</div>
                  <div class="comment-time">{{ formatDateTime(comment.created_at) }}</div>
                </div>
              </div>
              <div class="comment-rating">
                <span 
                  v-for="n in 5" 
                  :key="n" 
                  class="star" 
                  :class="{ 'filled': n <= comment.rating }"
                >★</span>
                <span class="rating-value">{{ comment.rating }}.0</span>
              </div>
            </div>
            
            <div class="property-info">
              <router-link 
                :to="`/admin/tables/accommodations?id=${comment.property_id}`"
                class="property-link"
              >
                {{ comment.property_title || '住所#' + comment.property_id }}
              </router-link>
              <span class="property-type" v-if="comment.property_type">
                {{ getPropertyTypeLabel(comment.property_type) }}
              </span>
              <span class="property-address" v-if="comment.property_address">
                {{ truncateText(comment.property_address, 50) }}
              </span>
            </div>
            
            <div class="comment-content">
              {{ comment.content }}
            </div>
            
            <div class="comment-images" v-if="comment.images && comment.images.length > 0">
              <div 
                v-for="(image, index) in comment.images" 
                :key="index"
                class="comment-image"
                @click="viewImage(image.url)"
              >
                <img :src="image.url" :alt="`評論圖片 ${index + 1}`" />
              </div>
            </div>
            
            <div class="comment-footer">
              <div class="comment-stats">
                <span class="stat-item">
                  <span class="material-symbols-outlined">thumb_up</span>
                  {{ comment.likes_count || 0 }}
                </span>
                <span class="stat-item">
                  <span class="material-symbols-outlined">reply</span>
                  {{ comment.replies_count || 0 }}
                </span>
                <span class="stat-item" v-if="comment.reports_count > 0">
                  <span class="material-symbols-outlined" style="color: #e53e3e;">flag</span>
                  {{ comment.reports_count }}
                </span>
              </div>
              
              <div class="comment-actions">
                <button class="action-btn view-btn" @click="viewDetails(comment)">
                  <span class="material-symbols-outlined">visibility</span>
                  詳情
                </button>
                <button class="action-btn edit-btn" @click="editComment(comment)">
                  <span class="material-symbols-outlined">edit</span>
                  編輯
                </button>
                <button class="action-btn delete-btn" @click="confirmDelete(comment)">
                  <span class="material-symbols-outlined">delete</span>
                  刪除
                </button>
              </div>
            </div>
            
            <!-- 回覆列表 (折疊) -->
            <div class="replies-section" v-if="comment.replies && comment.replies.length > 0">
              <div class="replies-toggle" @click="toggleReplies(comment)">
                <span class="material-symbols-outlined">
                  {{ comment.showReplies ? 'expand_less' : 'expand_more' }}
                </span>
                {{ comment.replies.length }} 則回覆
              </div>
              
              <div class="replies-list" v-if="comment.showReplies">
                <div class="reply-item" v-for="reply in comment.replies" :key="reply.id">
                  <div class="reply-header">
                    <div class="user-info">
                      <img 
                        :src="reply.user_avatar || '/images/default-avatar.jpg'" 
                        alt="用戶頭像"
                        class="user-avatar small"
                      />
                      <div class="user-details">
                        <div class="username">{{ reply.user_name || '使用者#' + reply.user_id }}</div>
                        <div class="comment-time">{{ formatDateTime(reply.created_at) }}</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="reply-content">
                    {{ reply.content }}
                  </div>
                  
                  <div class="reply-footer">
                    <div class="reply-actions">
                      <button class="action-btn small edit-btn" @click="editReply(reply)">
                        <span class="material-symbols-outlined">edit</span>
                      </button>
                      <button class="action-btn small delete-btn" @click="confirmDeleteReply(reply)">
                        <span class="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分頁 -->
        <div class="pagination" v-if="totalPages > 1">
          <button 
            class="page-btn"
            @click="changePage(currentPage - 1)"
            :disabled="currentPage === 1"
          >
            <span class="material-symbols-outlined">navigate_before</span>
          </button>
          
          <div class="page-numbers">
            <button 
              v-for="page in displayedPages" 
              :key="page"
              :class="['page-number', { active: page === currentPage }]"
              @click="changePage(page)"
            >
              {{ page }}
            </button>
          </div>
          
          <button 
            class="page-btn"
            @click="changePage(currentPage + 1)"
            :disabled="currentPage === totalPages"
          >
            <span class="material-symbols-outlined">navigate_next</span>
          </button>
        </div>
      </div>
  
      <!-- 評論詳情彈窗 -->
      <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeDetailsModal">
        <div class="modal-content details-modal">
          <div class="modal-header">
            <h2>評論詳情</h2>
            <button class="close-btn" @click="closeDetailsModal">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="details-section">
              <h3>評論資訊</h3>
              <div class="details-grid">
                <div class="detail-item">
                  <div class="detail-label">評論ID</div>
                  <div class="detail-value">{{ selectedComment.id }}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">評分</div>
                  <div class="detail-value">
                    <span 
                      v-for="n in 5" 
                      :key="n" 
                      class="star" 
                      :class="{ 'filled': n <= selectedComment.rating }"
                    >★</span>
                  </div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">建立時間</div>
                  <div class="detail-value">{{ formatDateTime(selectedComment.created_at) }}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">更新時間</div>
                  <div class="detail-value">{{ formatDateTime(selectedComment.updated_at) }}</div>
                </div>
                <div class="detail-item full-width">
                  <div class="detail-label">評論內容</div>
                  <div class="detail-value">{{ selectedComment.content }}</div>
                </div>
              </div>
            </div>
            
            <div class="details-section">
              <h3>用戶資訊</h3>
              <div class="details-grid">
                <div class="detail-item">
                  <div class="detail-label">用戶ID</div>
                  <div class="detail-value">{{ selectedComment.user_id }}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">用戶名稱</div>
                  <div class="detail-value">{{ selectedComment.user_name || '未知' }}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">郵箱</div>
                  <div class="detail-value">{{ selectedComment.user_email || '未知' }}</div>
                </div>
              </div>
            </div>
            
            <div class="details-section">
              <h3>住所資訊</h3>
              <div class="details-grid">
                <div class="detail-item">
                  <div class="detail-label">住所ID</div>
                  <div class="detail-value">{{ selectedComment.property_id }}</div>
                </div>
                <div class="detail-item">
                  <div class="detail-label">標題</div>
                  <div class="detail-value">{{ selectedComment.property_title || '未知' }}</div>
                </div>
                <div class="detail-item full-width">
                  <div class="detail-label">地址</div>
                  <div class="detail-value">{{ selectedComment.property_address || '未知' }}</div>
                </div>
              </div>
            </div>
            
            <div class="details-section" v-if="selectedComment.images && selectedComment.images.length > 0">
              <h3>評論圖片</h3>
              <div class="details-images">
                <div 
                  v-for="(image, index) in selectedComment.images" 
                  :key="index"
                  class="detail-image"
                  @click="viewImage(image.url)"
                >
                  <img :src="image.url" :alt="`評論圖片 ${index + 1}`" />
                </div>
              </div>
            </div>
            
            <div class="details-section" v-if="selectedComment.reports && selectedComment.reports.length > 0">
              <h3>舉報記錄</h3>
              <div class="reports-list">
                <div class="report-item" v-for="report in selectedComment.reports" :key="report.id">
                  <div class="report-header">
                    <div class="report-status" :class="report.status">
                      {{ getReportStatusText(report.status) }}
                    </div>
                    <div class="report-time">{{ formatDateTime(report.created_at) }}</div>
                  </div>
                  <div class="report-content">
                    <div class="report-reason">
                      <strong>原因:</strong> {{ report.reasons.join(', ') }}
                    </div>
                    <div class="report-description" v-if="report.description">
                      <strong>描述:</strong> {{ report.description }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="modal-actions">
              <button class="action-btn secondary-btn" @click="closeDetailsModal">關閉</button>
              <button class="action-btn edit-btn" @click="editCommentFromDetails">編輯評論</button>
              <button class="action-btn delete-btn" @click="confirmDeleteFromDetails">刪除評論</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 編輯評論彈窗 -->
      <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
        <div class="modal-content edit-modal">
          <div class="modal-header">
            <h2>{{ isEditingReply ? '編輯回覆' : '編輯評論' }}</h2>
            <button class="close-btn" @click="closeEditModal">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="saveEdit">
              <div class="form-group" v-if="!isEditingReply">
                <label>評分</label>
                <div class="rating-input">
                  <div class="stars-container">
                    <span 
                      v-for="n in 5" 
                      :key="n" 
                      class="rating-star" 
                      :class="{ 'selected': n <= editForm.rating }"
                      @click="editForm.rating = n"
                    >★</span>
                  </div>
                  <span class="rating-value">{{ editForm.rating }}.0</span>
                </div>
              </div>
              
              <div class="form-group">
                <label>{{ isEditingReply ? '回覆' : '評論' }}內容</label>
                <textarea 
                  v-model="editForm.content" 
                  rows="5" 
                  required
                  placeholder="請輸入內容"
                ></textarea>
              </div>
              
              <div class="modal-actions">
                <button type="button" class="action-btn secondary-btn" @click="closeEditModal">取消</button>
                <button type="submit" class="action-btn primary-btn">保存</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 刪除確認彈窗 -->
      <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
        <div class="modal-content delete-confirm-modal">
          <div class="modal-header">
            <h2>確認刪除</h2>
            <button class="close-btn" @click="cancelDelete">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          
          <div class="modal-body">
            <div class="confirm-message">
              <span class="material-symbols-outlined warning">warning</span>
              <p>您確定要刪除這{{ isEditingReply ? '則回覆' : '則評論' }}嗎？此操作無法撤銷。</p>
            </div>
            
            <div class="modal-actions">
              <button class="action-btn secondary-btn" @click="cancelDelete">取消</button>
              <button class="action-btn danger-btn" @click="confirmDeleteAction">確認刪除</button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 圖片查看器 -->
      <div v-if="showImageViewer" class="image-viewer" @click="closeImageViewer">
        <div class="image-container">
          <img :src="viewerImageUrl" alt="評論圖片" @click.stop />
        </div>
        <button class="close-viewer-btn" @click="closeImageViewer">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, computed, onMounted, watch } from 'vue';
  import { useRouter } from 'vue-router';
  import apiService from '@/services/api';
  import MessageService from '@/services/MessageService';
  
  export default {
    setup() {
      const router = useRouter();
      const loading = ref(false);
      const comments = ref([]);
      const totalItems = ref(0);
      const totalPages = ref(1);
      const currentPage = ref(1);
      const itemsPerPage = ref(10);
      
      // 篩選條件
      const filters = reactive({
        rating: '',
        accommodationType: '',
        dateFrom: '',
        dateTo: '',
        search: '',
      });
      
      // 顯示模態框
      const showDetailsModal = ref(false);
      const showEditModal = ref(false);
      const showDeleteConfirm = ref(false);
      const showImageViewer = ref(false);
      
      // 圖片查看器
      const viewerImageUrl = ref('');
      
      // 選中的項目
      const selectedComment = ref({});
      const selectedReply = ref({});
      const isEditingReply = ref(false);
      
      // 編輯表單
      const editForm = reactive({
        id: null,
        content: '',
        rating: 5,
      });
      
      // 今天日期（用於日期輸入框）
      const today = computed(() => {
        const now = new Date();
        return now.toISOString().split('T')[0];
      });
      
      // 計算要顯示的頁碼
      const displayedPages = computed(() => {
        const pages = [];
        const maxPagesToShow = 5;
        
        if (totalPages.value <= maxPagesToShow) {
          for (let i = 1; i <= totalPages.value; i++) {
            pages.push(i);
          }
        } else {
          let startPage = Math.max(1, currentPage.value - Math.floor(maxPagesToShow / 2));
          const endPage = Math.min(totalPages.value, startPage + maxPagesToShow - 1);
          
          if (endPage - startPage + 1 < maxPagesToShow) {
            startPage = Math.max(1, endPage - maxPagesToShow + 1);
          }
          
          for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
          }
        }
        
        return pages;
      });
      
      // 載入數據
      const loadComments = async () => {
        try {
          loading.value = true;
          
          // 構建查詢參數
          const params = {
            page: currentPage.value,
            per_page: itemsPerPage.value,
            include_relations: true, // 包含關聯數據：用戶、住所、回覆等
          };
          
          // 添加篩選條件
          if (filters.rating) params.rating = filters.rating;
          if (filters.accommodationType) params.property_type = filters.accommodationType;
          if (filters.dateFrom) params.date_from = filters.dateFrom;
          if (filters.dateTo) params.date_to = filters.dateTo;
          if (filters.search) params.search = filters.search;
          
          const response = await apiService.admin.getComments(params);
          
          if (response.success) {
            comments.value = response.comments.map(comment => ({
              ...comment,
              showReplies: false, // 添加控制回覆顯示的狀態
            }));
            totalItems.value = response.total;
            totalPages.value = response.pages;
          } else {
            MessageService.error(response.error || '載入評論失敗');
          }
        } catch (error) {
          console.error('載入評論失敗:', error);
          MessageService.error('載入評論失敗，請稍後再試');
        } finally {
          loading.value = false;
        }
      };
      
      // 切換回覆顯示狀態
      const toggleReplies = (comment) => {
        comment.showReplies = !comment.showReplies;
      };
      
      // 應用篩選條件
      const applyFilters = () => {
        currentPage.value = 1;
        loadComments();
      };
      
      // 重置篩選條件
      const resetFilters = () => {
        filters.rating = '';
        filters.accommodationType = '';
        filters.dateFrom = '';
        filters.dateTo = '';
        filters.search = '';
        
        currentPage.value = 1;
        loadComments();
      };
      
      // 切換頁碼
      const changePage = (page) => {
        if (page < 1 || page > totalPages.value) return;
        
        currentPage.value = page;
        loadComments();
      };
      
      // 查看評論詳情
      const viewDetails = async (comment) => {
        try {
          loading.value = true;
          
          // 獲取完整的評論詳情，包括報告
          const response = await apiService.admin.getCommentDetails(comment.id);
          
          if (response.success) {
            selectedComment.value = response.comment;
            showDetailsModal.value = true;
          } else {
            MessageService.error(response.error || '獲取評論詳情失敗');
          }
        } catch (error) {
          console.error('獲取評論詳情失敗:', error);
          MessageService.error('獲取評論詳情失敗，請稍後再試');
        } finally {
          loading.value = false;
        }
      };
      
      // 編輯評論
      const editComment = (comment) => {
        isEditingReply.value = false;
        selectedComment.value = comment;
        
        editForm.id = comment.id;
        editForm.content = comment.content;
        editForm.rating = comment.rating;
        
        showEditModal.value = true;
      };
      
      // 從詳情頁編輯評論
      const editCommentFromDetails = () => {
        closeDetailsModal();
        editComment(selectedComment.value);
      };
      
      // 編輯回覆
      const editReply = (reply) => {
        isEditingReply.value = true;
        selectedReply.value = reply;
        
        editForm.id = reply.id;
        editForm.content = reply.content;
        
        showEditModal.value = true;
      };
      
      // 保存編輯
      const saveEdit = async () => {
        try {
          let response;
          
          if (isEditingReply.value) {
            // 更新回覆
            response = await apiService.admin.updateReply(editForm.id, {
              content: editForm.content
            });
          } else {
            // 更新評論
            response = await apiService.admin.updateComment(editForm.id, {
              content: editForm.content,
              rating: editForm.rating
            });
          }
          
          if (response.success) {
            MessageService.success(isEditingReply.value ? '回覆已更新' : '評論已更新');
            closeEditModal();
            loadComments();
          } else {
            MessageService.error(response.error || (isEditingReply.value ? '更新回覆失敗' : '更新評論失敗'));
          }
        } catch (error) {
          console.error(isEditingReply.value ? '更新回覆失敗:' : '更新評論失敗:', error);
          MessageService.error((isEditingReply.value ? '更新回覆' : '更新評論') + '失敗，請稍後再試');
        }
      };
      
      // 確認刪除評論
      const confirmDelete = (comment) => {
        isEditingReply.value = false;
        selectedComment.value = comment;
        showDeleteConfirm.value = true;
      };
      
      // 從詳情頁確認刪除
      const confirmDeleteFromDetails = () => {
        closeDetailsModal();
        confirmDelete(selectedComment.value);
      };
      
      // 確認刪除回覆
      const confirmDeleteReply = (reply) => {
        isEditingReply.value = true;
        selectedReply.value = reply;
        showDeleteConfirm.value = true;
      };
      
      // 取消刪除
      const cancelDelete = () => {
        showDeleteConfirm.value = false;
      };
      
      // 確認刪除操作
      const confirmDeleteAction = async () => {
        try {
          let response;
          
          if (isEditingReply.value) {
            // 刪除回覆
            response = await apiService.admin.deleteReply(selectedReply.value.id);
          } else {
            // 刪除評論
            response = await apiService.admin.deleteComment(selectedComment.value.id);
          }
          
          if (response.success) {
            MessageService.success(isEditingReply.value ? '回覆已刪除' : '評論已刪除');
            showDeleteConfirm.value = false;
            loadComments();
          } else {
            MessageService.error(response.error || (isEditingReply.value ? '刪除回覆失敗' : '刪除評論失敗'));
          }
        } catch (error) {
          console.error(isEditingReply.value ? '刪除回覆失敗:' : '刪除評論失敗:', error);
          MessageService.error((isEditingReply.value ? '刪除回覆' : '刪除評論') + '失敗，請稍後再試');
        }
      };
      
      // 關閉詳情模態框
      const closeDetailsModal = () => {
        showDetailsModal.value = false;
      };
      
      // 關閉編輯模態框
      const closeEditModal = () => {
        showEditModal.value = false;
      };
      
      // 查看圖片
      const viewImage = (url) => {
        viewerImageUrl.value = url;
        showImageViewer.value = true;
      };
      
      // 關閉圖片查看器
      const closeImageViewer = () => {
        showImageViewer.value = false;
      };
      
      // 格式化日期時間
      const formatDateTime = (dateString) => {
        if (!dateString) return 'N/A';
        
        const date = new Date(dateString);
        return new Intl.DateTimeFormat('zh-TW', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }).format(date);
      };
      
      // 截斷文字
      const truncateText = (text, length) => {
        if (!text) return '';
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
      };
      
      // 獲取住所類型標籤
      const getPropertyTypeLabel = (type) => {
        const typeMap = {
          'apartment': '公寓',
          'house': '獨棟',
          'dormitory': '宿舍',
          'studio': '套房',
          'shared': '分租'
        };
        
        return typeMap[type] || type;
      };
      
      // 獲取舉報狀態文字
      const getReportStatusText = (status) => {
        const statusMap = {
          'pending': '待處理',
          'reviewed': '已審核',
          'resolved': '已解決',
          'rejected': '已拒絕'
        };
        
        return statusMap[status] || status;
      };
      
      // 初始化
      onMounted(() => {
        loadComments();
      });
      
      // 監聽篩選條件變化
      watch([filters.rating, filters.accommodationType], () => {
        applyFilters();
      });
      
      return {
        loading,
        comments,
        totalItems,
        totalPages,
        currentPage,
        filters,
        today,
        displayedPages,
        showDetailsModal,
        showEditModal,
        showDeleteConfirm,
        showImageViewer,
        viewerImageUrl,
        selectedComment,
        selectedReply,
        isEditingReply,
        editForm,
        
        loadComments,
        toggleReplies,
        applyFilters,
        resetFilters,
        changePage,
        viewDetails,
        editComment,
        editCommentFromDetails,
        editReply,
        saveEdit,
        confirmDelete,
        confirmDeleteFromDetails,
        confirmDeleteReply,
        cancelDelete,
        confirmDeleteAction,
        closeDetailsModal,
        closeEditModal,
        viewImage,
        closeImageViewer,
        formatDateTime,
        truncateText,
        getPropertyTypeLabel,
        getReportStatusText
      };
    }
  };
  </script>
  
  <style scoped>
  .comment-management-page {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  .page-header {
    margin-bottom: 20px;
  }
  
  .page-header h1 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #2d3748;
  }
  
  .filters {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    padding: 20px;
    background-color: #f8fafc;
    border-radius: 8px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    align-items: flex-end;
  }
  
  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  .filter-group label {
    font-size: 0.85rem;
    color: #4a5568;
    font-weight: 500;
  }
  
  .filter-group select,
  .filter-group input {
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 0.9rem;
    min-width: 120px;
  }
  
  .date-range {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .date-input {
    width: 140px;
  }
  
  .search-input {
    display: flex;
    align-items: center;
  }
  
  .search-input input {
    min-width: 200px;
    border-top-right-radius: 0;
    border-bottom-right-radius: 0;
    border-right: none;
  }
  
  .search-btn {
    padding: 8px 12px;
    background-color: #3182ce;
    color: white;
    border: none;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    cursor: pointer;
  }
  
  .reset-filters-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 8px 12px;
    background-color: #edf2f7;
    color: #4a5568;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
  }
  
  .reset-filters-btn:hover {
    background-color: #e2e8f0;
  }
  
  .loading-state,
  .empty-state {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 100px 0;
    color: #a0aec0;
  }
  
  .spinner {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    border: 3px solid #e2e8f0;
    border-top-color: #3182ce;
    animation: spin 1s infinite linear;
    margin-bottom: 15px;
  }
  
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  
  .empty-state .material-symbols-outlined {
    font-size: 48px;
    margin-bottom: 15px;
    color: #cbd5e0;
  }
  
  /* 評論卡片 */
  .comments-list {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .comment-card {
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow: hidden;
  }
  
  .comment-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  
  .user-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
    background-color: #e2e8f0;
  }
  
  .user-avatar.small {
    width: 30px;
    height: 30px;
  }
  
  .user-details {
    display: flex;
    flex-direction: column;
  }
  
  .username {
    font-weight: 500;
    color: #2d3748;
  }
  
  .comment-time {
    font-size: 0.8rem;
    color: #718096;
  }
  
  .comment-rating {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .star {
    color: #cbd5e0;
    font-size: 18px;
  }
  
  .star.filled {
    color: #ecc94b;
  }
  
  .rating-value {
    margin-left: 5px;
    font-weight: 500;
    color: #2d3748;
  }
  
  .property-info {
    padding: 12px 20px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .property-link {
    color: #3182ce;
    font-weight: 500;
    text-decoration: none;
  }
  
  .property-link:hover {
    text-decoration: underline;
  }
  
  .property-type {
    padding: 2px 8px;
    background-color: #e6f7ff;
    color: #0891b2;
    border-radius: 12px;
    font-size: 0.8rem;
  }
  
  .property-address {
    color: #718096;
    font-size: 0.9rem;
  }
  
  .comment-content {
    padding: 20px;
    color: #2d3748;
    line-height: 1.5;
  }
  
  .comment-images {
    padding: 0 20px 20px;
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .comment-image {
    width: 100px;
    height: 100px;
    border-radius: 4px;
    overflow: hidden;
    cursor: pointer;
  }
  
  .comment-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.2s;
  }
  
  .comment-image:hover img {
    transform: scale(1.05);
  }
  
  .comment-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 20px;
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
  }
  
  .comment-stats {
    display: flex;
    gap: 15px;
  }
  
  .stat-item {
    display: flex;
    align-items: center;
    gap: 5px;
    color: #718096;
    font-size: 0.9rem;
  }
  
  .comment-actions {
    display: flex;
    gap: 8px;
  }
  
  .action-btn {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 6px 12px;
    border: none;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }
  
  .action-btn.small {
    padding: 4px 8px;
  }
  
  .view-btn {
    background-color: #ebf8ff;
    color: #3182ce;
  }
  
  .edit-btn {
    background-color: #e6f7ee;
    color: #0e9f6e;
  }
  
  .delete-btn {
    background-color: #fee2e2;
    color: #e53e3e;
  }
  
  .primary-btn {
    background-color: #3182ce;
    color: white;
  }
  
  .secondary-btn {
    background-color: #edf2f7;
    color: #4a5568;
  }
  
  .danger-btn {
    background-color: #e53e3e;
    color: white;
  }
  
  .action-btn:hover {
    opacity: 0.9;
  }
  
  /* 回覆部分 */
  .replies-section {
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
  }
  
  .replies-toggle {
    display: flex;
    align-items: center;
    padding: 10px 20px;
    cursor: pointer;
    color: #4a5568;
    font-size: 0.9rem;
  }
  
  .replies-toggle:hover {
    background-color: #edf2f7;
  }
  
  .replies-list {
    padding: 0 20px 15px;
  }
  
  .reply-item {
    margin-top: 10px;
    background-color: #fff;
    border-radius: 6px;
    border: 1px solid #e2e8f0;
    overflow: hidden;
  }
  
  .reply-header {
    padding: 10px 15px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .reply-content {
    padding: 15px;
    color: #2d3748;
    line-height: 1.5;
  }
  
  .reply-footer {
    display: flex;
    justify-content: flex-end;
    padding: 8px 15px;
    background-color: #f8fafc;
    border-top: 1px solid #e2e8f0;
  }
  
  /* 分頁 */
  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 30px;
    gap: 10px;
  }
  
  .page-numbers {
    display: flex;
    gap: 5px;
  }
  
  .page-btn,
  .page-number {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: 1px solid #e2e8f0;
    background-color: #fff;
    color: #4a5568;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .page-number.active {
    background-color: #3182ce;
    color: white;
    border-color: #3182ce;
  }
  
  .page-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  /* 模態框 */
  .modal-overlay {
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
  
  .modal-content {
    background-color: #fff;
    border-radius: 8px;
    width: 90%;
    max-width: 700px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  
  .modal-content.edit-modal {
    max-width: 500px;
  }
  
  .modal-content.delete-confirm-modal {
    max-width: 400px;
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border-bottom: 1px solid #e2e8f0;
    position: sticky;
    top: 0;
    background-color: #fff;
    z-index: 1;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.2rem;
    color: #2d3748;
  }
  
  .close-btn {
    background: none;
    border: none;
    cursor: pointer;
    color: #718096;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .details-section {
    margin-bottom: 25px;
  }
  
  .details-section:last-child {
    margin-bottom: 0;
  }
  
  .details-section h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #2d3748;
    font-size: 1.1rem;
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 8px;
  }
  
  .details-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 15px;
  }
  
  .detail-item {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  
  .detail-item.full-width {
    grid-column: span 2;
  }
  
  .detail-label {
    font-size: 0.8rem;
    color: #718096;
    font-weight: 500;
  }
  
  .detail-value {
    color: #2d3748;
  }
  
  .details-images {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .detail-image {
    width: 120px;
    height: 120px;
    border-radius: 4px;
    overflow: hidden;
    cursor: pointer;
  }
  
  .detail-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.2s;
  }
  
  .detail-image:hover img {
    transform: scale(1.05);
  }
  
  .status-badge {
    display: inline-block;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
  }
  
  .status-badge.active {
    background-color: #e6f7ee;
    color: #0e9f6e;
  }
  
  .status-badge.pending {
    background-color: #fef3c7;
    color: #d97706;
  }
  
  .status-badge.banned {
    background-color: #fee2e2;
    color: #e53e3e;
  }
  
  .status-badge.unknown {
    background-color: #e2e8f0;
    color: #718096;
  }
  
  /* 舉報列表 */
  .reports-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .report-item {
    border: 1px solid #e2e8f0;
    border-radius: 6px;
    overflow: hidden;
  }
  
  .report-header {
    display: flex;
    justify-content: space-between;
    padding: 10px 15px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .report-status {
    display: inline-block;
    padding: 2px 8px;
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
    color: #e53e3e;
  }
  
  .report-time {
    font-size: 0.8rem;
    color: #718096;
  }
  
  .report-content {
    padding: 15px;
    color: #2d3748;
    line-height: 1.5;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  /* 表單 */
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 8px;
    color: #4a5568;
    font-weight: 500;
  }
  
  .form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    resize: vertical;
  }
  
  .rating-input {
    display: flex;
    align-items: center;
  }
  
  .stars-container {
    display: flex;
  }
  
  .rating-star {
    font-size: 24px;
    color: #cbd5e0;
    cursor: pointer;
  }
  
  .rating-star.selected {
    color: #ecc94b;
  }
  
  .modal-actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 20px;
  }
  
  /* 確認刪除 */
  .confirm-message {
    display: flex;
    align-items: center;
    gap: 15px;
  }
  
  .confirm-message .material-symbols-outlined.warning {
    font-size: 36px;
    color: #e53e3e;
  }
  
  /* 圖片查看器 */
  .image-viewer {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.9);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1100;
  }
  
  .image-container {
    max-width: 90%;
    max-height: 90%;
  }
  
  .image-container img {
    max-width: 100%;
    max-height: 90vh;
    object-fit: contain;
  }
  
  .close-viewer-btn {
    position: absolute;
    top: 20px;
    right: 20px;
    background: none;
    border: none;
    color: white;
    font-size: 30px;
    cursor: pointer;
  }
  </style>