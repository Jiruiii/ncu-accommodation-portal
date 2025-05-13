<template>
    <div class="editable-field">
      <div v-if="!isEditing" class="display-mode">
        <div class="field-content">
          <span class="field-value">{{ displayValue }}</span>
          <span v-if="showBadge" :class="['field-badge', badgeType]">{{ badge }}</span>
        </div>
        <button v-if="editable" @click="startEditing" class="edit-btn">
          {{ editButtonText }}
        </button>
      </div>
      <div v-else class="edit-mode">
        <slot name="editor">
          <input 
            ref="inputField"
            v-model="editValue" 
            :type="inputType" 
            :placeholder="placeholder"
            @keyup.enter="saveChanges"
            @keyup.escape="cancelEditing"
          />
        </slot>
        <div class="edit-actions">
          <button @click="saveChanges" class="save-btn" :disabled="isSaving">
            <span v-if="isSaving" class="loading-spinner"></span>
            {{ isSaving ? '儲存中...' : '儲存' }}
          </button>
          <button @click="cancelEditing" class="cancel-btn">取消</button>
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
        default: ""
      },
      displayValue: {
        type: String,
        default: ""
      },
      editable: {
        type: Boolean,
        default: true
      },
      editButtonText: {
        type: String,
        default: "修改"
      },
      inputType: {
        type: String,
        default: "text"
      },
      placeholder: {
        type: String,
        default: ""
      },
      showBadge: {
        type: Boolean,
        default: false
      },
      badge: {
        type: String,
        default: ""
      },
      badgeType: {
        type: String,
        default: "neutral"
      }
    },
    data() {
      return {
        isEditing: false,
        editValue: "",
        isSaving: false
      };
    },
    watch: {
      value: {
        immediate: true,
        handler(newVal) {
          this.editValue = newVal;
        }
      }
    },
    methods: {
      startEditing() {
        this.isEditing = true;
        this.editValue = this.value;
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
        this.$emit("save", this.editValue)
          .then(() => {
            this.isEditing = false;
          })
          .catch((error) => {
            console.error("儲存失敗:", error);
          })
          .finally(() => {
            this.isSaving = false;
          });
      },
      cancelEditing() {
        this.isEditing = false;
        this.editValue = this.value;
      }
    }
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
  }
  
  .field-value {
    font-size: 0.9rem;
  }
  
  .field-badge {
    font-size: 0.7rem;
    padding: 2px 6px;
    border-radius: 10px;
    text-align: center;
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
  }
  
  .edit-btn:hover {
    background-color: #f5f5f5;
  }
  
  .edit-mode {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .edit-mode input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 0.9rem;
  }
  
  .edit-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
  }
  
  .save-btn, .cancel-btn {
    padding: 5px 15px;
    border: none;
    border-radius: 4px;
    font-size: 0.8rem;
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
  
  .loading-spinner {
    display: inline-block;
    width: 12px;
    height: 12px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top-color: white;
    margin-right: 5px;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  </style>