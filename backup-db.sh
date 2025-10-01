#!/bin/bash

#############################################################################
# NCU 租屋網站 - 資料庫自動備份腳本
# 
# 功能: 
#   1. 自動備份 SQLite 資料庫
#   2. 保留最近 30 天的備份
#   3. 壓縮舊備份以節省空間
#   4. 記錄備份日誌
#
# 使用方式:
#   手動執行: ./backup-db.sh
#   自動執行: 添加到 crontab
#     crontab -e
#     0 2 * * * /var/www/ncu-accommodation-portal/backup-db.sh
#
#############################################################################

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
PROJECT_DIR="/var/www/ncu-accommodation-portal"
DB_FILE="$PROJECT_DIR/backend/data.sqlite"
BACKUP_DIR="$PROJECT_DIR/backups"
LOG_FILE="$PROJECT_DIR/backups/backup.log"
DATE=$(date +%Y%m%d_%H%M%S)
KEEP_DAYS=30

# 創建備份目錄
mkdir -p "$BACKUP_DIR"

# 記錄日誌
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

echo "========================================="
echo "NCU 租屋網站 - 資料庫備份"
echo "========================================="

# 檢查資料庫檔案是否存在
if [ ! -f "$DB_FILE" ]; then
    log "${RED}錯誤: 資料庫檔案不存在: $DB_FILE${NC}"
    exit 1
fi

# 顯示資料庫資訊
DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
log "資料庫大小: $DB_SIZE"

# 執行備份
BACKUP_FILE="$BACKUP_DIR/data.sqlite.$DATE"
log "開始備份..."

if cp "$DB_FILE" "$BACKUP_FILE"; then
    log "${GREEN}✓ 備份成功: data.sqlite.$DATE${NC}"
    
    # 壓縮備份檔案 (節省空間)
    if gzip "$BACKUP_FILE"; then
        BACKUP_FILE="${BACKUP_FILE}.gz"
        COMPRESSED_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
        log "${GREEN}✓ 壓縮完成: $COMPRESSED_SIZE${NC}"
    fi
else
    log "${RED}✗ 備份失敗${NC}"
    exit 1
fi

# 檢查資料庫完整性
log "檢查資料庫完整性..."
INTEGRITY_CHECK=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;" 2>&1)

if [ "$INTEGRITY_CHECK" = "ok" ]; then
    log "${GREEN}✓ 資料庫完整性檢查通過${NC}"
else
    log "${RED}⚠ 警告: 資料庫可能有問題: $INTEGRITY_CHECK${NC}"
fi

# 清理舊備份 (保留最近 30 天)
log "清理舊備份 (保留最近 $KEEP_DAYS 天)..."
OLD_BACKUPS=$(find "$BACKUP_DIR" -name "data.sqlite.*" -mtime +$KEEP_DAYS)

if [ -n "$OLD_BACKUPS" ]; then
    echo "$OLD_BACKUPS" | while read file; do
        rm -f "$file"
        log "  已刪除: $(basename $file)"
    done
else
    log "  沒有需要清理的舊備份"
fi

# 顯示備份統計
BACKUP_COUNT=$(find "$BACKUP_DIR" -name "data.sqlite.*" | wc -l)
BACKUP_TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)

echo ""
echo "========================================="
echo -e "${GREEN}備份完成！${NC}"
echo "========================================="
echo "備份檔案: $(basename $BACKUP_FILE)"
echo "備份總數: $BACKUP_COUNT 個"
echo "總大小:   $BACKUP_TOTAL_SIZE"
echo ""
echo "最近的 5 個備份:"
ls -lht "$BACKUP_DIR"/data.sqlite.* | head -n 5

log "備份流程完成"
