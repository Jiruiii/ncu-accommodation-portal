#!/bin/bash

# 網站健康檢查腳本

echo "========================================="
echo "NCU Accommodation Portal 健康檢查"
echo "========================================="
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. 檢查後端服務
echo -e "${YELLOW}[1] 後端服務狀態${NC}"
if sudo systemctl is-active --quiet ncu-accommodation-backend.service; then
    echo -e "${GREEN}✓ 後端服務運行中${NC}"
    sudo systemctl status ncu-accommodation-backend.service --no-pager -l | head -n 10
else
    echo -e "${RED}✗ 後端服務未運行${NC}"
    echo "使用以下命令查看詳細錯誤："
    echo "  sudo journalctl -u ncu-accommodation-backend.service -n 50"
fi
echo ""

# 2. 檢查後端端口
echo -e "${YELLOW}[2] 後端端口檢查${NC}"
if ss -tlnp | grep -q ':5000'; then
    echo -e "${GREEN}✓ 後端端口 5000 已監聽${NC}"
    ss -tlnp | grep ':5000'
else
    echo -e "${RED}✗ 後端端口 5000 未監聽${NC}"
fi
echo ""

# 3. 檢查 Nginx 狀態
echo -e "${YELLOW}[3] Nginx 服務狀態${NC}"
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx 服務運行中${NC}"
else
    echo -e "${RED}✗ Nginx 服務未運行${NC}"
fi
echo ""

# 4. 檢查 Nginx 端口
echo -e "${YELLOW}[4] Nginx 端口檢查${NC}"
if ss -tlnp | grep -q ':443'; then
    echo -e "${GREEN}✓ HTTPS 端口 443 已監聽${NC}"
else
    echo -e "${RED}✗ HTTPS 端口 443 未監聽${NC}"
fi

if ss -tlnp | grep -q ':80'; then
    echo -e "${GREEN}✓ HTTP 端口 80 已監聽${NC}"
else
    echo -e "${RED}✗ HTTP 端口 80 未監聽${NC}"
fi
echo ""

# 5. 檢查前端構建
echo -e "${YELLOW}[5] 前端構建檢查${NC}"
if [ -d "/var/www/ncu-accommodation-portal/dist" ]; then
    echo -e "${GREEN}✓ dist 目錄存在${NC}"
    if [ -f "/var/www/ncu-accommodation-portal/dist/index.html" ]; then
        echo -e "${GREEN}✓ index.html 存在${NC}"
    else
        echo -e "${RED}✗ index.html 不存在${NC}"
    fi
else
    echo -e "${RED}✗ dist 目錄不存在${NC}"
    echo "請運行: npm run build"
fi
echo ""

# 6. 檢查 SSL 證書
echo -e "${YELLOW}[6] SSL 證書檢查${NC}"
if [ -f "/etc/letsencrypt/live/rooms.student.ncu.edu.tw/fullchain.pem" ]; then
    echo -e "${GREEN}✓ SSL 證書存在${NC}"
    EXPIRY=$(sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/rooms.student.ncu.edu.tw/fullchain.pem | cut -d= -f2)
    echo "  證書到期時間: $EXPIRY"
else
    echo -e "${RED}✗ SSL 證書不存在${NC}"
fi
echo ""

# 7. 檢查環境變數
echo -e "${YELLOW}[7] 環境配置檢查${NC}"
if [ -f "/var/www/ncu-accommodation-portal/backend/.env" ]; then
    echo -e "${GREEN}✓ 後端 .env 文件存在${NC}"
    echo "  Client ID: $(grep NCU_OAUTH_CLIENT_ID /var/www/ncu-accommodation-portal/backend/.env | cut -d= -f2)"
    echo "  Redirect URI: $(grep NCU_OAUTH_REDIRECT_URI /var/www/ncu-accommodation-portal/backend/.env | cut -d= -f2)"
else
    echo -e "${RED}✗ 後端 .env 文件不存在${NC}"
fi

if [ -f "/var/www/ncu-accommodation-portal/.env.production" ]; then
    echo -e "${GREEN}✓ 前端 .env.production 文件存在${NC}"
    echo "  API Base URL: $(grep VUE_APP_API_BASE_URL /var/www/ncu-accommodation-portal/.env.production | cut -d= -f2)"
else
    echo -e "${RED}✗ 前端 .env.production 文件不存在${NC}"
fi
echo ""

# 8. 測試 API 連接
echo -e "${YELLOW}[8] API 連接測試${NC}"
if curl -s -k https://rooms.student.ncu.edu.tw/api/stats > /dev/null 2>&1; then
    echo -e "${GREEN}✓ API 可訪問${NC}"
    echo "  測試: curl -k https://rooms.student.ncu.edu.tw/api/stats"
else
    echo -e "${RED}✗ API 無法訪問${NC}"
    echo "  嘗試直接訪問後端: curl http://localhost:5000/api/stats"
fi
echo ""

# 9. 檢查資料庫
echo -e "${YELLOW}[9] 資料庫檢查${NC}"
if [ -f "/var/www/ncu-accommodation-portal/backend/data.sqlite" ]; then
    echo -e "${GREEN}✓ 資料庫文件存在${NC}"
    DB_SIZE=$(du -h /var/www/ncu-accommodation-portal/backend/data.sqlite | cut -f1)
    echo "  資料庫大小: $DB_SIZE"
else
    echo -e "${RED}✗ 資料庫文件不存在${NC}"
fi
echo ""

# 10. 檢查最近的錯誤日誌
echo -e "${YELLOW}[10] 最近的錯誤日誌${NC}"
echo "Nginx 錯誤日誌 (最後 5 行):"
if [ -f "/var/log/nginx/error.log" ]; then
    sudo tail -n 5 /var/log/nginx/error.log
else
    echo "  無錯誤日誌"
fi
echo ""

echo "後端錯誤日誌 (最後 5 行):"
if [ -f "/var/log/ncu-accommodation-backend-error.log" ]; then
    sudo tail -n 5 /var/log/ncu-accommodation-backend-error.log
else
    echo "  無錯誤日誌或服務未啟動"
fi
echo ""

echo "========================================="
echo "健康檢查完成"
echo "========================================="
