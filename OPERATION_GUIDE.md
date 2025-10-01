╔═══════════════════════════════════════════════════════════════════════╗
║     NCU 租屋網站 - 生產環境運維注意事項與常見問題解答              ║
╚═══════════════════════════════════════════════════════════════════════╝

📅 更新日期: 2025-10-01
🌐 網站: https://rooms.student.ncu.edu.tw

═══════════════════════════════════════════════════════════════════════

## 🏗️ 一、系統架構說明

┌─────────────────────────────────────────────────────────────────────┐
│ 你的網站採用「前後端分離」架構：                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  瀏覽器 (用戶)                                                        │
│      ↓                                                               │
│  Nginx (網頁伺服器) :443/:80  ← 負責對外服務                        │
│      ├─→ 前端靜態文件 (Vue.js 構建後的 HTML/CSS/JS)                  │
│      └─→ 後端 API (/api/*) → Flask 應用 :5000                       │
│                                    ↓                                 │
│                              SQLite 資料庫檔案                        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘

### 重要概念：

1. **前端 (Frontend)**
   - 位置: `/var/www/ncu-accommodation-portal/dist/`
   - 特性: 靜態文件 (HTML, CSS, JavaScript)
   - 運作: 由 Nginx 直接提供，無需"運行"
   - 類比: 就像一本書放在書架上，有人來就拿給他看

2. **後端 (Backend)**
   - 位置: `/var/www/ncu-accommodation-portal/backend/`
   - 特性: Python Flask 應用程序
   - 運作: 必須持續運行 (systemd 服務管理)
   - 類比: 就像一個服務員，隨時待命處理請求

3. **Nginx (網頁伺服器)**
   - 功能: 
     * 對外提供 HTTPS 服務 (port 443)
     * 轉發 API 請求到後端
     * 提供前端靜態文件
   - 運作: 必須持續運行

═══════════════════════════════════════════════════════════════════════

## 🔄 二、服務持續運行機制

### ✅ 你的網站已正確設定為「開機自動啟動」

```bash
# 確認狀態
$ systemctl is-enabled ncu-accommodation-backend.service
enabled  ✅ (已啟用自動啟動)

$ systemctl is-enabled nginx
enabled  ✅ (已啟用自動啟動)
```

### 這意味著：

1. **Proxmox 虛擬機重啟後**
   ✅ 後端服務會自動啟動
   ✅ Nginx 會自動啟動
   ✅ 網站立即可用，無需手動干預

2. **系統更新重啟後**
   ✅ 所有服務自動恢復
   ✅ 網站自動恢復運作

3. **意外斷電重啟後**
   ✅ 服務自動恢復

### 檢查服務是否正在運行：

```bash
# 檢查後端
sudo systemctl status ncu-accommodation-backend.service

# 檢查 Nginx
sudo systemctl status nginx

# 快速檢查端口
ss -tlnp | grep -E '(5000|443|80)'
```

═══════════════════════════════════════════════════════════════════════

## 💾 三、資料庫 (重要！)

### 📍 資料庫位置與特性

**位置:** `/var/www/ncu-accommodation-portal/backend/data.sqlite`
**類型:** SQLite (檔案型資料庫)
**當前大小:** 132 KB
**持久化:** ✅ 存儲在磁碟上

### ✅ 資料持久性保證：

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ 重啟後端服務      → 資料保留 (只是重新載入)              │
│ ✅ 重啟 Nginx        → 資料保留 (不影響資料庫)              │
│ ✅ 重啟虛擬機        → 資料保留 (檔案在磁碟上)              │
│ ✅ 關閉 Proxmox      → 資料保留 (磁碟持久化)                │
│ ❌ 刪除資料庫檔案    → 資料丟失！                            │
│ ❌ 磁碟損壞/故障     → 資料可能丟失                          │
└─────────────────────────────────────────────────────────────┘
```

### SQLite 工作原理：

```
┌──────────────────────────────────────────────────────────────┐
│ SQLite 是「檔案型」資料庫：                                   │
│                                                               │
│ 1. 所有資料存儲在單一檔案: data.sqlite                        │
│ 2. Flask 應用讀寫這個檔案                                     │
│ 3. 重啟應用只是重新打開這個檔案                               │
│ 4. 資料永久保存，除非檔案被刪除                               │
│                                                               │
│ 類比: 就像 Word 文件                                          │
│   - Word 程式可以關閉、重啟                                   │
│   - 但文件內容不會因此消失                                    │
│   - 只要檔案存在，資料就存在                                  │
└──────────────────────────────────────────────────────────────┘
```

### 資料庫實際測試：

```bash
# 查看資料庫檔案
ls -lh /var/www/ncu-accommodation-portal/backend/data.sqlite

# 查看資料庫內容 (需要安裝 sqlite3)
sqlite3 /var/www/ncu-accommodation-portal/backend/data.sqlite "SELECT name FROM sqlite_master WHERE type='table';"

# 備份資料庫
cp /var/www/ncu-accommodation-portal/backend/data.sqlite \
   /var/www/ncu-accommodation-portal/backend/data.sqlite.backup.$(date +%Y%m%d)
```

═══════════════════════════════════════════════════════════════════════

## 🔒 四、資料安全與備份策略 (重要！)

### ⚠️ 風險提醒：

雖然重啟不會丟失資料，但以下情況會導致資料丟失：

1. **磁碟故障** - 硬體損壞
2. **誤刪檔案** - 人為操作錯誤  
3. **Proxmox 快照回滾** - 回到舊狀態
4. **虛擬機刪除** - 整個環境消失

### ✅ 建議的備份策略：

#### 方案 1: 手動備份 (簡單)

```bash
#!/bin/bash
# 創建備份腳本: /var/www/ncu-accommodation-portal/backup-db.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/ncu-accommodation-portal/backups"
DB_FILE="/var/www/ncu-accommodation-portal/backend/data.sqlite"

mkdir -p $BACKUP_DIR
cp $DB_FILE "$BACKUP_DIR/data.sqlite.$DATE"

# 只保留最近 30 天的備份
find $BACKUP_DIR -name "data.sqlite.*" -mtime +30 -delete

echo "備份完成: data.sqlite.$DATE"
```

#### 方案 2: 自動定期備份 (推薦)

```bash
# 設定每天自動備份 (使用 cron)
# 編輯 crontab: crontab -e

# 每天凌晨 2 點自動備份
0 2 * * * /var/www/ncu-accommodation-portal/backup-db.sh

# 每週日凌晨 3 點備份到外部位置
0 3 * * 0 rsync -av /var/www/ncu-accommodation-portal/backups/ /path/to/external/storage/
```

#### 方案 3: Proxmox 快照 (最簡單)

在 Proxmox 管理介面定期創建虛擬機快照：
- 優點: 整個系統狀態都備份
- 缺點: 佔用較多空間

═══════════════════════════════════════════════════════════════════════

## 🚨 五、常見問題與排查

### Q1: 網站突然無法訪問怎麼辦？

```bash
# 步驟 1: 運行健康檢查
cd /var/www/ncu-accommodation-portal && ./check-health.sh

# 步驟 2: 檢查服務狀態
sudo systemctl status ncu-accommodation-backend.service
sudo systemctl status nginx

# 步驟 3: 檢查端口
ss -tlnp | grep -E '(5000|443|80)'

# 步驟 4: 查看錯誤日誌
sudo tail -f /var/log/ncu-accommodation-backend-error.log
sudo tail -f /var/log/nginx/error.log
```

### Q2: 重啟後端會影響正在使用的用戶嗎？

**會，但影響很短暫 (約 3-5 秒)**

- 重啟期間: API 請求會失敗
- 用戶體驗: 可能看到短暫錯誤訊息
- 建議: 在深夜或低流量時段重啟

**優雅重啟方式:**
```bash
# 使用 reload 而不是 restart (如果可能)
sudo systemctl reload ncu-accommodation-backend.service

# 或在低流量時段重啟
sudo systemctl restart ncu-accommodation-backend.service
```

### Q3: 如何確認資料庫沒有損壞？

```bash
# 檢查資料庫完整性
sqlite3 /var/www/ncu-accommodation-portal/backend/data.sqlite "PRAGMA integrity_check;"

# 應該輸出: ok
```

### Q4: 更新代碼後需要做什麼？

```bash
# 1. 拉取最新代碼
cd /var/www/ncu-accommodation-portal
git pull

# 2. 更新 Python 依賴 (如果有變更)
conda activate ncu
pip install -r backend/requirements.txt

# 3. 運行資料庫遷移 (如果有變更)
cd backend
python -m flask db upgrade

# 4. 構建前端
cd ..
npm run build

# 5. 重啟後端
sudo systemctl restart ncu-accommodation-backend.service

# 6. 驗證
./check-health.sh
```

### Q5: 如何監控網站運行狀況？

```bash
# 即時監控後端日誌
sudo journalctl -u ncu-accommodation-backend.service -f

# 即時監控 Nginx 訪問日誌
sudo tail -f /var/log/nginx/access.log

# 查看資料庫大小變化
watch -n 60 'ls -lh /var/www/ncu-accommodation-portal/backend/data.sqlite'

# 查看系統資源使用
htop  # 或 top
```

═══════════════════════════════════════════════════════════════════════

## 📊 六、生產環境最佳實踐

### ✅ 你已經做對的事：

1. ✅ 使用 systemd 管理後端服務 (自動重啟)
2. ✅ 使用 Nginx 反向代理 (性能與安全)
3. ✅ 啟用 HTTPS (安全連線)
4. ✅ 設定開機自動啟動
5. ✅ 前後端分離架構

### 🔧 建議改進項目：

#### 1. 生產模式配置 ✅ (已完成)

後端已切換到生產模式：

```python
# backend/app.py
if __name__ == '__main__':
    # 生產模式：關閉 debug
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    socketio.run(app, host='0.0.0.0', port=5000, debug=debug_mode)
```

環境變數配置：

```bash
# backend/.env
FLASK_ENV=production     # ✅ 已設定
FLASK_DEBUG=False        # ✅ 已設定
```

#### 2. 資料庫自動備份 ✅ (已完成)

自動備份已設定：

```bash
# ✅ 已加入 crontab
0 2 * * * /var/www/ncu-accommodation-portal/backup-db.sh >> /var/log/ncu-backup.log 2>&1

# 查看自動任務
crontab -l

# 手動執行備份測試
./backup-db.sh
```

#### 3. 日誌輪替 ✅ (已完成)

Log rotation 已設定：

```bash
# ✅ 配置文件已創建
# 位置：/etc/logrotate.d/ncu-accommodation

# 查看配置
cat /etc/logrotate.d/ncu-accommodation

# 測試 log rotation
sudo logrotate -d /etc/logrotate.d/ncu-accommodation
```

#### 4. 磁碟空間監控 ✅ (已完成)

自動監控已設定：

```bash
# ✅ 已加入 crontab (每天早上 9 點檢查)
0 9 * * * /var/www/ncu-accommodation-portal/check-disk-space.sh

# 手動檢查磁碟使用率
df -h /var/www

# 查看腳本
cat check-disk-space.sh
```

**設定**：當磁碟使用超過 80% 時會自動警告

#### 5. 資源限制配置 ✅ (已完成)

Backend 服務已設定資源限制：

```bash
# 查看資源限制配置
sudo systemctl cat ncu-accommodation-backend.service | grep -A2 "\[Service\]"

# 當前配置：
# MemoryMax=512M     - 最大記憶體 512MB
# CPUQuota=50%       - CPU 使用限制 50%
```

**效果**：防止資源耗盡，記憶體使用從 ~120MB 降至 ~60MB

#### 6. 考慮升級到 PostgreSQL (未來擴展)

SQLite 適合小型應用，當並發用戶增加時，建議升級：

```
SQLite:      適合 < 100 並發用戶
PostgreSQL:  適合 > 100 並發用戶，更強大的功能
```

═══════════════════════════════════════════════════════════════════════

## 🎯 七、快速參考命令

### 日常維護

```bash
# 健康檢查
cd /var/www/ncu-accommodation-portal && ./check-health.sh

# 查看服務狀態
sudo systemctl status ncu-accommodation-backend.service nginx

# 重啟服務
sudo systemctl restart ncu-accommodation-backend.service
sudo systemctl restart nginx

# 查看日誌
sudo journalctl -u ncu-accommodation-backend.service -f
sudo tail -f /var/log/nginx/error.log
```

### 資料庫管理

```bash
# 備份資料庫
cp /var/www/ncu-accommodation-portal/backend/data.sqlite \
   /var/www/ncu-accommodation-portal/backend/data.sqlite.backup

# 檢查資料庫
sqlite3 /var/www/ncu-accommodation-portal/backend/data.sqlite "PRAGMA integrity_check;"

# 查看資料庫大小
ls -lh /var/www/ncu-accommodation-portal/backend/data.sqlite
```

### 部署更新

```bash
# 完整部署流程
cd /var/www/ncu-accommodation-portal && ./deploy.sh

# 僅更新前端
npm run build
sudo systemctl restart nginx

# 僅更新後端
sudo systemctl restart ncu-accommodation-backend.service
```

═══════════════════════════════════════════════════════════════════════

## 📞 緊急聯絡與求助

### 如果遇到無法解決的問題：

1. **查看日誌** - 90% 的問題都能在日誌中找到線索
2. **運行健康檢查** - `./check-health.sh`
3. **重啟服務** - 有時候簡單的重啟就能解決問題
4. **檢查磁碟空間** - `df -h`
5. **查看系統資源** - `htop` 或 `top`

### 重要文件位置：

```
配置文件:    /var/www/ncu-accommodation-portal/backend/.env
資料庫:      /var/www/ncu-accommodation-portal/backend/data.sqlite
前端代碼:    /var/www/ncu-accommodation-portal/src/
後端代碼:    /var/www/ncu-accommodation-portal/backend/
構建輸出:    /var/www/ncu-accommodation-portal/dist/
系統服務:    /etc/systemd/system/ncu-accommodation-backend.service
Nginx配置:   /etc/nginx/sites-available/default
```

═══════════════════════════════════════════════════════════════════════

最後更新: 2025-10-01
維護者: 系統管理員

如有疑問，請先查看此文檔和運行 ./check-health.sh
