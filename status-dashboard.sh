#!/bin/bash

#############################################################################
# NCU 租屋網站 - 系統狀態儀表板
# 
# 功能: 快速查看系統所有重要資訊
#############################################################################

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

clear

echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║          NCU 租屋網站 - 系統狀態儀表板                                ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}⏰ 當前時間:${NC} $(date '+%Y-%m-%d %H:%M:%S %Z')"
echo -e "${BLUE}🖥️  主機名稱:${NC} $(hostname)"
echo -e "${BLUE}🌐 網站 URL:${NC} https://rooms.student.ncu.edu.tw"
echo ""

# 1. 服務狀態
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📊 服務狀態${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# 後端服務
if systemctl is-active --quiet ncu-accommodation-backend.service; then
    BACKEND_STATUS="${GREEN}✅ 運行中${NC}"
    BACKEND_UPTIME=$(systemctl show ncu-accommodation-backend.service --property=ActiveEnterTimestamp | cut -d= -f2)
    BACKEND_MEMORY=$(systemctl show ncu-accommodation-backend.service --property=MemoryCurrent | cut -d= -f2)
    BACKEND_MEMORY_MB=$((BACKEND_MEMORY / 1024 / 1024))
else
    BACKEND_STATUS="${RED}❌ 停止${NC}"
    BACKEND_UPTIME="N/A"
    BACKEND_MEMORY_MB="N/A"
fi

echo -e "後端服務:   $BACKEND_STATUS"
if [ "$BACKEND_UPTIME" != "N/A" ]; then
    echo -e "  啟動時間: $BACKEND_UPTIME"
    echo -e "  記憶體:   ${BACKEND_MEMORY_MB} MB"
fi

# Nginx 服務
if systemctl is-active --quiet nginx; then
    NGINX_STATUS="${GREEN}✅ 運行中${NC}"
else
    NGINX_STATUS="${RED}❌ 停止${NC}"
fi
echo -e "Nginx:      $NGINX_STATUS"

# 2. 網路端口
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔌 網路端口${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ss -tlnp 2>/dev/null | grep -q ':5000'; then
    echo -e "後端 (5000):   ${GREEN}✅ 監聽中${NC}"
else
    echo -e "後端 (5000):   ${RED}❌ 未監聽${NC}"
fi

if ss -tlnp 2>/dev/null | grep -q ':443'; then
    echo -e "HTTPS (443):   ${GREEN}✅ 監聽中${NC}"
else
    echo -e "HTTPS (443):   ${RED}❌ 未監聽${NC}"
fi

if ss -tlnp 2>/dev/null | grep -q ':80'; then
    echo -e "HTTP (80):     ${GREEN}✅ 監聽中${NC}"
else
    echo -e "HTTP (80):     ${RED}❌ 未監聽${NC}"
fi

# 3. 資料庫狀態
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}💾 資料庫狀態${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DB_FILE="/var/www/ncu-accommodation-portal/backend/data.sqlite"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(du -h "$DB_FILE" | cut -f1)
    DB_MODIFIED=$(stat -c %y "$DB_FILE" | cut -d. -f1)
    echo -e "資料庫檔案: ${GREEN}✅ 存在${NC}"
    echo -e "  大小:     $DB_SIZE"
    echo -e "  更新時間: $DB_MODIFIED"
    
    # 檢查資料庫完整性
    INTEGRITY=$(sqlite3 "$DB_FILE" "PRAGMA integrity_check;" 2>&1)
    if [ "$INTEGRITY" = "ok" ]; then
        echo -e "  完整性:   ${GREEN}✅ 正常${NC}"
    else
        echo -e "  完整性:   ${RED}⚠️  異常${NC}"
    fi
else
    echo -e "資料庫檔案: ${RED}❌ 不存在${NC}"
fi

# 4. 備份狀態
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}📦 備份狀態${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

BACKUP_DIR="/var/www/ncu-accommodation-portal/backups"
if [ -d "$BACKUP_DIR" ]; then
    BACKUP_COUNT=$(find "$BACKUP_DIR" -name "data.sqlite.*" 2>/dev/null | wc -l)
    if [ $BACKUP_COUNT -gt 0 ]; then
        LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/data.sqlite.* 2>/dev/null | head -n 1)
        LATEST_BACKUP_TIME=$(stat -c %y "$LATEST_BACKUP" | cut -d. -f1)
        BACKUP_SIZE=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1)
        
        echo -e "備份總數:   ${GREEN}$BACKUP_COUNT 個${NC}"
        echo -e "總大小:     $BACKUP_SIZE"
        echo -e "最新備份:   $(basename $LATEST_BACKUP)"
        echo -e "  時間:     $LATEST_BACKUP_TIME"
    else
        echo -e "備份總數:   ${YELLOW}⚠️  無備份${NC}"
        echo -e "建議執行:   ./backup-db.sh"
    fi
else
    echo -e "備份目錄:   ${RED}❌ 不存在${NC}"
fi

# 5. 系統資源
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}💻 系統資源${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# CPU 負載
LOAD=$(uptime | awk -F'load average:' '{print $2}' | xargs)
echo -e "CPU 負載:   $LOAD"

# 記憶體使用
MEM_INFO=$(free -h | awk 'NR==2{printf "使用: %s / 總共: %s (%.0f%%)", $3, $2, $3/$2*100}')
echo -e "記憶體:     $MEM_INFO"

# 磁碟使用
DISK_INFO=$(df -h /var/www | awk 'NR==2{printf "使用: %s / 總共: %s (%s)", $3, $2, $5}')
echo -e "磁碟空間:   $DISK_INFO"

# 系統運行時間
UPTIME=$(uptime -p)
echo -e "運行時間:   $UPTIME"

# 6. 前端構建
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🎨 前端狀態${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

DIST_DIR="/var/www/ncu-accommodation-portal/dist"
if [ -d "$DIST_DIR" ] && [ -f "$DIST_DIR/index.html" ]; then
    DIST_SIZE=$(du -sh "$DIST_DIR" 2>/dev/null | cut -f1)
    BUILD_TIME=$(stat -c %y "$DIST_DIR/index.html" | cut -d. -f1)
    echo -e "構建目錄:   ${GREEN}✅ 存在${NC}"
    echo -e "  大小:     $DIST_SIZE"
    echo -e "  構建時間: $BUILD_TIME"
else
    echo -e "構建目錄:   ${RED}❌ 不存在或不完整${NC}"
    echo -e "建議執行:   npm run build"
fi

# 7. SSL 證書
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}🔒 SSL 證書${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

CERT_FILE="/etc/letsencrypt/live/rooms.student.ncu.edu.tw/fullchain.pem"
if [ -f "$CERT_FILE" ]; then
    EXPIRY=$(sudo openssl x509 -enddate -noout -in "$CERT_FILE" 2>/dev/null | cut -d= -f2)
    DAYS_LEFT=$(( ($(date -d "$EXPIRY" +%s) - $(date +%s)) / 86400 ))
    
    echo -e "證書狀態:   ${GREEN}✅ 有效${NC}"
    echo -e "  到期日:   $EXPIRY"
    
    if [ $DAYS_LEFT -lt 30 ]; then
        echo -e "  剩餘天數: ${RED}⚠️  $DAYS_LEFT 天 (即將到期!)${NC}"
    else
        echo -e "  剩餘天數: ${GREEN}$DAYS_LEFT 天${NC}"
    fi
else
    echo -e "證書狀態:   ${RED}❌ 不存在${NC}"
fi

# 8. 最近錯誤
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}⚠️  最近錯誤 (最近 5 條)${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "/var/log/ncu-accommodation-backend-error.log" ]; then
    ERRORS=$(sudo grep -i "error\|exception\|critical" /var/log/ncu-accommodation-backend-error.log 2>/dev/null | tail -n 5)
    if [ -n "$ERRORS" ]; then
        echo "$ERRORS" | while read line; do
            echo -e "${RED}  • $line${NC}"
        done
    else
        echo -e "${GREEN}  ✅ 無最近錯誤${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠️  日誌檔案不存在${NC}"
fi

# 底部操作提示
echo ""
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}💡 快速操作${NC}"
echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  健康檢查:       ./check-health.sh"
echo "  備份資料庫:     ./backup-db.sh"
echo "  驗證配置:       ./verify-config.sh"
echo "  重啟後端:       sudo systemctl restart ncu-accommodation-backend.service"
echo "  查看後端日誌:   sudo journalctl -u ncu-accommodation-backend.service -f"
echo "  部署更新:       ./deploy.sh"
echo ""
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
