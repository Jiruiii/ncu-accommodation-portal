#!/bin/bash

#############################################################################
# NCU 租屋網站 - 磁碟空間監控腳本
# 
# 功能: 監控磁碟使用率，超過閾值時發送警告
#############################################################################

# 配置
THRESHOLD=80  # 警告閾值 (百分比)
LOG_FILE="/var/log/ncu-disk-monitor.log"
PARTITION="/var/www"

# 獲取磁碟使用率
USAGE=$(df -h "$PARTITION" | awk 'NR==2{print $5}' | sed 's/%//')

# 記錄日誌
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# 檢查使用率
if [ "$USAGE" -ge "$THRESHOLD" ]; then
    log "⚠️  警告: 磁碟使用率達到 ${USAGE}% (閾值: ${THRESHOLD}%)"
    log "建議清理舊的日誌和備份檔案"
    
    # 列出大檔案
    log "最大的 5 個檔案:"
    du -ah /var/www/ncu-accommodation-portal | sort -rh | head -n 5 | tee -a "$LOG_FILE"
else
    log "✅ 磁碟使用率正常: ${USAGE}%"
fi
