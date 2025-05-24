<template>
      <div class="landlord-verification-page">
        <div class="landlord-verification-content">
        <div class="verification-header">
          <h1>房東身份認證</h1>
          <p>完成認證後，您將獲得發布房源、管理租約等特權</p>
        </div>
    
        <div class="verification-progress">
          <div class="progress-steps">
            <div 
              v-for="(step, index) in steps" 
              :key="index"
              :class="['step', { 'active': currentStep >= index, 'completed': currentStep > index }]"
            >
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-label">{{ step.label }}</div>
            </div>
          </div>
          <div class="progress-bar">
            <div class="progress" :style="{ width: progressPercentage + '%' }"></div>
          </div>
        </div>
    
        <!-- 基本資料表單 -->
        <div v-if="currentStep === 0" class="verification-form">
          <h2>基本資料</h2>
          <div class="form-group">
            <label>真實姓名 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="formData.realName" 
              placeholder="請輸入您的真實姓名，需與證件一致"
            />
            <div class="error-message" v-if="validationErrors.realName">{{ validationErrors.realName }}</div>
          </div>
          
          <div class="form-group">
            <label>身份證號碼 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="formData.idNumber" 
              placeholder="請輸入您的身份證號碼"
            />
            <div class="error-message" v-if="validationErrors.idNumber">{{ validationErrors.idNumber }}</div>
          </div>
          
          <div class="form-group">
            <label>聯絡電話 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="formData.phone" 
              placeholder="請輸入您的聯絡電話"
            />
            <div class="error-message" v-if="validationErrors.phone">{{ validationErrors.phone }}</div>
          </div>
          
          <div class="form-group">
            <label>電子郵件 <span class="required">*</span></label>
            <input 
              type="email" 
              v-model="formData.email" 
              placeholder="請輸入您的電子郵件"
            />
            <div class="error-message" v-if="validationErrors.email">{{ validationErrors.email }}</div>
          </div>
          
          <div class="form-group">
            <label>地址 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="formData.address" 
              placeholder="請輸入您的地址"
            />
            <div class="error-message" v-if="validationErrors.address">{{ validationErrors.address }}</div>
          </div>
          
          <div class="form-actions">
            <button class="next-btn" @click="validateAndContinue">繼續</button>
          </div>
        </div>
    
        <!-- 身份驗證表單 -->
        <div v-else-if="currentStep === 1" class="verification-form">
          <h2>身份驗證</h2>
          <div class="upload-section">
            <div class="upload-card">
              <h3>身份證正面 <span class="required">*</span></h3>
              <div 
                class="upload-area"
                :class="{ 'has-file': formData.idCardFront }"
                @click="triggerFileUpload('idCardFront')"
              >
                <div v-if="!formData.idCardFront" class="upload-placeholder">
                  <i class="fa-solid fa-upload"></i>
                  <p>點擊上傳或拖曳檔案至此</p>
                </div>
                <div v-else class="file-preview">
                  <img :src="formData.idCardFrontPreview" alt="身份證正面預覽" />
                  <button class="remove-file" @click.stop="removeFile('idCardFront')">
                    <i class="fa-solid fa-times"></i>
                  </button>
                </div>
              </div>
              <input 
                type="file" 
                ref="idCardFrontInput"
                style="display: none" 
                accept="image/*"
                @change="handleFileUpload('idCardFront', $event)"
              />
              <div class="error-message" v-if="validationErrors.idCardFront">{{ validationErrors.idCardFront }}</div>
            </div>
            
            <div class="upload-card">
              <h3>身份證反面 <span class="required">*</span></h3>
              <div 
                class="upload-area"
                :class="{ 'has-file': formData.idCardBack }"
                @click="triggerFileUpload('idCardBack')"
              >
                <div v-if="!formData.idCardBack" class="upload-placeholder">
                  <i class="fa-solid fa-upload"></i>
                  <p>點擊上傳或拖曳檔案至此</p>
                </div>
                <div v-else class="file-preview">
                  <img :src="formData.idCardBackPreview" alt="身份證反面預覽" />
                  <button class="remove-file" @click.stop="removeFile('idCardBack')">
                    <i class="fa-solid fa-times"></i>
                  </button>
                </div>
              </div>
              <input 
                type="file" 
                ref="idCardBackInput"
                style="display: none" 
                accept="image/*"
                @change="handleFileUpload('idCardBack', $event)"
              />
              <div class="error-message" v-if="validationErrors.idCardBack">{{ validationErrors.idCardBack }}</div>
            </div>
          </div>
          
          <div class="privacy-notice">
            <input type="checkbox" id="privacyConsent" v-model="formData.privacyConsent" />
            <label for="privacyConsent">
              我同意系統收集、處理及利用我提供的個人資料，用於身份驗證目的。系統將依據<a href="#">隱私權政策</a>保護我的個人資料。
            </label>
            <div class="error-message" v-if="validationErrors.privacyConsent">{{ validationErrors.privacyConsent }}</div>
          </div>
          
          <div class="form-actions">
            <button class="back-btn" @click="currentStep--">返回</button>
            <button class="next-btn" @click="validateAndContinue">繼續</button>
          </div>
        </div>
    
        <!-- 房源相關資訊 -->
        <div v-else-if="currentStep === 2" class="verification-form">
          <h2>房產資訊</h2>
          <div class="form-group">
            <label>您是否有房產出租經驗？</label>
            <div class="radio-group">
              <label>
                <input type="radio" v-model="formData.hasRentalExperience" :value="true" />
                是
              </label>
              <label>
                <input type="radio" v-model="formData.hasRentalExperience" :value="false" />
                否
              </label>
            </div>
          </div>
          
          <div class="form-group">
            <label>您打算出租的房屋數量</label>
            <select v-model="formData.propertyCount">
              <option value="1">1間</option>
              <option value="2-5">2-5間</option>
              <option value="6-10">6-10間</option>
              <option value="10+">10間以上</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>房屋類型 <span class="required">*</span></label>
            <div class="checkbox-group">
              <label v-for="type in propertyTypes" :key="type.value">
                <input type="checkbox" v-model="formData.propertyTypes" :value="type.value" />
                {{ type.label }}
              </label>
            </div>
            <div class="error-message" v-if="validationErrors.propertyTypes">{{ validationErrors.propertyTypes }}</div>
          </div>
          
          <div class="form-group">
            <label>房屋所在區域 <span class="required">*</span></label>
            <select v-model="formData.propertyArea">
              <option value="">請選擇區域</option>
              <option value="中壢區">中壢區</option>
              <option value="平鎮區">平鎮區</option>
              <option value="龍潭區">龍潭區</option>
              <option value="楊梅區">楊梅區</option>
              <option value="其他">其他</option>
            </select>
            <div class="error-message" v-if="validationErrors.propertyArea">{{ validationErrors.propertyArea }}</div>
          </div>
          
          <div class="form-group">
            <label>其他資訊或備註</label>
            <textarea
              v-model="formData.additionalInfo"
              placeholder="請輸入任何您希望我們知道的額外資訊"
              rows="4"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button class="back-btn" @click="currentStep--">返回</button>
            <button class="next-btn" @click="validateAndContinue">繼續</button>
          </div>
        </div>
    
        <!-- 提交確認 -->
        <div v-else-if="currentStep === 3" class="verification-form">
          <h2>確認提交</h2>
          <div class="confirmation-summary">
            <p>請確認以下資訊無誤，提交後將由管理員進行審核，審核結果將發送至您的郵箱。</p>
            
            <div class="summary-section">
              <h3>基本資料</h3>
              <div class="summary-item">
                <span class="summary-label">真實姓名</span>
                <span class="summary-value">{{ formData.realName }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">身份證號碼</span>
                <span class="summary-value">{{ maskIdNumber(formData.idNumber) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">聯絡電話</span>
                <span class="summary-value">{{ formData.phone }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">電子郵件</span>
                <span class="summary-value">{{ formData.email }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">地址</span>
                <span class="summary-value">{{ formData.address }}</span>
              </div>
            </div>
            
            <div class="summary-section">
              <h3>房產資訊</h3>
              <div class="summary-item">
                <span class="summary-label">出租經驗</span>
                <span class="summary-value">{{ formData.hasRentalExperience ? '有' : '無' }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">房屋數量</span>
                <span class="summary-value">{{ formData.propertyCount }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">房屋類型</span>
                <span class="summary-value">{{ getPropertyTypeLabels().join(', ') }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">所在區域</span>
                <span class="summary-value">{{ formData.propertyArea }}</span>
              </div>
              <div class="summary-item" v-if="formData.additionalInfo">
                <span class="summary-label">備註</span>
                <span class="summary-value">{{ formData.additionalInfo }}</span>
              </div>
            </div>
            
            <div class="terms-agreement">
              <input type="checkbox" id="termsConsent" v-model="formData.termsConsent" />
              <label for="termsConsent">
                我確認所提供的資訊真實無誤，並同意遵守系統的<a href="#">服務條款</a>和<a href="#">房東規範</a>。
              </label>
              <div class="error-message" v-if="validationErrors.termsConsent">{{ validationErrors.termsConsent }}</div>
            </div>
          </div>
          
          <div class="form-actions">
            <button class="back-btn" @click="currentStep--">返回</button>
            <button class="submit-btn" @click="submitVerification" :disabled="isSubmitting">
              <span v-if="isSubmitting">
                <i class="fa-solid fa-spinner fa-spin"></i> 提交中...
              </span>
              <span v-else>提交申請</span>
            </button>
          </div>
        </div>
    
        <!-- 提交完成 -->
        <div v-else-if="currentStep === 4" class="verification-form success-form">
          <div class="success-message">
            <i class="fa-solid fa-check-circle"></i>
            <h2>申請提交成功！</h2>
            <p>您的房東認證申請已成功提交，我們會在1-3個工作日內完成審核。</p>
            <p>審核結果將發送至您的電子信箱：{{ formData.email }}</p>
            
            <div class="verification-status">
              <div class="status-label">審核狀態</div>
              <div class="status-value pending">審核中</div>
            </div>
            
            <div class="next-steps">
              <h3>後續步驟</h3>
              <ul>
                <li>請保持電話暢通，我們可能需要與您電話確認</li>
                <li>審核通過後，您將獲得房東特權，可以發布和管理房源</li>
                <li>您可以隨時在個人資料頁面查看審核狀態</li>
              </ul>
            </div>
            
            <div class="form-actions">
              <button class="home-btn" @click="goToProfile">返回個人資料</button>
              <button class="dashboard-btn" @click="goToLandlordDashboard">前往房東中心</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, reactive, computed } from 'vue';
  import { useRouter } from 'vue-router';
  import apiService from '@/services/api';
  
  export default {
    name: 'LandlordVerificationPage',
    setup() {
      const router = useRouter();
      const currentStep = ref(0);
      const isSubmitting = ref(false);
      
      // 驗證表單錯誤
      const validationErrors = reactive({});
      
      // 檔案上傳 ref
      const idCardFrontInput = ref(null);
      const idCardBackInput = ref(null);
      
      // 表單數據
      const formData = reactive({
        // 基本資料
        realName: '',
        idNumber: '',
        phone: '',
        email: '',
        address: '',
        
        // 身份驗證
        idCardFront: null,
        idCardFrontPreview: '',
        idCardBack: null,
        idCardBackPreview: '',
        privacyConsent: false,
        
        // 房產資訊
        hasRentalExperience: false,
        propertyCount: '1',
        propertyTypes: [],
        propertyArea: '',
        additionalInfo: '',
        
        // 提交確認
        termsConsent: false
      });
      
      // 步驟設定
      const steps = [
        { label: '基本資料' },
        { label: '身份驗證' },
        { label: '房產資訊' },
        { label: '確認提交' }
      ];
      
      // 房屋類型選項
      const propertyTypes = [
        { value: 'apartment', label: '公寓/電梯大樓' },
        { value: 'house', label: '獨棟/透天厝' },
        { value: 'studio', label: '套房' },
        { value: 'shared', label: '分租套房/雅房' },
        { value: 'dorm', label: '學生宿舍' },
        { value: 'other', label: '其他' }
      ];
      
      // 進度百分比計算
      const progressPercentage = computed(() => {
        return (currentStep.value / (steps.length - 0.5)) * 100;
      });
      
      // 觸發檔案上傳
      const triggerFileUpload = (type) => {
        if (type === 'idCardFront') {
          idCardFrontInput.value.click();
        } else if (type === 'idCardBack') {
          idCardBackInput.value.click();
        }
      };
      
      // 處理檔案上傳
      const handleFileUpload = (type, event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        if (!file.type.match('image.*')) {
          validationErrors[type] = '請上傳圖片檔案';
          return;
        }
        
        if (file.size > 5 * 1024 * 1024) {
          validationErrors[type] = '檔案大小不得超過 5MB';
          return;
        }
        
        const reader = new FileReader();
        reader.onload = (e) => {
          if (type === 'idCardFront') {
            formData.idCardFront = file;
            formData.idCardFrontPreview = e.target.result;
          } else if (type === 'idCardBack') {
            formData.idCardBack = file;
            formData.idCardBackPreview = e.target.result;
          }
        };
        reader.readAsDataURL(file);
        
        // 清除相關錯誤
        validationErrors[type] = '';
      };
      
      // 移除已上傳的檔案
      const removeFile = (type) => {
        if (type === 'idCardFront') {
          formData.idCardFront = null;
          formData.idCardFrontPreview = '';
        } else if (type === 'idCardBack') {
          formData.idCardBack = null;
          formData.idCardBackPreview = '';
        }
      };
      
      // 驗證並繼續下一步
      const validateAndContinue = () => {
        // 清空驗證錯誤
        Object.keys(validationErrors).forEach(key => {
          validationErrors[key] = '';
        });
        
        // 根據當前步驟進行不同的驗證
        if (currentStep.value === 0) {
          // 基本資料驗證
          if (!formData.realName) {
            validationErrors.realName = '請輸入真實姓名';
          }
          
          if (!formData.idNumber) {
            validationErrors.idNumber = '請輸入身份證號碼';
          } else if (!/^[A-Z][12]\d{8}$/.test(formData.idNumber)) {
            validationErrors.idNumber = '請輸入有效的身份證號碼';
          }
          
          if (!formData.phone) {
            validationErrors.phone = '請輸入聯絡電話';
          } else if (!/^09\d{8}$/.test(formData.phone)) {
            validationErrors.phone = '請輸入有效的手機號碼';
          }
          
          if (!formData.email) {
            validationErrors.email = '請輸入電子郵件';
          } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
            validationErrors.email = '請輸入有效的電子郵件格式';
          }
          
          if (!formData.address) {
            validationErrors.address = '請輸入地址';
          }
        } else if (currentStep.value === 1) {
          // 身份驗證驗證
          if (!formData.idCardFront) {
            validationErrors.idCardFront = '請上傳身份證正面照片';
          }
          
          if (!formData.idCardBack) {
            validationErrors.idCardBack = '請上傳身份證反面照片';
          }
          
          if (!formData.privacyConsent) {
            validationErrors.privacyConsent = '請同意隱私權政策才能繼續';
          }
        } else if (currentStep.value === 2) {
          // 房產資訊驗證
          if (formData.propertyTypes.length === 0) {
            validationErrors.propertyTypes = '請至少選擇一種房屋類型';
          }
          
          if (!formData.propertyArea) {
            validationErrors.propertyArea = '請選擇房屋所在區域';
          }
        } else if (currentStep.value === 3) {
          // 提交確認驗證
          if (!formData.termsConsent) {
            validationErrors.termsConsent = '請同意服務條款才能提交申請';
          }
        }
        
        // 檢查是否有驗證錯誤
        if (Object.values(validationErrors).some(error => error)) {
          return;
        }
        
        // 進入下一步
        currentStep.value++;
      };
      
      // 遮蔽身份證號碼，僅顯示前後幾位
      const maskIdNumber = (idNumber) => {
        if (!idNumber) return '';
        return idNumber.substring(0, 3) + '****' + idNumber.substring(7);
      };
      
      // 取得房屋類型標籤
      const getPropertyTypeLabels = () => {
        return formData.propertyTypes.map(type => {
          const found = propertyTypes.find(item => item.value === type);
          return found ? found.label : type;
        });
      };
      
      // 提交驗證申請
      const submitVerification = async () => {
        if (!formData.termsConsent) {
          validationErrors.termsConsent = '請同意服務條款才能提交申請';
          return;
        }
        
        isSubmitting.value = true;
        
        try {
          // 將表單數據處理成 FormData 格式
          const submitData = new FormData();
          
          // 添加基本資料
          submitData.append('realName', formData.realName);
          submitData.append('idNumber', formData.idNumber);
          submitData.append('phone', formData.phone);
          submitData.append('email', formData.email);
          submitData.append('address', formData.address);
          
          // 添加身份證照片
          if (formData.idCardFront) {
            submitData.append('idCardFront', formData.idCardFront);
          }
          
          if (formData.idCardBack) {
            submitData.append('idCardBack', formData.idCardBack);
          }
          
          // 添加房產資訊
          submitData.append('hasRentalExperience', formData.hasRentalExperience);
          submitData.append('propertyCount', formData.propertyCount);
          submitData.append('propertyTypes', JSON.stringify(formData.propertyTypes));
          submitData.append('propertyArea', formData.propertyArea);
          submitData.append('additionalInfo', formData.additionalInfo);
          
          // 發送 API 請求
          const response = await apiService.landlord.submitVerification(submitData);
          
          // 處理成功響應
          if (response && response.success) {
            // 進入最後一步（成功頁面）
            currentStep.value = 4;
          } else {
            throw new Error(response.message || '提交失敗，請稍後再試');
          }
        } catch (error) {
          console.error('提交房東認證申請失敗:', error);
          alert(`提交失敗: ${error.message || '未知錯誤'}`);
        } finally {
          isSubmitting.value = false;
        }
      };
      
      // 導航方法
      const goToProfile = () => {
        router.push('/profile');
      };
      
      const goToLandlordDashboard = () => {
        router.push('/landlord/dashboard');
      };
      
      return {
        currentStep,
        steps,
        formData,
        validationErrors,
        propertyTypes,
        idCardFrontInput,
        idCardBackInput,
        isSubmitting,
        progressPercentage,
        triggerFileUpload,
        handleFileUpload,
        removeFile,
        validateAndContinue,
        maskIdNumber,
        getPropertyTypeLabels,
        submitVerification,
        goToProfile,
        goToLandlordDashboard
      };
    }
  };
  </script>
  
  <style scoped>
  .landlord-verification-page {
    margin: 0 auto;
    padding: 40px 30px;
    overflow-y: auto;
    height: calc(100vh - 80px);
  }

  .landlord.verification-content{
    max-width: 900px;
    position: relative;
  }
  
  .verification-header {
    text-align: center;
    margin-bottom: 40px;
  }
  
  .verification-header h1 {
    font-size: 2rem;
    margin-bottom: 10px;
    color: #333;
  }
  
  .verification-header p {
    color: #666;
  }
  
  .verification-progress {
    margin-bottom: 40px;
  }
  
  .progress-steps {
    display: flex;
    justify-content: space-between;
    margin-bottom: 15px;
  }
  
  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 25%;
  }
  
  .step-number {
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    background-color: #e0e0e0;
    color: #666;
    margin-bottom: 8px;
    font-weight: bold;
  }
  
  .step.active .step-number,
  .step.completed .step-number {
    background-color: #4CAF50;
    color: white;
  }
  
  .step-label {
    font-size: 0.9rem;
    color: #666;
  }
  
  .step.active .step-label,
  .step.completed .step-label {
    color: #4CAF50;
    font-weight: 500;
  }
  
  .progress-bar {
    height: 6px;
    background-color: #e0e0e0;
    border-radius: 3px;
    overflow: hidden;
  }
  
  .progress {
    height: 100%;
    background-color: #4CAF50;
    transition: width 0.3s ease;
  }
  
  .verification-form {
    background-color: white;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    padding: 30px;
    margin-bottom: 30px;
  }
  
  .verification-form h2 {
    font-size: 1.5rem;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
    color: #333;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: 500;
    color: #555;
  }
  
  .form-group input[type="text"],
  .form-group input[type="email"],
  .form-group select,
  .form-group textarea {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    font-size: 1rem;
  }
  
  .form-group input[type="text"]:focus,
  .form-group input[type="email"]:focus,
  .form-group select:focus,
  .form-group textarea:focus {
    outline: none;
    border-color: #7CB9E8;
    box-shadow: 0 0 0 2px rgba(124, 185, 232, 0.2);
  }
  
  .required {
    color: #e53935;
  }
  
  .error-message {
    color: #e53935;
    font-size: 0.85rem;
    margin-top: 5px;
  }
  
  .radio-group,
  .checkbox-group {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-top: 5px;
  }
  
  .radio-group label,
  .checkbox-group label {
    display: flex;
    align-items: center;
    gap: 5px;
    font-weight: normal;
    cursor: pointer;
  }
  
  .upload-section {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
  }
  
  .upload-card {
    flex: 1;
  }
  
  .upload-card h3 {
    font-size: 1rem;
    margin-bottom: 10px;
  }
  
  .upload-area {
    width: 100%;
    aspect-ratio: 16/10;
    border: 2px dashed #ddd;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    overflow: hidden;
    position: relative;
    transition: border-color 0.2s;
  }
  
  .upload-area:hover {
    border-color: #7CB9E8;
  }
  
  .upload-area.has-file {
    border-style: solid;
    border-color: #4CAF50;
  }
  
  .upload-placeholder {
    text-align: center;
    color: #999;
  }
  
  .upload-placeholder i {
    font-size: 2rem;
    margin-bottom: 10px;
    color: #aaa;
  }
  
  .file-preview {
    width: 100%;
    height: 100%;
    position: relative;
  }
  
  .file-preview img {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
  
  .remove-file {
    position: absolute;
    top: 10px;
    right: 10px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.6);
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
  }
  
  .privacy-notice,
  .terms-agreement {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 20px;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 5px;
  }
  
  .privacy-notice input,
  .terms-agreement input {
    margin-top: 3px;
  }
  
  .privacy-notice label,
  .terms-agreement label {
    font-size: 0.9rem;
    color: #555;
  }
  
  .privacy-notice a,
  .terms-agreement a {
    color: #007bff;
    text-decoration: underline;
  }
  
  .form-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 30px;
  }
  
  .back-btn,
  .next-btn,
  .submit-btn,
  .home-btn,
  .dashboard-btn {
    padding: 10px 25px;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s;
  }
  
  .back-btn {
    background-color: #f5f5f5;
    color: #666;
  }
  
  .back-btn:hover {
    background-color: #e0e0e0;
  }
  
  .next-btn,
  .submit-btn,
  .dashboard-btn {
    background-color: #4CAF50;
    color: white;
  }
  
  .next-btn:hover,
  .submit-btn:hover,
  .dashboard-btn:hover {
    background-color: #388E3C;
  }
  
  .home-btn {
    background-color: #f5f5f5;
    color: #333;
  }
  
  .home-btn:hover {
    background-color: #e0e0e0;
  }
  
  .submit-btn:disabled {
    background-color: #a5d6a7;
    cursor: not-allowed;
  }
  
  .confirmation-summary {
    margin-bottom: 30px;
  }
  
  .confirmation-summary p {
    margin-bottom: 20px;
    color: #555;
  }
  
  .summary-section {
    background-color: #f9f9f9;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .summary-section h3 {
    font-size: 1.1rem;
    margin-bottom: 10px;
    color: #333;
  }
  
  .summary-item {
    display: flex;
    margin-bottom: 8px;
  }
  
  .summary-label {
    width: 120px;
    font-weight: 500;
    color: #555;
  }
  
  .summary-value {
    flex: 1;
    color: #333;
  }
  
  .success-form {
    text-align: center;
  }
  
  .success-message {
    padding: 30px 20px;
  }
  
  .success-message i {
    font-size: 4rem;
    color: #4CAF50;
    margin-bottom: 20px;
  }
  
  .success-message h2 {
    font-size: 1.8rem;
    margin-bottom: 15px;
    border: none;
    color: #333;
  }
  
  .success-message p {
    color: #555;
    margin-bottom: 10px;
  }
  
  .verification-status {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    margin: 20px 0;
    padding: 10px 20px;
    background-color: #f5f5f5;
    border-radius: 20px;
  }
  
  .status-label {
    font-weight: 500;
    color: #555;
  }
  
  .status-value {
    font-weight: 500;
  }
  
  .status-value.pending {
    color: #ff9800;
  }
  
  .next-steps {
    text-align: left;
    margin: 30px 0;
    background-color: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
  }
  
  .next-steps h3 {
    font-size: 1.2rem;
    margin-bottom: 15px;
    color: #333;
  }
  
  .next-steps ul {
    list-style-type: disc;
    padding-left: 20px;
  }
  
  .next-steps li {
    margin-bottom: 8px;
    color: #555;
  }
  
  @media (max-width: 768px) {
    .upload-section {
      flex-direction: column;
    }
    
    .form-actions {
      flex-direction: column;
      gap: 10px;
    }
    
    .back-btn, .next-btn, .submit-btn, .home-btn, .dashboard-btn {
      width: 100%;
    }
  }
  </style>