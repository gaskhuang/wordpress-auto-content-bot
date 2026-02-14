# 除錯指南 - Gasker Content Refresher

## ✅ 已增強的除錯功能

我已經為你添加了詳細的除錯日誌功能!現在可以清楚看到執行過程中的每一步。

---

## 📊 新增的除錯功能

### 1. **詳細的執行日誌**
- ✅ 每個步驟都有日誌記錄
- ✅ 顯示執行時間
- ✅ 顯示錯誤訊息
- ✅ 顯示 AI Engine 呼叫狀態
- ✅ 顯示 Token 使用量

### 2. **除錯日誌面板**
在後台設定頁面底部新增了「除錯日誌」區塊,即時顯示:
- 最近 100 筆執行記錄
- 每個步驟的詳細資訊
- 錯誤訊息與堆疊追蹤

### 3. **WordPress Debug Log**
如果啟用 WP_DEBUG,所有日誌也會寫入 `wp-content/debug.log`

---

## 🔍 如何查看除錯資訊

### 方式 1: 後台除錯日誌面板 (最簡單)

1. 前往 WordPress 後台
2. **設定 → Content Refresher**
3. 滾動到頁面最底部
4. 查看 **「除錯日誌」** 區塊
5. 這裡會顯示完整的執行過程

**日誌範例:**
```
2025-01-24 11:00:00 === 開始執行手動改寫任務 ===
2025-01-24 11:00:00 --- 開始處理舊文章 ---
2025-01-24 11:00:01 載入設定: {"posts_per_day":5,"ai_model":"gpt-4o"...}
2025-01-24 11:00:01 查詢參數: {"post_type":"post","post_status":"publish"...}
2025-01-24 11:00:02 找到 3 篇符合條件的文章
2025-01-24 11:00:02 開始處理文章 ID: 123 - 測試文章
2025-01-24 11:00:02   文章長度: 1500 字 (上限: 5000)
2025-01-24 11:00:02   檢查 AI Engine 狀態...
2025-01-24 11:00:02   AI Engine 已啟用
2025-01-24 11:00:02   構建 Prompt...
2025-01-24 11:00:02   Prompt 長度: 1800 字
2025-01-24 11:00:03   呼叫 AI Engine (模型: gpt-4o)...
2025-01-24 11:00:03     AI Engine 呼叫開始...
2025-01-24 11:00:03     模型: gpt-4o
2025-01-24 11:00:03     取得 AI Engine 實例...
2025-01-24 11:00:03     創建查詢物件...
2025-01-24 11:00:03     設定模型: gpt-4o
2025-01-24 11:00:03     設定 max_tokens: 4000
2025-01-24 11:00:03     執行查詢...
2025-01-24 11:00:05     查詢成功
2025-01-24 11:00:05     回應長度: 1600 字
2025-01-24 11:00:05     Token 使用: 2500
2025-01-24 11:00:05   AI Engine 回應成功,Token 使用: 2500
2025-01-24 11:00:05   驗證內容安全性...
2025-01-24 11:00:05   內容驗證通過
2025-01-24 11:00:05   更新文章 (自動發布: 否)...
2025-01-24 11:00:06   文章更新成功
2025-01-24 11:00:06 文章 ID 123 處理結果: success - 成功改寫
```

### 方式 2: WordPress Debug Log

1. 編輯 `wp-config.php` 添加:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

2. 查看日誌檔案:
```bash
tail -f /path/to/wordpress/wp-content/debug.log | grep GCR
```

3. 日誌會顯示為:
```
[24-Jan-2025 11:00:00 UTC] [GCR] === 開始執行手動改寫任務 ===
[24-Jan-2025 11:00:00 UTC] [GCR] --- 開始處理舊文章 ---
...
```

---

## 🐛 常見錯誤與解決方法

### 錯誤 1: "AI Engine 插件未啟用"

**日誌顯示:**
```
錯誤: AI Engine 未啟用
```

**原因:**
- AI Engine 插件未安裝或未啟用

**解決方法:**
```bash
# 檢查 AI Engine 狀態
wp plugin list | grep ai-engine

# 如果未安裝
wp plugin install ai-engine --activate

# 或在後台手動安裝
WordPress 後台 → 插件 → 安裝插件 → 搜尋 "AI Engine"
```

---

### 錯誤 2: "Meow_MWAI_Core 類別不存在"

**日誌顯示:**
```
AI Engine 錯誤: Meow_MWAI_Core 類別不存在
```

**原因:**
- AI Engine 版本過舊
- AI Engine 未正確載入

**解決方法:**
1. 更新 AI Engine 到最新版本
2. 停用並重新啟用 AI Engine
3. 清除 WordPress 快取

---

### 錯誤 3: "無法取得 AI Engine 實例"

**日誌顯示:**
```
AI Engine 錯誤: 無法取得 AI Engine 實例
```

**原因:**
- AI Engine 初始化失敗
- API Key 未設定

**解決方法:**
1. 前往 **Meow Apps → AI Engine → Settings**
2. 確認已選擇 **OpenAI** 或 **Google** 標籤
3. 輸入有效的 API Key
4. 點擊 **Save**
5. 測試 AI Engine:
   ```bash
   wp eval "var_dump(class_exists('Meow_MWAI_Core'));"
   ```

---

### 錯誤 4: API 相關錯誤

**日誌顯示:**
```
AI Engine 錯誤: Incorrect API key provided
AI Engine 錯誤: You exceeded your current quota
AI Engine 錯誤: Rate limit exceeded
```

**原因與解決方法:**

| 錯誤訊息 | 原因 | 解決方法 |
|---------|------|---------|
| `Incorrect API key` | API Key 錯誤 | 檢查 AI Engine 中的 API Key 是否正確 |
| `exceeded your quota` | 帳號無餘額 | 前往 OpenAI 充值 |
| `Rate limit exceeded` | 請求過於頻繁 | 降低每日處理篇數,或等待幾分鐘後重試 |
| `Model not found` | 模型不存在 | 確認模型名稱正確 (gpt-4o, gpt-4o-mini) |

---

### 錯誤 5: "找到 0 篇符合條件的文章"

**日誌顯示:**
```
找到 0 篇符合條件的文章
警告: 沒有找到符合條件的文章
```

**原因:**
- 所有文章都是最近 30 天內更新的
- 文章被排除規則過濾掉了
- 網站沒有已發布的文章

**解決方法:**
1. 檢查冷卻天數設定是否太短
2. 檢查排除分類是否排除了所有文章
3. 確認網站有已發布的文章:
   ```bash
   wp post list --post_type=post --post_status=publish
   ```

---

### 錯誤 6: "內容驗證失敗"

**日誌顯示:**
```
驗證失敗: 內容不符合安全標準
內容驗證失敗,未更新
```

**原因:**
- AI 回傳的內容太短 (少於原文 50%)
- 圖片數量減少
- HTML 標籤數量異常

**解決方法:**
1. 檢查 AI 回傳的內容 (在除錯日誌中)
2. 嘗試切換到 GPT-4o 模型 (更穩定)
3. 檢查原文章是否本身就有問題
4. 調整 Prompt 設定

---

### 錯誤 7: "文章更新失敗"

**日誌顯示:**
```
錯誤: 文章更新失敗
更新文章失敗
```

**原因:**
- 資料庫權限不足
- 文章被鎖定
- 文章已被刪除

**解決方法:**
1. 檢查資料庫權限
2. 確認文章存在且可編輯
3. 檢查 WordPress 錯誤日誌

---

## 🔧 進階除錯技巧

### 1. 手動測試 AI Engine

在 WordPress 後台,前往 **Meow Apps → AI Engine → Playground**,測試 AI 是否正常運作。

### 2. 檢查 PHP 錯誤

```bash
# 查看 PHP 錯誤日誌
tail -f /var/log/php_errors.log
```

### 3. 使用 WP-CLI 手動觸發

```bash
# 手動執行 Cron 任務
wp cron event run gcr_daily_rewrite_event

# 檢查結果
wp option get gcr_logs --format=json
```

### 4. 檢查資料庫

```sql
-- 查看插件設定
SELECT * FROM wp_options WHERE option_name LIKE 'gcr_%';

-- 查看除錯日誌
SELECT * FROM wp_options WHERE option_name = 'gcr_debug_logs';
```

---

## 📋 除錯檢查清單

遇到問題時,按照以下順序檢查:

- [ ] 查看後台「除錯日誌」面板
- [ ] 確認 AI Engine 已安裝並啟用
- [ ] 確認 API Key 已正確設定
- [ ] 確認 API 帳號有餘額
- [ ] 確認有符合條件的文章
- [ ] 查看 WordPress debug.log
- [ ] 測試 AI Engine Playground
- [ ] 檢查 PHP 版本 (需要 7.4+)
- [ ] 檢查資料庫連線
- [ ] 清除 WordPress 快取

---

## 🆘 仍然無法解決?

如果按照以上步驟仍無法解決:

1. **收集資訊:**
   - 複製完整的除錯日誌
   - 記錄錯誤訊息
   - 記錄 WordPress 版本
   - 記錄 PHP 版本
   - 記錄 AI Engine 版本

2. **聯絡支援:**
   - 提供上述資訊
   - 描述問題發生的步驟
   - 提供截圖 (如果有)

---

## ✅ 除錯日誌維護

### 清除除錯日誌

後台除錯日誌會保留最近 100 筆記錄,如果需要清除:

1. 點擊「除錯日誌」區塊右上角的 **「清除除錯日誌」** 按鈕
2. 或使用 WP-CLI:
   ```bash
   wp option delete gcr_debug_logs
   ```

### 查看歷史日誌

除錯日誌儲存在資料庫中:
```bash
wp option get gcr_debug_logs --format=json | jq
```

---

**現在你有完整的除錯能力!** 🎉

重新上傳插件後,點擊「立即執行一次」,然後立即查看「除錯日誌」區塊,你就能看到完整的執行過程和任何錯誤訊息。
