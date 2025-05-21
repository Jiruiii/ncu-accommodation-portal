# ncu-accommodation-portal

A website that organizes NCU accommodation information

## Project setup

```bash
npm install
```

### Customize configuration

See [Configuration Reference](https://cli.vuejs.org/config/).

## 資料庫同步流程

為確保團隊成員之間的資料庫保持同步，請遵循以下流程：

### 初次設置

1. 確保已拉取最新的代碼
2. 運行 `python backend/db_sync.py status` 檢查當前同步狀態
3. 運行 `python backend/db_sync.py import` 匯入最新的資料庫

### 日常使用

每次開始工作前：

1. 拉取最新代碼 `git pull`
2. 運行 `python backend/db_sync.py import` 更新本地資料庫

在重要變更後：

1. 運行 `python backend/db_sync.py export` 匯出資料庫
2. 提交代碼時包含新的匯出檔 `git add backend/db_sync/*.json`
3. 提交更改 `git commit -m "更新資料庫匯出檔"`

### 解決衝突

如果遇到資料庫衝突：

1. 運行 `python backend/db_sync.py status` 查看可用的匯出檔
2. 選擇適當的匯出檔進行匯入：`python backend/db_sync.py import -f <filename>`

### 注意事項

- 不要直接修改 `backend/db_sync` 目錄中的 JSON 檔案
- 如果新增了模型或更改了模型結構，確保更新資料庫匯出檔
- `last_updated` 等時間戳欄位可能導致衝突，請在匯入時注意

### 如一直發生git衝突

```bash
git rm -r --cached .
git add .
git commit -m "clear git cache"
```
