<template>
    <div class="sublet-page">
      <!-- 頂部橫幅 -->
      <div class="sublet-banner">
        <div class="overlay"></div>
        <div class="banner-content">
          <h1>轉租專區</h1>
          <p>安全、快速地找到短期租屋或釋出你的轉租資訊</p>
        </div>
      </div>
  
      <!-- 功能區塊 -->
      <div class="sublet-actions">
        <div class="search-filters">
          <div class="filter-input">
            <i class="search-icon"></i>
            <input 
              type="text" 
              placeholder="搜尋關鍵字..."
              v-model="searchTerm"
            >
          </div>
          
          <div class="filter-group">
            <div class="filter-item">
              <label>租期</label>
              <select v-model="filters.duration">
                <option value="">不限</option>
                <option value="1-3">1-3個月</option>
                <option value="3-6">3-6個月</option>
                <option value="6+">6個月以上</option>
              </select>
            </div>
            
            <div class="filter-item">
              <label>價格</label>
              <select v-model="filters.price">
                <option value="">不限</option>
                <option value="0-5000">5000元以下</option>
                <option value="5000-8000">5000-8000元</option>
                <option value="8000-10000">8000-10000元</option>
                <option value="10000+">10000元以上</option>
              </select>
            </div>
            
            <div class="filter-item">
              <label>入住時間</label>
              <select v-model="filters.moveInDate">
                <option value="">不限</option>
                <option value="immediate">立即可入住</option>
                <option value="within-month">1個月內</option>
                <option value="later">1個月後</option>
              </select>
            </div>
          </div>
        </div>
        
        <div class="post-sublet-btn" @click="togglePostForm">
          <i class="plus-icon"></i>
          發布轉租資訊
        </div>
      </div>
      
      <!-- 發布轉租表單 (模態框) -->
      <div class="modal" v-if="showPostForm">
        <div class="modal-backdrop" @click="togglePostForm"></div>
        <div class="modal-content">
          <div class="modal-header">
            <h2>發布轉租資訊</h2>
            <div class="close-btn" @click="togglePostForm">×</div>
          </div>
          
          <div class="modal-body">
            <form @submit.prevent="submitSublet">
              <div class="form-group">
                <label>標題*</label>
                <input 
                  type="text" 
                  v-model="newSublet.title" 
                  placeholder="例如：中大國際學生宿舍單人套房轉租"
                  required
                >
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>租金/月*</label>
                  <input 
                    type="number" 
                    v-model="newSublet.price" 
                    placeholder="NT$" 
                    required
                  >
                </div>
                
                <div class="form-group">
                  <label>剩餘租期*</label>
                  <select v-model="newSublet.duration" required>
                    <option value="" disabled>請選擇</option>
                    <option value="1-3">1-3個月</option>
                    <option value="3-6">3-6個月</option>
                    <option value="6+">6個月以上</option>
                  </select>
                </div>
              </div>
              
              <div class="form-group">
                <label>地址*</label>
                <input 
                  type="text" 
                  v-model="newSublet.address" 
                  placeholder="請提供詳細地址" 
                  required
                >
              </div>
              
              <div class="form-row">
                <div class="form-group">
                  <label>房型*</label>
                  <select v-model="newSublet.roomType" required>
                    <option value="" disabled>請選擇</option>
                    <option value="套房">套房</option>
                    <option value="雅房">雅房</option>
                    <option value="分租套房">分租套房</option>
                    <option value="整層住家">整層住家</option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label>可入住日期*</label>
                  <input type="date" v-model="newSublet.availableDate" required>
                </div>
              </div>
              
              <div class="form-group">
                <label>房源描述*</label>
                <textarea 
                  v-model="newSublet.description" 
                  placeholder="請描述房源特色、附近環境、轉租原因等..."
                  rows="4" 
                  required
                ></textarea>
              </div>
              
              <div class="form-group">
                <label>聯絡方式*</label>
                <input 
                  type="text" 
                  v-model="newSublet.contact" 
                  placeholder="LINE ID、電話或其他聯絡方式" 
                  required
                >
              </div>
              
              <div class="form-group">
                <label>上傳照片 (至少1張，最多5張)</label>
                <div class="upload-area">
                  <input
                    type="file"
                    ref="fileInput"
                    accept="image/*"
                    multiple
                    @change="handleFileUpload"
                    style="display: none"
                  >
                  <div class="upload-button" @click="triggerFileUpload">
                    <i class="upload-icon"></i> 選擇照片
                  </div>
                  <div class="upload-preview" v-if="uploadedFiles.length">
                    <div v-for="(file, index) in uploadedFiles" :key="index" class="preview-item">
                      <img :src="filePreview(file)" alt="Preview">
                      <div class="remove-file" @click="removeFile(index)">×</div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="form-checkbox">
                <input type="checkbox" id="verification" v-model="newSublet.verified" required>
                <label for="verification">我確認以上資訊屬實，並同意平台隱私政策與使用條款</label>
              </div>
              
              <div class="security-note">
                <i class="info-icon"></i>
                <p>安全提醒：發布內容需經過平台審核，避免填寫敏感個人資料。若有可疑使用者聯繫您，請向平台舉報。</p>
              </div>
              
              <div class="form-actions">
                <button type="button" class="cancel-btn" @click="togglePostForm">取消</button>
                <button type="submit" class="submit-btn">發布資訊</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      
      <!-- 轉租列表 -->
      <div class="sublet-container" v-if="filteredSublets.length">
        <div 
          v-for="sublet in filteredSublets" 
          :key="sublet.id"
          class="sublet-card"
          :class="{'verified-sublet': sublet.isVerified}"
          @click="viewSubletDetail(sublet)"
        >
          <div class="sublet-image">
            <img :src="sublet.image" :alt="sublet.title">
            <div class="sublet-price">NT$ {{ sublet.price }} / 月</div>
            <div v-if="sublet.isVerified" class="verified-tag">已驗證</div>
            <div v-if="isRecent(sublet.postedDate)" class="new-tag">NEW</div>
          </div>
          <div class="sublet-content">
            <h3>{{ sublet.title }}</h3>
            <div class="sublet-meta">
              <span><i class="calendar-icon"></i>可入住: {{ formatDate(sublet.availableDate) }}</span>
              <span><i class="duration-icon"></i>租期: {{ getDurationText(sublet.duration) }}</span>
              <span><i class="home-icon"></i>{{ sublet.roomType }}</span>
            </div>
            <p class="sublet-description">{{ truncateText(sublet.description, 100) }}</p>
            <div class="sublet-footer">
              <div class="user-info">
                <div class="user-avatar" :style="`background-image: url(${sublet.userAvatar})`"></div>
                <span>{{ sublet.userName }}</span>
              </div>
              <div class="post-date">{{ getTimeAgo(sublet.postedDate) }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 空狀態 -->
      <div class="empty-state" v-else>
        <div class="empty-icon"></div>
        <h3>目前沒有符合條件的轉租資訊</h3>
        <p>調整搜尋條件或是發布自己的轉租資訊</p>
        <button class="btn-primary" @click="togglePostForm">發布轉租資訊</button>
      </div>
      
      <!-- 轉租詳情模態框 -->
      <div class="modal" v-if="selectedSublet">
        <div class="modal-backdrop" @click="selectedSublet = null"></div>
        <div class="modal-content detail-modal">
          <div class="modal-header">
            <h2>轉租詳情</h2>
            <div class="close-btn" @click="selectedSublet = null">×</div>
          </div>
          
          <div class="modal-body">
            <div class="detail-gallery">
              <!-- 簡易輪播實現 -->
              <div class="gallery-main">
                <img :src="selectedSublet.images ? selectedSublet.images[currentImageIndex] : selectedSublet.image" alt="房源照片">
              </div>
              <div class="gallery-thumbs" v-if="selectedSublet.images && selectedSublet.images.length > 1">
                <div 
                  v-for="(img, idx) in selectedSublet.images" 
                  :key="idx" 
                  class="thumb-item"
                  :class="{ active: idx === currentImageIndex }"
                  @click="currentImageIndex = idx"
                >
                  <img :src="img" :alt="`縮圖 ${idx + 1}`">
                </div>
              </div>
            </div>
            
            <div class="detail-content">
              <div class="detail-header">
                <h1>{{ selectedSublet.title }}</h1>
                <div class="price-tag">NT$ {{ selectedSublet.price }} / 月</div>
              </div>
              
              <div class="detail-meta">
                <div class="meta-item"><i class="location-icon"></i>{{ selectedSublet.address }}</div>
                <div class="meta-item"><i class="room-icon"></i>{{ selectedSublet.roomType }}</div>
                <div class="meta-item"><i class="calendar-icon"></i>可入住日期: {{ formatDate(selectedSublet.availableDate) }}</div>
                <div class="meta-item"><i class="duration-icon"></i>租期: {{ getDurationText(selectedSublet.duration) }}</div>
              </div>
              
              <div class="detail-description">
                <h3>房源描述</h3>
                <p>{{ selectedSublet.description }}</p>
              </div>
              
              <div class="contact-section">
                <h3>聯絡資訊</h3>
                <div class="contact-card">
                  <div class="user-avatar" :style="`background-image: url(${selectedSublet.userAvatar})`"></div>
                  <div class="contact-info">
                    <h4>{{ selectedSublet.userName }}</h4>
                    <p v-if="selectedSublet.isVerified"><i class="verified-icon"></i>已通過學生身份驗證</p>
                    <div class="contact-methods">
                      <button class="contact-btn primary" @click="contactUser(selectedSublet)">
                        <i class="message-icon"></i>聯絡轉租者
                      </button>
                      <button class="contact-btn secondary" @click="reportListing(selectedSublet)">
                        <i class="report-icon"></i>檢舉
                      </button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="safety-tips">
                <h4><i class="shield-icon"></i>安全提醒</h4>
                <ul>
                  <li>盡量選擇可實地看房的房源</li>
                  <li>切勿進行包含「匯款、轉帳」的操作</li>
                  <li>簽約前詳細審閱合約內容</li>
                  <li>如有異常，請立即檢舉或聯繫平台協助</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed, onMounted } from 'vue';
//   import { useStore } from 'vuex';
  
  export default {
    name: 'SubletPage',
    setup() {
    //   const store = useStore();
      const searchTerm = ref('');
      const filters = ref({
        duration: '',
        price: '',
        moveInDate: ''
      });
      
      const showPostForm = ref(false);
      const selectedSublet = ref(null);
      const currentImageIndex = ref(0);
      const uploadedFiles = ref([]);
      
      // 表單資料
      const newSublet = ref({
        title: '',
        price: '',
        duration: '',
        address: '',
        roomType: '',
        availableDate: '',
        description: '',
        contact: '',
        verified: false
      });
      
      // 模擬資料
      const sublets = ref([
        {
          id: 1,
          title: '中大校門口學生公寓單人房急轉',
          price: 7000,
          duration: '3-6',
          address: '桃園市中壢區中大路300號附近',
          roomType: '套房',
          availableDate: '2025-05-15',
          description: '因實習需搬到台北，出租中大校門口步行5分鐘的單人房。家具齊全，包含書桌、衣櫃、冰箱、冷氣、洗衣機等。4-9月可入住，希望能找到愛惜房子的學弟妹！',
          image: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
          images: [
            'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
          ],
          userName: '林同學',
          userAvatar: 'https://randomuser.me/api/portraits/women/32.jpg',
          postedDate: new Date(2025, 4, 3),
          isVerified: true
        },
        {
          id: 2,
          title: '松苑學生宿舍兩人房轉租 (限女生)',
          price: 5500,
          duration: '1-3',
          address: '桃園市中壢區五權里1鄰中大路500號',
          roomType: '雅房',
          availableDate: '2025-05-10',
          description: '松苑學生宿舍女生房間轉租，離學校步行約10分鐘。環境安靜，室友友善。因暑假要出國交換，5月至8月可以轉租。租金含水電網路。',
          image: 'https://images.unsplash.com/photo-1493809842364-78817add7ffb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
          userName: '王同學',
          userAvatar: 'https://randomuser.me/api/portraits/women/44.jpg',
          postedDate: new Date(2025, 4, 4),
          isVerified: true
        },
        {
          id: 3,
          title: '中壢後火車站整層套房短租',
          price: 12000,
          duration: '1-3',
          address: '桃園市中壢區延平路228號',
          roomType: '整層住家',
          availableDate: '2025-05-20',
          description: '因工作調職到外縣市，需要轉租中壢後火車站附近的整層套房。交通便利，走路5分鐘到火車站，騎車15分鐘到中央大學。可短租3個月，租金面議。歡迎聯絡看房！',
          image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
          userName: '陳同學',
          userAvatar: 'https://randomuser.me/api/portraits/men/67.jpg',
          postedDate: new Date(2025, 4, 1),
          isVerified: false
        },
        {
          id: 4,
          title: '中央路三段雙人套房短期轉租',
          price: 8500,
          duration: '3-6',
          address: '桃園市中壢區中央路三段',
          roomType: '套房',
          availableDate: '2025-06-01',
          description: '因畢業搬家需要轉租，位於中央路三段的優質雙人套房，距離中央大學約10分鐘機車車程。房間寬敞明亮，附有獨立衛浴、冷氣、洗衣機、冰箱等。附近生活機能佳，有全家、7-11、各式餐廳。適合情侶或朋友合租，可短租半年。',
          image: 'https://images.unsplash.com/photo-1554995207-c18c203602cb?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
          userName: '張同學',
          userAvatar: 'https://randomuser.me/api/portraits/men/22.jpg',
          postedDate: new Date(2025, 3, 25),
          isVerified: true
        }
      ]);
      
      // 篩選後的轉租列表
      const filteredSublets = computed(() => {
        return sublets.value.filter(sublet => {
          // 關鍵字搜尋
          if (searchTerm.value && 
              !sublet.title.includes(searchTerm.value) && 
              !sublet.description.includes(searchTerm.value)) {
            return false;
          }
          
          // 租期篩選
          if (filters.value.duration && sublet.duration !== filters.value.duration) {
            return false;
          }
          
          // 價格篩選
          if (filters.value.price) {
            const [min, max] = filters.value.price.split('-').map(Number);
            if (max && (sublet.price < min || sublet.price > max)) {
              return false;
            } else if (!max && sublet.price < min) {
              return false;
            }
          }
          
          // 入住時間篩選
          if (filters.value.moveInDate) {
            const availableDate = new Date(sublet.availableDate);
            const today = new Date();
            
            if (filters.value.moveInDate === 'immediate' && 
                availableDate > new Date(today.setDate(today.getDate() + 7))) {
              return false;
            } else if (filters.value.moveInDate === 'within-month' && 
                      availableDate > new Date(today.setDate(today.getDate() + 30))) {
              return false;
            } else if (filters.value.moveInDate === 'later' && 
                      availableDate <= new Date(today.setDate(today.getDate() + 30))) {
              return false;
            }
          }
          
          return true;
        });
      });
      
      // 切換發布表單顯示
      const togglePostForm = () => {
        showPostForm.value = !showPostForm.value;
        
        // 如果關閉表單，重置表單資料
        if (!showPostForm.value) {
          newSublet.value = {
            title: '',
            price: '',
            duration: '',
            address: '',
            roomType: '',
            availableDate: '',
            description: '',
            contact: '',
            verified: false
          };
          uploadedFiles.value = [];
        }
      };
      
      // 提交轉租表單
      const submitSublet = () => {
        // 模擬表單提交
        const submittedSublet = {
          ...newSublet.value,
          id: sublets.value.length + 1,
          postedDate: new Date(),
          isVerified: false,
          userName: '我',
          userAvatar: 'https://randomuser.me/api/portraits/lego/1.jpg',
          image: uploadedFiles.value.length > 0 ? filePreview(uploadedFiles.value[0]) : 'https://via.placeholder.com/300x200?text=No+Image'
        };
        
        // 將新轉租資訊加入列表
        sublets.value.unshift(submittedSublet);
        
        // 關閉表單
        togglePostForm();
        
        // 顯示成功信息
        alert('轉租資訊已發布，審核通過後將會顯示在列表中');
      };
      
      // 查看轉租詳情
      const viewSubletDetail = (sublet) => {
        selectedSublet.value = sublet;
        currentImageIndex.value = 0;
      };
      
      // 聯絡轉租者
      const contactUser = (sublet) => {
        alert(`聯絡 ${sublet.userName}：請加 LINE ID: ${sublet.contact || 'NCU_sublet_demo'}`);
      };
      
      // 檢舉列表
      const reportListing = () => {
        const reason = prompt('請輸入檢舉原因：');
        if (reason) {
          alert('感謝您的檢舉，我們會盡速處理');
        }
      };
      
      // 觸發檔案上傳
      const triggerFileUpload = () => {
        document.querySelector('input[type="file"]').click();
      };
      
      // 處理檔案上傳
      const handleFileUpload = (event) => {
        const files = event.target.files;
        if (files.length + uploadedFiles.value.length > 5) {
          alert('最多只能上傳5張照片');
          return;
        }
        
        for (let i = 0; i < files.length; i++) {
          if (uploadedFiles.value.length < 5) {
            uploadedFiles.value.push(files[i]);
          }
        }
      };
      
      // 移除已上傳的檔案
      const removeFile = (index) => {
        uploadedFiles.value.splice(index, 1);
      };
      
      // 生成檔案預覽URL
      const filePreview = (file) => {
        return URL.createObjectURL(file);
      };
      
      // 格式化日期
      const formatDate = (dateString) => {
        if (!dateString) return '未設定';
        
        const date = new Date(dateString);
        return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
      };
      
      // 獲取相對時間
      const getTimeAgo = (date) => {
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return '今天';
        if (diffDays === 1) return '昨天';
        if (diffDays < 7) return `${diffDays}天前`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)}週前`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)}個月前`;
        return `${Math.floor(diffDays / 365)}年前`;
      };
      
      // 檢查是否為最近發布
      const isRecent = (date) => {
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        return diffDays <= 3;
      };
      
      // 獲取租期文字
      const getDurationText = (duration) => {
        if (!duration) return '未設定';
        
        switch (duration) {
          case '1-3':
            return '1-3個月';
          case '3-6':
            return '3-6個月';
          case '6+':
            return '6個月以上';
          default:
            return duration;
        }
      };
      
      // 截斷文字
      const truncateText = (text, length) => {
        if (!text) return '';
        return text.length > length ? text.substring(0, length) + '...' : text;
      };
      
      onMounted(() => {
        // 可以在此處獲取實際轉租資料
        // store.dispatch('fetchSubletListings');
      });
      
      return {
        searchTerm,
        filters,
        showPostForm,
        newSublet,
        sublets,
        filteredSublets,
        selectedSublet,
        currentImageIndex,
        uploadedFiles,
        togglePostForm,
        submitSublet,
        viewSubletDetail,
        contactUser,
        reportListing,
        triggerFileUpload,
        handleFileUpload,
        removeFile,
        filePreview,
        formatDate,
        getTimeAgo,
        isRecent,
        getDurationText,
        truncateText
      };
    }
  }
  </script>
  
  <style scoped>
  .sublet-page {
    width: 100%;
    min-height: 100vh;
    background-color: var(--light-gray);
    padding-bottom: 50px;
    overflow-y: auto;
    position: relative;
  }
  
  /* 頂部橫幅 */
  .sublet-banner {
    height: 250px;
    position: relative;
    background-image: url('https://images.unsplash.com/photo-1556912172-45b7abe8b7e1?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80');
    background-size: cover;
    background-position: center;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
  }
  
  .overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.6));
  }
  
  .banner-content {
    position: relative;
    z-index: 2;
    color: white;
  }
  
  .banner-content h1 {
    font-size: 2.5rem;
    margin-bottom: 15px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.3);
  }
  
  .banner-content p {
    font-size: 1.1rem;
    max-width: 600px;
    margin: 0 auto;
  }
  
  /* 功能區塊 */
  .sublet-actions {
    max-width: 1200px;
    margin: -50px auto 30px;
    padding: 20px;
    background-color: white;
    border-radius: 10px;
    box-shadow: var(--card-shadow);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 20px;
    position: relative;
    z-index: 10;
  }
  
  .search-filters {
    flex: 1;
    min-width: 300px;
  }
  
  .filter-input {
    position: relative;
    margin-bottom: 15px;
  }
  
  .search-icon {
    position: absolute;
    top: 50%;
    left: 15px;
    transform: translateY(-50%);
    width: 20px;
    height: 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23999"><path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/></svg>');
  }
  
  .filter-input input {
    width: 100%;
    padding: 12px 12px 12px 45px;
    border: 1px solid #e0e0e0;
    border-radius: 30px;
    font-size: 14px;
  }
  
  .filter-group {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .filter-item {
    flex: 1;
    min-width: 150px;
  }
  
  .filter-item label {
    display: block;
    font-size: 12px;
    color: #666;
    margin-bottom: 5px;
    padding-left: 5px;
  }
  
  .filter-item select {
    width: 100%;
    padding: 10px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    background-color: white;
    font-size: 14px;
    transition: all 0.3s ease;
    cursor: pointer;
  }

  .filter-item select:hover{
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    border-color: var(--primary-color);
    transform: translateY(-1px);
  }
  
  .post-sublet-btn {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 12px 25px;
    border-radius: 30px;
    font-weight: 600;
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(0,123,255,0.3);
    white-space: nowrap;
  }
  
  .post-sublet-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0,123,255,0.4);
  }
  
  .plus-icon {
    width: 16px;
    height: 16px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>');
  }
  
  /* 轉租列表 */
  .sublet-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 30px;
  }
  
  .sublet-card {
    background-color: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: var(--card-shadow);
    transition: all 0.3s ease;
    cursor: pointer;
  }
  
  .sublet-card:hover {
    transform: translateY(-10px);
    box-shadow: 0 15px 30px rgba(0,0,0,0.1);
  }
  
  .sublet-image {
    height: 200px;
    position: relative;
    overflow: hidden;
  }
  
  .sublet-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.5s ease;
  }
  
  .sublet-card:hover .sublet-image img {
    transform: scale(1.1);
  }
  
  .sublet-price {
    position: absolute;
    bottom: 15px;
    right: 15px;
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-weight: 600;
    font-size: 14px;
  }
  
  .verified-tag {
    position: absolute;
    top: 15px;
    left: 15px;
    background: rgba(46, 213, 115, 0.9);
    color: white;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
  
  .new-tag {
    position: absolute;
    top: 15px;
    right: 15px;
    background: var(--accent-color);
    color: white;
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }
  
  .sublet-content {
    padding: 20px;
  }
  
  .sublet-content h3 {
    margin-bottom: 10px;
    font-size: 18px;
    line-height: 1.4;
  }
  
  .sublet-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 15px;
    margin-bottom: 15px;
    font-size: 13px;
    color: #666;
  }
  
  .sublet-meta span {
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .sublet-description {
    margin-bottom: 20px;
    font-size: 14px;
    color: #666;
    line-height: 1.6;
  }
  
  .sublet-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
  }
  
  .user-info {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .user-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-size: cover;
    background-position: center;
  }
  
  .post-date {
    font-size: 12px;
    color: #999;
  }
  
  /* 空狀態樣式 */
  .empty-state {
    max-width: 500px;
    margin: 100px auto;
    text-align: center;
    padding: 40px;
    background-color: white;
    border-radius: 15px;
    box-shadow: var(--card-shadow);
  }
  
  .empty-icon {
    width: 80px;
    height: 80px;
    margin: 0 auto 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23e0e0e0"><path d="M19 5v14H5V5h14m1.1-2H3.9c-.5 0-.9.4-.9.9v16.2c0 .4.4.9.9.9h16.2c.4 0 .9-.5.9-.9V3.9c0-.5-.5-.9-.9-.9zM11 7h6v2h-6V7zm0 4h6v2h-6v-2zm0 4h6v2h-6v-2zM7 7h2v2H7V7zm0 4h2v2H7v-2zm0 4h2v2H7v-2z"/></svg>');
    background-repeat: no-repeat;
    background-position: center;
    background-size: contain;
  }
  
  .empty-state h3 {
    font-size: 20px;
    margin-bottom: 10px;
    color: #555;
  }
  
  .empty-state p {
    color: #888;
    margin-bottom: 25px;
  }
  
  /* 模態框樣式 */
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    overflow-y: auto;
  }
  
  .modal-backdrop {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    backdrop-filter: blur(3px);
  }
  
  .modal-content {
    position: relative;
    width: 95%;
    max-width: 800px;
    max-height: 90vh;
    background-color: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
    overflow-y: auto;
  }
  
  .detail-modal {
    max-width: 900px;
  }
  
  .modal-header {
    padding: 20px;
    border-bottom: 1px solid #f0f0f0;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 10;
  }
  
  .modal-header h2 {
    font-size: 20px;
  }
  
  .close-btn {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .close-btn:hover {
    background-color: #e0e0e0;
  }
  
  .modal-body {
    padding: 20px;
    overflow-y: auto;
  }
  
  /* 表單樣式 */
  form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  .form-group label {
    font-size: 14px;
    font-weight: 600;
  }
  
  .form-group input,
  .form-group select,
  .form-group textarea {
    padding: 12px;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    font-size: 14px;
  }
  
  .form-group textarea {
    resize: vertical;
    min-height: 100px;
  }
  
  .form-checkbox {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .form-checkbox input {
    width: 18px;
    height: 18px;
  }
  
  .security-note {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }
  
  .info-icon {
    width: 20px;
    height: 20px;
    min-width: 20px;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%23007bff"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z"/></svg>');
  }
  
  .security-note p {
    font-size: 13px;
    color: #666;
    line-height: 1.5;
  }
  
  .form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 10px;
  }
  
  .cancel-btn,
  .submit-btn {
    padding: 12px 25px;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    font-size: 14px;
  }
  
  .cancel-btn {
    background-color: #f0f0f0;
    color: #333;
  }
  
  .submit-btn {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    box-shadow: 0 4px 15px rgba(0,123,255,0.2);
  }
  
  /* 圖片上傳區域 */
  .upload-area {
    border: 2px dashed #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
  }
  
  .upload-button {
    padding: 12px 25px;
    background-color: #f8f9fa;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .upload-button:hover {
    background-color: #f0f0f0;
  }
  
  .upload-preview {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 15px;
  }
  
  .preview-item {
    position: relative;
    width: 80px;
    height: 80px;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .preview-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .remove-file {
    position: absolute;
    top: 3px;
    right: 3px;
    width: 20px;
    height: 20px;
    background-color: rgba(0,0,0,0.5);
    border-radius: 50%;
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    cursor: pointer;
  }
  
  /* 詳情頁樣式 */
  .detail-gallery {
    margin-bottom: 30px;
  }
  
  .gallery-main {
    height: 400px;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 15px;
  }
  
  .gallery-main img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .gallery-thumbs {
    display: flex;
    gap: 10px;
    overflow-x: auto;
    padding-bottom: 10px;
  }
  
  .thumb-item {
    width: 80px;
    height: 60px;
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    opacity: 0.7;
    transition: all 0.3s ease;
  }
  
  .thumb-item.active {
    opacity: 1;
    box-shadow: 0 0 0 2px var(--primary-color);
  }
  
  .thumb-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .detail-content {
    padding: 0 10px;
  }
  
  .detail-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 20px;
    gap: 20px;
  }
  
  .detail-header h1 {
    font-size: 24px;
    line-height: 1.4;
    flex: 1;
  }
  
  .price-tag {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    white-space: nowrap;
  }
  
  .detail-meta {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 30px;
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 10px;
  }
  
  .meta-item {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
  }
  
  .detail-description {
    margin-bottom: 30px;
  }
  
  .detail-description h3 {
    margin-bottom: 15px;
    font-size: 18px;
    color: var(--primary-color);
  }
  
  .detail-description p {
    line-height: 1.7;
    color: #444;
  }
  
  .contact-section {
    margin-bottom: 30px;
  }
  
  .contact-section h3 {
    margin-bottom: 15px;
    font-size: 18px;
    color: var(--primary-color);
  }
  
  .contact-card {
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 10px;
    display: flex;
    gap: 20px;
  }
  
  .contact-info {
    flex: 1;
  }
  
  .contact-info h4 {
    margin-bottom: 5px;
    font-size: 16px;
  }
  
  .contact-info p {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 13px;
    color: #28a745;
    margin-bottom: 15px;
  }
  
  .contact-methods {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .contact-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    cursor: pointer;
    font-size: 14px;
  }
  
  .contact-btn.primary {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
  }
  
  .contact-btn.secondary {
    background-color: white;
    color: #666;
    border: 1px solid #e0e0e0;
  }
  
  .safety-tips {
    padding: 20px;
    background-color: #fff8e1;
    border-radius: 10px;
    margin-top: 30px;
  }
  
  .safety-tips h4 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 15px;
    color: #ff9800;
  }
  
  .safety-tips ul {
    padding-left: 30px;
  }
  
  .safety-tips li {
    margin-bottom: 10px;
    font-size: 13px;
    color: #666;
  }
  
  @media (max-width: 768px) {
    .sublet-banner {
      height: 200px;
    }
    
    .banner-content h1 {
      font-size: 2rem;
    }
    
    .form-row {
      grid-template-columns: 1fr;
    }
    
    .detail-header {
      flex-direction: column;
    }
    
    .price-tag {
      align-self: flex-start;
    }
    
    .gallery-main {
      height: 300px;
    }
  }
  </style>