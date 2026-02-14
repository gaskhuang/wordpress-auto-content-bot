# 🔧 故障排除 - 執行卡住問題

## 🚨 你遇到的問題

根據除錯日誌,程式卡在:
```
2026-01-24 11:30:06 取得 AI Engine 實例...
2026-01-24 11:30:06 執行查詢...
```

然後就沒有繼續了,這表示 **AI Engine 的 API 呼叫卡住了**。

---

## 🎯 快速診斷

### 步驟 1: 檢查 AI Engine 設定

1. 前往 WordPress 後台
2. **Meow Apps → AI Engine → Settings**
3. 確認以下幾點:

**OpenAI 設定** (如果你使用 OpenAI):
- [ ] API Key 欄位有填寫
- [ ] API Key 格式正確 (sk-proj-...)
- [ ] 點擊「Test」按鈕測試連線
- [ ] 看到綠色的「Connection successful」訊息

**檢查方法:**
```
前往: Meow Apps → AI Engine → Settings → OpenAI 標籤
確認: API Key 欄位不是空的
測試: 點擊下方的「Test API Key」或「Test」按鈕
```

### 步驟 2: 測試 AI Engine Playground

1. 前往 **Meow Apps → AI Engine → Playground**
2. 在文字框中輸入: `測試`
3. 點擊 **Generate**
4. 看是否有回應

**如果沒有回應或出現錯誤:**
- 記下錯誤訊息
- 這表示 API Key 有問題

### 步驟 3: 檢查 API 帳號狀態

1. 前往 https://platform.openai.com/account/usage
2. 登入你的 OpenAI 帳號
3. 檢查:
   - [ ] 帳號是否有餘額
   - [ ] 是否超過使用限額
   - [ ] API Key 是否仍然有效

---

## 💡 常見原因與解決方法

### 原因 1: API Key 無效或過期

**症狀:**
- 程式卡住不動
- AI Engine Playground 無法測試成功
- 沒有錯誤訊息

**解決方法:**
1. 撤銷舊的 API Key
2. 在 OpenAI 後台創建新的 API Key
3. 複製新的 Key
4. 在 AI Engine 設定中更新
5. 點擊 Save
6. 重新測試

**步驟:**
```
1. https://platform.openai.com/api-keys
2. 找到舊的 Key → 點擊「Revoke」
3. 點擊「Create new secret key」
4. 輸入名稱 (例如: WordPress GCR)
5. 複製 Key (只會顯示一次!)
6. 回到 WordPress: Meow Apps → AI Engine → Settings → OpenAI
7. 貼上新的 Key
8. 點擊 Save
```

---

### 原因 2: OpenAI 帳號無餘額

**症狀:**
- 之前可以用,現在不行了
- API Key 是對的

**檢查方法:**
```
1. https://platform.openai.com/account/usage
2. 查看「Credits」欄位
3. 如果是 $0.00 → 需要充值
```

**解決方法:**
```
1. https://platform.openai.com/account/billing/overview
2. 點擊「Add payment method」
3. 輸入信用卡資訊
4. 點擊「Add to credit balance」
5. 充值至少 $5 USD
```

---

### 原因 3: PHP 執行超時

**症狀:**
- 程式運行一段時間後停止
- 除錯日誌突然中斷

**解決方法:**

編輯 `wp-config.php`,在 `<?php` 後面添加:
```php
set_time_limit(600); // 10 分鐘
ini_set('max_execution_time', 600);
ini_set('memory_limit', '512M');
```

或編輯 `.htaccess`:
```apache
php_value max_execution_time 600
php_value max_input_time 600
php_value memory_limit 512M
```

---

### 原因 4: 伺服器防火牆阻擋

**症狀:**
- 本地測試正常
- 線上伺服器不行

**解決方法:**

檢查伺服器是否可以連接到 OpenAI:
```bash
# SSH 登入伺服器後執行
curl -I https://api.openai.com/v1/models

# 應該看到 HTTP/2 200 或 401
# 如果看到 timeout 或 connection refused → 防火牆問題
```

聯絡主機商,要求開放以下網域:
- `api.openai.com`
- `*.openai.com`

---

### 原因 5: AI Engine 版本過舊

**檢查版本:**
```
WordPress 後台 → 插件 → 已安裝的插件
找到 AI Engine → 查看版本號
```

**更新方法:**
```
1. 如果有「更新可用」提示 → 點擊更新
2. 或手動更新:
   - 停用 AI Engine
   - 刪除 AI Engine
   - 重新安裝最新版
   - 啟用
   - 重新設定 API Key
```

---

## 🔬 進階診斷

### 啟用 WordPress Debug

編輯 `wp-config.php`:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
define('SCRIPT_DEBUG', true);
```

然後查看日誌:
```bash
tail -f wp-content/debug.log
```

執行「立即執行一次」,看 debug.log 中有沒有錯誤訊息。

### 手動測試 AI Engine API

在 WordPress 後台 → **工具 → Site Health → Info → Server**,查看:
- PHP Version
- PHP Extensions
- cURL Version

確保:
- PHP >= 7.4
- cURL 已啟用
- OpenSSL 已啟用

---

## ✅ 解決步驟檢查清單

按照順序執行:

- [ ] 步驟 1: 檢查 AI Engine 是否已安裝並啟用
- [ ] 步驟 2: 檢查 API Key 是否已設定
- [ ] 步驟 3: 在 AI Engine Settings 中測試 API Key
- [ ] 步驟 4: 在 AI Engine Playground 測試生成
- [ ] 步驟 5: 檢查 OpenAI 帳號是否有餘額
- [ ] 步驟 6: 創建新的 API Key 並更新
- [ ] 步驟 7: 增加 PHP 執行時間限制
- [ ] 步驟 8: 啟用 WordPress Debug 查看錯誤
- [ ] 步驟 9: 更新 AI Engine 到最新版
- [ ] 步驟 10: 聯絡主機商檢查防火牆

---

## 🎯 最可能的原因 (根據你的情況)

從你的除錯日誌來看,最可能是以下兩個原因之一:

### 1. API Key 無效 (機率 70%)

**現象:**
- 程式卡在「執行查詢...」
- 沒有錯誤訊息
- AI Engine 顯示已啟用

**解決:**
```
1. 前往 AI Engine Settings
2. 測試 API Key
3. 如果測試失敗 → 創建新的 Key
4. 重新保存設定
```

### 2. OpenAI API 回應緩慢 (機率 20%)

**現象:**
- 文章很長 (5250 字)
- Prompt 很長 (7517 字)
- 總共約 12,767 字 → 約 16,000 tokens

**解決:**
```
1. 降低「最大文章長度」設定
   從 8000 → 改為 3000
2. 這樣 Prompt 會變短
3. AI 回應會更快
```

### 3. PHP 超時 (機率 10%)

**現象:**
- 等很久沒反應

**解決:**
```
增加 PHP 執行時間 (見上方說明)
```

---

## 📞 如果還是無法解決

請提供以下資訊:

1. **AI Engine Settings 截圖**
   - Meow Apps → AI Engine → Settings → OpenAI 標籤
   - 遮蓋 API Key,只顯示是否有填寫

2. **AI Engine Playground 測試結果**
   - 輸入「測試」後是否有回應
   - 如果有錯誤,錯誤訊息是什麼

3. **OpenAI 帳號狀態**
   - 是否有餘額
   - API Key 狀態

4. **完整的除錯日誌**
   - 除錯日誌區塊的完整內容

5. **wp-content/debug.log 內容**
   - 如果有啟用 WP_DEBUG

---

## 💡 臨時解決方案

如果急需使用,可以:

1. **降低處理篇數**
   - 從 5 篇改為 1 篇
   - 這樣即使卡住也只影響一篇

2. **縮短文章長度限制**
   - 從 8000 改為 2000
   - 只處理短文章

3. **使用更快的模型**
   - 從 gpt-4o-mini 改為... 等等,你已經用最快的了
   - 或改用 gpt-4o (雖然貴但可能更穩定)

---

**現在請按照「解決步驟檢查清單」逐一檢查,特別是前 6 個步驟!**
