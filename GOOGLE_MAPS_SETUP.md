# 🗺️ Google Maps API 設定指南

## 問題說明

地圖上顯示 **"For development purposes only"** 浮水印，表示 Google Maps API Key 有問題：

1. ❌ API Key 沒有綁定帳單帳戶
2. ❌ API Key 配額已用完
3. ❌ API Key 限制設定不正確
4. ❌ API Key 已過期或被停用

---

## ✅ 解決方案：取得新的 Google Maps API Key

### 步驟 1：前往 Google Cloud Console

訪問：https://console.cloud.google.com/

### 步驟 2：建立或選擇專案

1. 如果沒有專案，點擊 **「建立專案」**
2. 輸入專案名稱（例如：`NCU-Accommodation-Portal`）
3. 點擊 **「建立」**

### 步驟 3：啟用 Maps JavaScript API

1. 在左側選單選擇 **「API 和服務」** > **「程式庫」**
2. 搜尋 **「Maps JavaScript API」**
3. 點擊進入後，按 **「啟用」**

### 步驟 4：建立 API 金鑰

1. 在左側選單選擇 **「API 和服務」** > **「憑證」**
2. 點擊 **「+ 建立憑證」** > **「API 金鑰」**
3. 系統會自動產生 API 金鑰，複製它

### 步驟 5：限制 API 金鑰（重要！）

為了安全性，建議限制 API 金鑰：

1. 在憑證頁面找到剛建立的 API 金鑰，點擊編輯圖示
2. **應用程式限制**：
   - 選擇 **「HTTP 參照網址 (網站)」**
3. **網站限制**：
   - 加入：`rooms.student.ncu.edu.tw/*`
   - 加入：`https://rooms.student.ncu.edu.tw/*`
   - （如果需要本地測試）加入：`localhost/*`
4. **API 限制**：
   - 選擇 **「限制金鑰」**
   - 勾選 **「Maps JavaScript API」**
5. 點擊 **「儲存」**

### 步驟 6：設定帳單帳戶（移除浮水印）

⚠️ **這是移除 "For development purposes only" 的關鍵步驟！**

1. 在 Google Cloud Console 選單中選擇 **「帳單」**
2. 如果沒有帳單帳戶：
   - 點擊 **「建立帳單帳戶」**
   - 輸入付款資訊（需要信用卡）
   - Google 提供 **$300 免費額度**（90 天）
3. 將帳單帳戶連結到你的專案

### 步驟 7：更新環境變數

將新的 API Key 更新到以下檔案：

#### 前端環境變數

編輯 `.env`：
```bash
VUE_APP_GOOGLE_MAPS_API_KEY=你的新API金鑰
```

編輯 `.env.production`：
```bash
VUE_APP_GOOGLE_MAPS_API_KEY=你的新API金鑰
```

#### 後端環境變數（可選）

編輯 `backend/.env`：
```bash
GOOGLE_MAPS_API_KEY=你的新API金鑰
```

### 步驟 8：重新建構並部署

```bash
# 進入專案目錄
cd /var/www/ncu-accommodation-portal

# 重新建構前端
npm run build

# 重新啟動後端（如果有需要）
sudo systemctl restart ncu-accommodation-backend
```

### 步驟 9：清除瀏覽器快取並測試

1. 按 `Ctrl + Shift + R` 強制重新整理
2. 或開啟無痕視窗（`Ctrl + Shift + N`）
3. 前往地圖搜尋頁面測試

---

## 📊 Google Maps API 配額

**免費配額（每月）：**
- Maps JavaScript API：28,000 次地圖載入
- 超過後：每 1,000 次 $7 USD

**省錢技巧：**
1. 使用快取減少 API 呼叫
2. 只在需要時載入地圖
3. 設定 API 限制避免濫用

---

## 🔍 疑難排解

### 問題：API Key 更新後仍顯示浮水印

**解決方案：**
1. 確認已綁定帳單帳戶
2. 等待 5-10 分鐘讓設定生效
3. 清除瀏覽器快取（`Ctrl + Shift + Delete`）
4. 檢查 API 限制是否正確設定

### 問題：地圖無法載入

**解決方案：**
1. 檢查瀏覽器 Console 是否有錯誤訊息
2. 確認 Maps JavaScript API 已啟用
3. 檢查網域限制是否包含你的網站
4. 確認 API Key 沒有輸入錯誤

### 問題：顯示 "This page can't load Google Maps correctly"

**解決方案：**
1. API Key 可能未正確設定
2. Maps JavaScript API 未啟用
3. 帳單帳戶未連結或已過期

---

## 📝 當前 API Key 位置

**舊的寫死位置（已修正）：**
- ~~`src/views/MapSearch.vue` 第 176 行~~

**新的環境變數位置：**
- `.env` - 開發環境
- `.env.production` - 生產環境
- `backend/.env` - 後端環境

---

## 🔒 安全提醒

1. ✅ **永遠不要**將 API Key 提交到 Git
2. ✅ **務必設定** API 限制和網域限制
3. ✅ **定期檢查**使用量避免超額
4. ✅ **使用** `.gitignore` 排除 `.env` 檔案

---

## 📞 需要協助？

- Google Maps Platform 文件：https://developers.google.com/maps/documentation
- Google Cloud Console：https://console.cloud.google.com/
- 計費說明：https://cloud.google.com/maps-platform/pricing

---

**更新日期**：2025-10-02  
**狀態**：⚠️ 需要更新 Google Maps API Key
