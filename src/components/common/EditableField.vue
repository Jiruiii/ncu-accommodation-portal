<template>
  <div class="editable-field">
    <div class="display-mode">
      <div class="field-content">
        <span class="field-value">{{ displayValue }}</span>
        <span v-if="showBadge" :class="['field-badge', badgeType]">{{
          badge
        }}</span>
      </div>
      <button v-if="editable" @click="openEditModal" class="edit-btn">
        {{ editButtonText }}
      </button>
    </div>

    <!-- 修改資料的彈窗 -->
    <div v-if="isEditing" class="modal-overlay" @click.self="cancelEditing">
      <div class="modal-content">
        <h3>{{ modalTitle || "修改資料" }}</h3>

        <div class="modal-form">
          <div class="form-group">
            <label>目前{{ fieldLabel }}</label>
            <div class="current-value">{{ displayValue }}</div>
          </div>

          <div class="form-group">
            <label>新{{ fieldLabel }}</label>
            <slot name="editor">
              <input
                ref="inputField"
                v-model="editValue"
                :type="inputType"
                :placeholder="placeholder"
                @keyup.enter="saveChanges"
              />
            </slot>
          </div>

          <!-- 驗證警告提示 -->
          <div v-if="showVerificationWarning" class="verification-warning">
            <i class="warning-icon">⚠️</i>
            <span>修改{{ fieldLabel }}後，您需要重新進行驗證</span>
          </div>

          <!-- 操作結果提示 -->
          <div v-if="statusMessage" :class="['status-message', statusType]">
            <i class="status-icon">{{
              statusType === "success" ? "✓" : "⚠️"
            }}</i>
            <span>{{ statusMessage }}</span>
          </div>
        </div>

        <div class="modal-buttons">
          <button @click="saveChanges" class="save-btn" :disabled="isSaving">
            <span v-if="isSaving" class="loading-spinner"></span>
            {{ isSaving ? "儲存中..." : "確認修改" }}
          </button>
          <button @click="cancelEditing" class="cancel-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "EditableField",
    props: {
      value: {
        type: [String, Number],
        default: "",
      },
      displayValue: {
        type: String,
        default: "",
      },
      editable: {
        type: Boolean,
        default: true,
      },
      editButtonText: {
        type: String,
        default: "修改",
      },
      inputType: {
        type: String,
        default: "text",
      },
      placeholder: {
        type: String,
        default: "",
      },
      showBadge: {
        type: Boolean,
        default: false,
      },
      badge: {
        type: String,
        default: "",
      },
      badgeType: {
        type: String,
        default: "neutral",
      },
      fieldLabel: {
        type: String,
        default: "資料",
      },
      modalTitle: {
        type: String,
        default: "",
      },
      showVerificationWarning: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        isEditing: false,
        editValue: "",
        isSaving: false,
        statusMessage: "",
        statusType: "error",
        saveTimeout: null,
      };
    },
    watch: {
      value: {
        immediate: true,
        handler(newVal) {
          this.editValue = newVal;
        },
      },
    },
    methods: {
      openEditModal() {
        this.isEditing = true;
        this.editValue = this.value;
        this.statusMessage = "";
        this.$nextTick(() => {
          if (this.$refs.inputField) {
            this.$refs.inputField.focus();
          }
        });
      },

      saveChanges() {
        if (this.editValue === this.value) {
          this.isEditing = false;
          return;
        }

        this.isSaving = true;
        this.statusMessage = "";

        try {
          // 使用事件回調方式處理父組件的 Promise
          this.$emit("save", this.editValue, {
            success: () => {
              this.statusType = "success";
              this.statusMessage = `${this.fieldLabel}已更新成功`;

              setTimeout(() => {
                this.isSaving = false;
                this.isEditing = false; 
                this.statusMessage = "";
              }, 1500);

              if (this.saveTimeout) {
                clearTimeout(this.saveTimeout);
                this.saveTimeout = null;
              }
            },
            error: (errorMsg) => {
              console.error("儲存失敗");
              this.isSaving = false;
              this.statusType = "error";
              this.statusMessage = errorMsg || `${this.fieldLabel}更新失敗，請稍後再試`;

              // 清除可能設置的超時計時器
              if (this.saveTimeout) {
                clearTimeout(this.saveTimeout);
                this.saveTimeout = null;
              }
            },
          });

          // 設置超時檢查，如果 5 秒後還沒收到回調，則假定操作超時
          this.saveTimeout = setTimeout(() => {
            if (this.isSaving) {
              this.isSaving = false;
              this.statusType = "error";
              this.statusMessage = `更新${this.fieldLabel}超時，請稍後再試`;
            }
          }, 5000);
        } catch (error) {
          console.error("儲存過程中發生錯誤:", error);
          this.isSaving = false;
          this.statusType = "error";
          this.statusMessage = `${this.fieldLabel}更新失敗，請稍後再試`;
        }
      },

      cancelEditing() {
        this.isEditing = false;
        this.editValue = this.value;
        this.statusMessage = "";
        if (this.saveTimeout) {
          clearTimeout(this.saveTimeout);
          this.saveTimeout = null;
        }
      },
    },

    beforeUnmount() {
      if (this.saveTimeout) {
        clearTimeout(this.saveTimeout);
        this.saveTimeout = null;
      }
    },
  };
</script>

<style scoped>
  .editable-field {
    width: 100%;
  }

  .display-mode {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .field-content {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    min-width: 0;
  }

  .field-value {
    font-size: 0.9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .field-badge {
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 10px;
    text-align: center;
    flex-shrink: 0;
  }

  .field-badge.verified {
    background-color: #4caf50;
    color: white;
  }

  .field-badge.unverified {
    background-color: #f5f5f5;
    color: #666;
  }

  .field-badge.neutral {
    background-color: #e0e0e0;
    color: #555;
  }

  .edit-btn {
    padding: 5px 10px;
    background-color: transparent;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.8rem;
    cursor: pointer;
    transition: all 0.2s;
    flex-shrink: 0;
  }

  .edit-btn:hover {
    background-color: #f5f5f5;
  }

  /* Modal 相關樣式 */
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
    background-color: white;
    padding: 30px;
    border-radius: 12px;
    max-width: 500px;
    width: 100%;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  }

  h3 {
    margin-top: 0;
    margin-bottom: 20px;
    color: #333;
    font-size: 1.5rem;
  }

  .modal-form {
    margin-bottom: 20px;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-group label {
    display: block;
    margin-bottom: 8px;
    font-weight: 500;
    color: #555;
  }

  .current-value {
    padding: 10px;
    background-color: #f5f5f5;
    border-radius: 4px;
    font-size: 0.9rem;
    color: #555;
  }

  .modal-form input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }

  .verification-warning {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    background-color: #fff3e0;
    border-left: 4px solid #ff9800;
    border-radius: 4px;
    margin: 15px 0;
  }

  .warning-icon {
    font-size: 1.2rem;
  }

  .modal-buttons {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
  }

  .save-btn,
  .cancel-btn {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .save-btn {
    background-color: #4a90e2;
    color: white;
  }

  .save-btn:hover:not(:disabled) {
    background-color: #3a80d2;
  }

  .save-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .cancel-btn {
    background-color: transparent;
    border: 1px solid #ddd;
    color: #666;
  }

  .cancel-btn:hover {
    background-color: #f5f5f5;
  }

  .status-message {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px;
    border-radius: 4px;
    margin: 15px 0 0;
  }
  
  .status-message.success {
    background-color: #e6f7e6;
    border-left: 4px solid #4caf50;
  }
  
  .status-message.error {
    background-color: #ffebee;
    border-left: 4px solid #f44336;
  }
  
  .status-icon {
    font-size: 1.2rem;
  }

  .loading-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    margin-right: 8px;
    animation: spin 1s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
