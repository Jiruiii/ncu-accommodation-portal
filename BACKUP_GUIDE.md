╔═══════════════════════════════════════════════════════════════════════╗
║            設定自動備份 - 快速指南                                    ║
╚═══════════════════════════════════════════════════════════════════════╝

## 📦 已為你準備好備份腳本

備份腳本位置: /var/www/ncu-accommodation-portal/backup-db.sh

功能:
  ✅ 自動備份資料庫
  ✅ 壓縮備份檔案 (節省空間)
  ✅ 檢查資料庫完整性
  ✅ 自動清理 30 天前的舊備份
  ✅ 記錄備份日誌

═══════════════════════════════════════════════════════════════════════

## 🚀 方式一：手動備份 (最簡單)

當你想要備份時，直接執行：

```bash
cd /var/www/ncu-accommodation-portal
./backup-db.sh
```

備份檔案會儲存在: /var/www/ncu-accommodation-portal/backups/

═══════════════════════════════════════════════════════════════════════

## ⏰ 方式二：自動定期備份 (推薦)

### 步驟 1: 編輯 crontab

```bash
crontab -e
```

### 步驟 2: 添加以下任一行 (選擇一個)

```bash
# 選項 A: 每天凌晨 2 點自動備份 (推薦)
0 2 * * * /var/www/ncu-accommodation-portal/backup-db.sh >> /var/log/ncu-backup.log 2>&1

# 選項 B: 每天中午 12 點自動備份
0 12 * * * /var/www/ncu-accommodation-portal/backup-db.sh >> /var/log/ncu-backup.log 2>&1

# 選項 C: 每 6 小時備份一次
0 */6 * * * /var/www/ncu-accommodation-portal/backup-db.sh >> /var/log/ncu-backup.log 2>&1

# 選項 D: 每週日凌晨 3 點備份
0 3 * * 0 /var/www/ncu-accommodation-portal/backup-db.sh >> /var/log/ncu-backup.log 2>&1
```

### 步驟 3: 儲存並退出

- 在 nano 編輯器中: 按 `Ctrl+X`，然後 `Y`，再按 `Enter`
- 在 vim 編輯器中: 按 `ESC`，輸入 `:wq`，按 `Enter`

### 步驟 4: 驗證 cron 任務已設定

```bash
crontab -l
```

應該會看到你剛剛添加的那一行。

═══════════════════════════════════════════════════════════════════════

## 📅 Cron 時間格式說明

```
* * * * * 指令
│ │ │ │ │
│ │ │ │ └─── 星期 (0-7, 0和7都代表星期日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小時 (0-23)
└─────────── 分鐘 (0-59)
```

### 常用範例：

```bash
0 2 * * *       # 每天凌晨 2:00
0 */6 * * *     # 每 6 小時 (0:00, 6:00, 12:00, 18:00)
0 0 * * 0       # 每週日午夜 12:00
0 3 1 * *       # 每月 1 號凌晨 3:00
*/30 * * * *    # 每 30 分鐘
```

═══════════════════════════════════════════════════════════════════════

## 🔍 查看備份結果

### 查看所有備份：

```bash
ls -lh /var/www/ncu-accommodation-portal/backups/
```

### 查看備份日誌：

```bash
cat /var/www/ncu-accommodation-portal/backups/backup.log
```

### 查看最近的備份：

```bash
ls -lht /var/www/ncu-accommodation-portal/backups/ | head -n 10
```

### 查看備份總大小：

```bash
du -sh /var/www/ncu-accommodation-portal/backups/
```

═══════════════════════════════════════════════════════════════════════

## 🔄 恢復資料庫 (萬一需要)

### 步驟 1: 停止後端服務

```bash
sudo systemctl stop ncu-accommodation-backend.service
```

### 步驟 2: 備份當前資料庫 (安全起見)

```bash
cp /var/www/ncu-accommodation-portal/backend/data.sqlite \
   /var/www/ncu-accommodation-portal/backend/data.sqlite.current
```

### 步驟 3: 解壓縮並恢復備份

```bash
# 列出所有備份，選擇要恢復的
ls -lh /var/www/ncu-accommodation-portal/backups/

# 恢復特定備份 (替換日期為實際備份檔案名)
gunzip -c /var/www/ncu-accommodation-portal/backups/data.sqlite.20251001_141232.gz \
  > /var/www/ncu-accommodation-portal/backend/data.sqlite
```

### 步驟 4: 重啟後端服務

```bash
sudo systemctl start ncu-accommodation-backend.service
```

### 步驟 5: 驗證

```bash
# 檢查服務狀態
sudo systemctl status ncu-accommodation-backend.service

# 檢查資料庫完整性
sqlite3 /var/www/ncu-accommodation-portal/backend/data.sqlite "PRAGMA integrity_check;"
```

═══════════════════════════════════════════════════════════════════════

## 💡 備份最佳實踐

### ✅ 建議做法：

1. **多重備份**
   - 本地備份 (已設定)
   - 定期複製到外部儲存
   - 考慮使用雲端備份

2. **定期測試恢復**
   - 每季度測試一次恢復流程
   - 確保備份可以真的用來恢復

3. **監控備份**
   - 定期檢查備份是否成功執行
   - 查看備份日誌

4. **保留策略**
   - 每日備份: 保留 30 天
   - 每週備份: 保留 3 個月
   - 每月備份: 保留 1 年

### 📦 進階: 複製到外部儲存

```bash
# 複製到外部硬碟 (假設掛載在 /mnt/external)
rsync -av /var/www/ncu-accommodation-portal/backups/ /mnt/external/ncu-backups/

# 複製到遠端伺服器 (使用 scp)
scp /var/www/ncu-accommodation-portal/backups/*.gz user@remote-server:/backup/ncu/

# 複製到另一個 Proxmox 主機
rsync -av -e ssh /var/www/ncu-accommodation-portal/backups/ user@proxmox-backup:/backups/ncu/
```

═══════════════════════════════════════════════════════════════════════

## ✅ 完成檢查清單

□ 備份腳本已測試運行
□ Cron 任務已設定 (如果選擇自動備份)
□ 已驗證 crontab 設定: `crontab -l`
□ 知道如何查看備份: `ls -lh /var/www/ncu-accommodation-portal/backups/`
□ 知道如何恢復資料庫
□ 已閱讀 OPERATION_GUIDE.md

═══════════════════════════════════════════════════════════════════════

最後更新: 2025-10-01
