<template>
    <div class="table-view">
      <div class="table-header">
        <div class="breadcrumb">
          <router-link to="/admin">儀表板</router-link> / {{ tableName }}
        </div>
        <h1>資料表: {{ tableName }}</h1>
        <div class="table-actions">
          <button @click="showAddModal = true" class="add-button">新增資料</button>
          <button @click="refreshData" class="refresh-button">重新整理</button>
        </div>
      </div>
      
      <div class="table-toolbar">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchTerm" 
            placeholder="搜尋..." 
            @input="handleSearch"
          />
        </div>
        <div class="pagination">
          <span>第 {{ currentPage }} / {{ totalPages }} 頁</span>
          <button 
            :disabled="currentPage === 1" 
            @click="changePage(currentPage - 1)"
          >上一頁</button>
          <button 
            :disabled="currentPage === totalPages" 
            @click="changePage(currentPage + 1)"
          >下一頁</button>
        </div>
      </div>
      
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th v-for="column in columns" :key="column.name" @click="sortBy(column.name)">
                {{ column.name }}
                <span v-if="sortColumn === column.name" class="sort-indicator">
                  {{ sortDirection === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in tableData" :key="getPrimaryKey(row)">
              <td v-for="column in columns" :key="column.name">
                {{ formatCellValue(row[column.name]) }}
              </td>
              <td class="actions-cell">
                <button @click="editRow(row)" class="edit-button">編輯</button>
                <button @click="deleteRow(row)" class="delete-button">刪除</button>
              </td>
            </tr>
            <tr v-if="tableData.length === 0">
              <td :colspan="columns.length + 1" class="no-data">
                無資料
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 編輯模態框 -->
      <div class="modal" v-if="showEditModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>編輯資料</h2>
            <button @click="showEditModal = false" class="close-button">&times;</button>
          </div>
          <div class="modal-body">
            <div v-for="column in editableColumns" :key="column.name" class="form-group">
              <label :for="column.name">{{ column.name }}</label>
              <input 
                :id="column.name"
                v-model="currentRow[column.name]"
                :type="getInputType(column.type)"
                :disabled="column.primary_key"
              />
              <small>{{ column.type }} {{ column.nullable ? '' : '(必填)' }}</small>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showEditModal = false" class="cancel-button">取消</button>
            <button @click="saveRow" class="save-button">保存</button>
          </div>
        </div>
      </div>
      
      <!-- 添加模態框 -->
      <div class="modal" v-if="showAddModal">
        <div class="modal-content">
          <div class="modal-header">
            <h2>新增資料</h2>
            <button @click="showAddModal = false" class="close-button">&times;</button>
          </div>
          <div class="modal-body">
            <div v-for="column in editableColumns" :key="column.name" class="form-group">
              <label :for="`new-${column.name}`">{{ column.name }}</label>
              <input 
                :id="`new-${column.name}`"
                v-model="newRow[column.name]"
                :type="getInputType(column.type)"
                :disabled="column.primary_key"
              />
              <small>{{ column.type }} {{ column.nullable ? '' : '(必填)' }}</small>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="showAddModal = false" class="cancel-button">取消</button>
            <button @click="addRow" class="save-button">新增</button>
          </div>
        </div>
      </div>
      
      <!-- 確認刪除對話框 -->
      <div class="modal" v-if="showDeleteConfirm">
        <div class="modal-content modal-sm">
          <div class="modal-header">
            <h2>確認刪除</h2>
            <button @click="showDeleteConfirm = false" class="close-button">&times;</button>
          </div>
          <div class="modal-body">
            <p>確定要刪除此條記錄嗎？此操作無法撤消。</p>
          </div>
          <div class="modal-footer">
            <button @click="showDeleteConfirm = false" class="cancel-button">取消</button>
            <button @click="confirmDelete" class="delete-button">確認刪除</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted, watch } from 'vue';
  import { useRoute } from 'vue-router';
  import apiService from '@/services/api';
  
  export default {
    setup() {
      const route = useRoute();
      const tableName = computed(() => route.params.tableName);
      
      const columns = ref([]);
      const tableData = ref([]);
      const totalItems = ref(0);
      const currentPage = ref(1);
      const itemsPerPage = ref(20);
      const sortColumn = ref('');
      const sortDirection = ref('asc');
      const searchTerm = ref('');
      const showEditModal = ref(false);
      const showAddModal = ref(false);
      const showDeleteConfirm = ref(false);
      const currentRow = ref({});
      const newRow = ref({});
      const rowToDelete = ref(null);
      
      const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value));
      
      const editableColumns = computed(() => {
        return columns.value.filter(column => !column.primary_key || column.name !== 'created_at' && column.name !== 'updated_at');
      });
      
      const primaryKeyColumn = computed(() => {
        return columns.value.find(column => column.primary_key);
      });
      
      // 加載表結構
      const loadTableStructure = async () => {
        try {
          const response = await apiService.admin.getTableStructure(tableName.value);
          columns.value = response.columns;
          // 初始化新行對象
          resetNewRow();
        } catch (error) {
          console.error('無法載入表結構:', error);
        }
      };
      
      // 加載表數據
      const loadTableData = async () => {
        try {
          const params = {
            page: currentPage.value,
            per_page: itemsPerPage.value,
            sort_by: sortColumn.value,
            sort_direction: sortDirection.value
          };
          
          const response = await apiService.admin.getTableData(tableName.value, params);
          tableData.value = response.data;
          totalItems.value = response.total;
        } catch (error) {
          console.error('無法載入表數據:', error);
        }
      };
      
      // 初始化新行對象
      const resetNewRow = () => {
        const row = {};
        columns.value.forEach(column => {
          if (!column.primary_key) {
            row[column.name] = null;
          }
        });
        newRow.value = row;
      };
      
      // 格式化單元格值
      const formatCellValue = (value) => {
        if (value === null || value === undefined) return '';
        
        if (typeof value === 'boolean') {
          return value ? '是' : '否';
        }
        
        // 檢測 ISO 日期字符串
        if (typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T/)) {
          return new Date(value).toLocaleString('zh-TW');
        }
        
        return value;
      };
      
      // 獲取主鍵值
      const getPrimaryKey = (row) => {
        const pkColumn = primaryKeyColumn.value;
        return pkColumn ? row[pkColumn.name] : JSON.stringify(row);
      };
      
      // 根據列類型獲取輸入類型
      const getInputType = (columnType) => {
        if (columnType.toLowerCase().includes('int')) {
          return 'number';
        } else if (columnType.toLowerCase().includes('date') || columnType.toLowerCase().includes('time')) {
          return 'datetime-local';
        } else if (columnType.toLowerCase().includes('boolean')) {
          return 'checkbox';
        } else {
          return 'text';
        }
      };
      
      // 切換排序
      const sortBy = (column) => {
        if (sortColumn.value === column) {
          sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
        } else {
          sortColumn.value = column;
          sortDirection.value = 'asc';
        }
        loadTableData();
      };
      
      // 翻頁
      const changePage = (page) => {
        currentPage.value = page;
        loadTableData();
      };
      
      // 處理搜索
      const handleSearch = () => {
        currentPage.value = 1; // 重置到第一頁
        loadTableData();
      };
      
      // 編輯行
      const editRow = (row) => {
        currentRow.value = { ...row };
        showEditModal.value = true;
      };
      
      // 保存編輯
      const saveRow = async () => {
        try {
          const pkColumn = primaryKeyColumn.value;
          if (!pkColumn) {
            throw new Error('找不到主鍵列');
          }
          
          const rowId = currentRow.value[pkColumn.name];
          await apiService.admin.updateTableRow(tableName.value, rowId, currentRow.value);
          showEditModal.value = false;
          loadTableData(); // 重新加載數據
        } catch (error) {
          console.error('保存失敗:', error);
        }
      };
      
      // 刪除行
      const deleteRow = (row) => {
        rowToDelete.value = row;
        showDeleteConfirm.value = true;
      };
      
      // 確認刪除
      const confirmDelete = async () => {
        try {
          const pkColumn = primaryKeyColumn.value;
          if (!pkColumn) {
            throw new Error('找不到主鍵列');
          }
          
          const rowId = rowToDelete.value[pkColumn.name];
          await apiService.admin.deleteTableRow(tableName.value, rowId);
          showDeleteConfirm.value = false;
          loadTableData(); // 重新加載數據
        } catch (error) {
          console.error('刪除失敗:', error);
        }
      };
      
      // 添加行
      const addRow = async () => {
        try {
          await apiService.admin.addTableRow(tableName.value, newRow.value);
          showAddModal.value = false;
          resetNewRow();
          loadTableData(); // 重新加載數據
        } catch (error) {
          console.error('添加失敗:', error);
        }
      };
      
      // 刷新數據
      const refreshData = () => {
        loadTableData();
      };
      
      // 當表名變更時重新加載數據
      watch(() => route.params.tableName, () => {
        loadTableStructure();
        currentPage.value = 1;
        loadTableData();
      });
      
      onMounted(() => {
        loadTableStructure();
        loadTableData();
      });
      
      return {
        tableName,
        columns,
        tableData,
        currentPage,
        totalPages,
        sortColumn,
        sortDirection,
        searchTerm,
        showEditModal,
        showAddModal,
        showDeleteConfirm,
        currentRow,
        newRow,
        editableColumns,
        formatCellValue,
        getPrimaryKey,
        getInputType,
        sortBy,
        changePage,
        handleSearch,
        editRow,
        saveRow,
        deleteRow,
        confirmDelete,
        addRow,
        refreshData
      };
    }
  }
  </script>
  
  <style scoped>
  .table-view {
    padding: 20px;
    max-width: 1400px;
    margin: 0 auto;
  }
  
  .table-header {
    margin-bottom: 30px;
  }
  
  .breadcrumb {
    margin-bottom: 10px;
    font-size: 0.9rem;
  }
  
  .breadcrumb a {
    color: #3a86ff;
    text-decoration: none;
  }
  
  h1 {
    margin: 0;
    margin-bottom: 20px;
  }
  
  .table-actions {
    display: flex;
    gap: 10px;
  }
  
  .table-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .search-bar input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 250px;
  }
  
  .pagination {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .pagination button {
    padding: 6px 12px;
    background: #f0f0f0;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
  }
  
  .pagination button:disabled {
    background: #f9f9f9;
    color: #aaa;
    cursor: not-allowed;
  }
  
  .table-container {
    overflow-x: auto;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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
    cursor: pointer;
    position: relative;
  }
  
  th:hover {
    background-color: #e9ecef;
  }
  
  .sort-indicator {
    margin-left: 5px;
  }
  
  tr:hover {
    background-color: #f8f9fa;
  }
  
  .no-data {
    text-align: center;
    padding: 30px;
    color: #888;
  }
  
  .actions-cell {
    display: flex;
    gap: 8px;
  }
  
  .modal {
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
    background-color: white;
    border-radius: 8px;
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  }
  
  .modal-sm {
    max-width: 400px;
  }
  
  .modal-header {
    padding: 15px 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.2rem;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-footer {
    padding: 15px 20px;
    border-top: 1px solid #eee;
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
  }
  
  .form-group input {
    width: 100%;
    padding: 8px 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
  }
  
  .form-group small {
    display: block;
    margin-top: 4px;
    color: #777;
    font-size: 0.8rem;
  }
  
  /* 按鈕樣式 */
  button {
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background-color 0.2s;
  }
  
  .add-button {
    background-color: #0ca678;
    color: white;
    border: none;
  }
  
  .add-button:hover {
    background-color: #099268;
  }
  
  .refresh-button {
    background-color: #f8f9fa;
    color: #495057;
    border: 1px solid #ddd;
  }
  
  .refresh-button:hover {
    background-color: #e9ecef;
  }
  
  .edit-button {
    background-color: #3a86ff;
    color: white;
    border: none;
  }
  
  .edit-button:hover {
    background-color: #2667cc;
  }
  
  .delete-button {
    background-color: #e03131;
    color: white;
    border: none;
  }
  
  .delete-button:hover {
    background-color: #c92a2a;
  }
  
  .save-button {
    background-color: #0ca678;
    color: white;
    border: none;
  }
  
  .save-button:hover {
    background-color: #099268;
  }
  
  .cancel-button {
    background-color: #f8f9fa;
    color: #495057;
    border: 1px solid #ddd;
  }
  
  .cancel-button:hover {
    background-color: #e9ecef;
  }
  
  .close-button {
    background: none;
    border: none;
    font-size: 1.5rem;
    padding: 0;
    cursor: pointer;
  }
  </style>