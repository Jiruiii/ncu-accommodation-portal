#!/bin/bash

# 配置驗證腳本

echo "========================================="
echo "NCU Accommodation Portal 配置驗證"
echo "========================================="
echo ""

# 顏色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 檢查後端環境變數
echo -e "${YELLOW}後端配置 (backend/.env):${NC}"
if [ -f "/var/www/ncu-accommodation-portal/backend/.env" ]; then
    echo -e "${GREEN}✓ 文件存在${NC}"
    echo ""
    echo "Client ID:"
    grep "NCU_OAUTH_CLIENT_ID" /var/www/ncu-accommodation-portal/backend/.env
    echo ""
    echo "Client Secret (前20個字符):"
    grep "NCU_OAUTH_CLIENT_SECRET" /var/www/ncu-accommodation-portal/backend/.env | sed 's/=.*/=*********************/'
    echo ""
    echo "Redirect URI:"
    grep "NCU_OAUTH_REDIRECT_URI" /var/www/ncu-accommodation-portal/backend/.env
    echo ""
else
    echo -e "${RED}✗ 文件不存在${NC}"
fi

# 檢查前端環境變數
echo -e "${YELLOW}前端配置 (.env.production):${NC}"
if [ -f "/var/www/ncu-accommodation-portal/.env.production" ]; then
    echo -e "${GREEN}✓ 文件存在${NC}"
    echo ""
    cat /var/www/ncu-accommodation-portal/.env.production
    echo ""
else
    echo -e "${RED}✗ 文件不存在${NC}"
fi

# 檢查期望值
echo -e "${YELLOW}期望配置 (從圖片):${NC}"
echo "Client ID: 20250918165350qQGrRKwccnPj"
echo "Client Secret: yCBZ4wijlSYsCTpO6B6UsnzzS7BiuGmftrQxlBhEl4qcGkq1YzJ"
echo "Redirect URI: https://rooms.student.ncu.edu.tw/auth/callback"
echo "Login URL: https://rooms.student.ncu.edu.tw/auth/login"
echo ""

# 比對配置
echo -e "${YELLOW}配置匹配檢查:${NC}"

BACKEND_CLIENT_ID=$(grep "NCU_OAUTH_CLIENT_ID" /var/www/ncu-accommodation-portal/backend/.env 2>/dev/null | cut -d= -f2)
EXPECTED_CLIENT_ID="20250918165350qQGrRKwccnPj"

if [ "$BACKEND_CLIENT_ID" = "$EXPECTED_CLIENT_ID" ]; then
    echo -e "${GREEN}✓ Client ID 正確${NC}"
else
    echo -e "${RED}✗ Client ID 不匹配${NC}"
    echo "  當前: $BACKEND_CLIENT_ID"
    echo "  期望: $EXPECTED_CLIENT_ID"
fi

BACKEND_SECRET=$(grep "NCU_OAUTH_CLIENT_SECRET" /var/www/ncu-accommodation-portal/backend/.env 2>/dev/null | cut -d= -f2)
EXPECTED_SECRET="yCBZ4wijlSYsCTpO6B6UsnzzS7BiuGmftrQxlBhEl4qcGkq1YzJ"

if [ "$BACKEND_SECRET" = "$EXPECTED_SECRET" ]; then
    echo -e "${GREEN}✓ Client Secret 正確${NC}"
else
    echo -e "${RED}✗ Client Secret 不匹配${NC}"
    echo "  請檢查 backend/.env 文件"
fi

BACKEND_REDIRECT=$(grep "NCU_OAUTH_REDIRECT_URI" /var/www/ncu-accommodation-portal/backend/.env 2>/dev/null | cut -d= -f2)
EXPECTED_REDIRECT="https://rooms.student.ncu.edu.tw/auth/callback"

if [ "$BACKEND_REDIRECT" = "$EXPECTED_REDIRECT" ]; then
    echo -e "${GREEN}✓ Redirect URI 正確${NC}"
else
    echo -e "${RED}✗ Redirect URI 不匹配${NC}"
    echo "  當前: $BACKEND_REDIRECT"
    echo "  期望: $EXPECTED_REDIRECT"
fi

echo ""
echo "========================================="
echo "配置驗證完成"
echo "========================================="
