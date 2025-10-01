#!/bin/bash

# NCU Accommodation Portal 部署腳本
# 此腳本會完成以下操作：
# 1. 構建前端 Vue 應用
# 2. 更新 Nginx 配置
# 3. 設置後端服務
# 4. 重啟所有服務

set -e  # 遇到錯誤立即退出

echo "========================================="
echo "NCU Accommodation Portal 部署開始"
echo "========================================="

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 項目目錄
PROJECT_DIR="/var/www/ncu-accommodation-portal"
BACKEND_DIR="$PROJECT_DIR/backend"

# 步驟 1: 檢查當前目錄
echo -e "${YELLOW}[1/7] 檢查項目目錄...${NC}"
cd $PROJECT_DIR
echo -e "${GREEN}✓ 當前目錄: $(pwd)${NC}"

# 步驟 2: 構建前端
echo -e "${YELLOW}[2/7] 構建前端 Vue 應用...${NC}"
echo "使用 .env.production 配置文件"
npm run build
echo -e "${GREEN}✓ 前端構建完成${NC}"

# 步驟 3: 檢查 dist 目錄
if [ ! -d "$PROJECT_DIR/dist" ]; then
    echo -e "${RED}✗ 錯誤: dist 目錄不存在${NC}"
    exit 1
fi
echo -e "${GREEN}✓ dist 目錄存在${NC}"

# 步驟 4: 更新 Nginx 配置
echo -e "${YELLOW}[3/7] 更新 Nginx 配置...${NC}"
sudo cp $PROJECT_DIR/nginx-config.conf /etc/nginx/sites-available/default
echo -e "${GREEN}✓ Nginx 配置已更新${NC}"

# 測試 Nginx 配置
echo -e "${YELLOW}[4/7] 測試 Nginx 配置...${NC}"
sudo nginx -t
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx 配置測試通過${NC}"
else
    echo -e "${RED}✗ Nginx 配置測試失敗${NC}"
    exit 1
fi

# 步驟 5: 設置後端服務
echo -e "${YELLOW}[5/7] 設置後端 systemd 服務...${NC}"

# 停止現有的後端進程
echo "停止現有的後端進程..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# 複製服務文件
sudo cp $PROJECT_DIR/ncu-accommodation-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ncu-accommodation-backend.service
echo -e "${GREEN}✓ 後端服務已設置${NC}"

# 步驟 6: 啟動服務
echo -e "${YELLOW}[6/7] 啟動所有服務...${NC}"

# 啟動後端
echo "啟動後端服務..."
sudo systemctl start ncu-accommodation-backend.service
sleep 3

# 檢查後端狀態
if sudo systemctl is-active --quiet ncu-accommodation-backend.service; then
    echo -e "${GREEN}✓ 後端服務運行中${NC}"
else
    echo -e "${RED}✗ 後端服務啟動失敗${NC}"
    echo "檢查日誌: sudo journalctl -u ncu-accommodation-backend.service -n 50"
    exit 1
fi

# 重啟 Nginx
echo "重啟 Nginx..."
sudo systemctl restart nginx
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Nginx 已重啟${NC}"
else
    echo -e "${RED}✗ Nginx 重啟失敗${NC}"
    exit 1
fi

# 步驟 7: 驗證部署
echo -e "${YELLOW}[7/7] 驗證部署...${NC}"

# 檢查後端端口
if ss -tlnp | grep -q ':5000'; then
    echo -e "${GREEN}✓ 後端端口 5000 已監聽${NC}"
else
    echo -e "${RED}✗ 後端端口 5000 未監聽${NC}"
fi

# 檢查 Nginx 端口
if ss -tlnp | grep -q ':443'; then
    echo -e "${GREEN}✓ Nginx HTTPS 端口 443 已監聽${NC}"
else
    echo -e "${RED}✗ Nginx HTTPS 端口 443 未監聽${NC}"
fi

# 檢查 SSL 證書
if [ -f "/etc/letsencrypt/live/rooms.student.ncu.edu.tw/fullchain.pem" ]; then
    echo -e "${GREEN}✓ SSL 證書存在${NC}"
    # 檢查證書過期時間
    EXPIRY=$(sudo openssl x509 -enddate -noout -in /etc/letsencrypt/live/rooms.student.ncu.edu.tw/fullchain.pem | cut -d= -f2)
    echo "  證書到期時間: $EXPIRY"
else
    echo -e "${YELLOW}⚠ SSL 證書不存在或無法訪問${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "========================================="
echo ""
echo "網站 URL: https://rooms.student.ncu.edu.tw"
echo ""
echo "有用的命令："
echo "  查看後端日誌:     sudo journalctl -u ncu-accommodation-backend.service -f"
echo "  查看後端狀態:     sudo systemctl status ncu-accommodation-backend.service"
echo "  重啟後端:         sudo systemctl restart ncu-accommodation-backend.service"
echo "  查看 Nginx 日誌:  sudo tail -f /var/log/nginx/error.log"
echo "  測試 API:         curl -k https://rooms.student.ncu.edu.tw/api/stats"
echo ""
