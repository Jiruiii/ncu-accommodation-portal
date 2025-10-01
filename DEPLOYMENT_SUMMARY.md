# NCU 中央大學租屋網站 - 完整部署總結

## 🎉 恭喜！你的網站已成功部署

**網站 URL:** https://rooms.student.ncu.edu.tw  
**部署日期:** 2025-10-01  
**狀態:** ✅ 生產環境運行中

詳細運維指南請參考: **OPERATION_GUIDE.md** ⭐

---

## ✅ 你關心的問題 - 快速解答

### Q1: 前端和後端會一直運行嗎？

**是的！已設定為開機自動啟動，24/7 運行**

- ✅ 後端服務: systemd 管理，自動啟動
- ✅ Nginx: systemd 管理，自動啟動  
- ✅ Proxmox 重啟後自動恢復

### Q2: 資料庫會因為重啟而清空嗎？

**不會！資料是安全的！**

SQLite 是檔案型資料庫，存儲在: `/var/www/ncu-accommodation-portal/backend/data.sqlite`

- ✅ 重啟後端 → 資料保留
- ✅ 重啟虛擬機 → 資料保留
- ✅ 關閉 Proxmox → 資料保留
- ⚠️ 只有刪除檔案或磁碟故障才會丟失

### Q3: 如何確保資料安全？

**建議設定自動備份！**

```bash
# 1. 測試備份
./backup-db.sh

# 2. 設定每天自動備份
crontab -e
# 添加: 0 2 * * * /var/www/ncu-accommodation-portal/backup-db.sh
```

詳見: **BACKUP_GUIDE.md**

---

## 🚀 快速開始

### 查看系統狀態

```bash
# 完整狀態儀表板 (推薦！)
./status-dashboard.sh

# 健康檢查
./check-health.sh
```

### 常用命令

```bash
# 重啟後端
sudo systemctl restart ncu-accommodation-backend.service

# 備份資料庫
./backup-db.sh

# 查看日誌
sudo journalctl -u ncu-accommodation-backend.service -f
```

---

## 📚 完整文檔

| 文檔 | 內容 | 重要性 |
|------|------|--------|
| **OPERATION_GUIDE.md** | 系統運作原理、常見問題 | ⭐⭐⭐ 必讀 |
| **BACKUP_GUIDE.md** | 備份與恢復指南 | ⭐⭐⭐ 必讀 |
| **QUICK_REFERENCE.txt** | 快速參考命令 | ⭐⭐ 推薦 |

---

## ✨ 系統現狀

```
✅ 前端: 已構建並部署
✅ 後端: 運行中，自動啟動 (conda ncu 環境，端口 5000)
✅ Nginx: 運行中，HTTPS 啟用 (端口 80, 443)
✅ 資料庫: SQLite (136 KB)，持久化存儲
✅ OAuth: 已正確配置
✅ 備份: 腳本已準備
```

**下一步: 閱讀 OPERATION_GUIDE.md，設定自動備份**

---

最後更新: 2025-10-01
