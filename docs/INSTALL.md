# 安裝與部署指南

這是 Gasker Content Refresher 的詳細安裝與部署指南。

## 前置需求

### 1. WordPress 環境
- WordPress 6.0 或更高版本
- PHP 7.4 或更高版本
- MySQL 5.7+ 或 MariaDB 10.3+
- 足夠的伺服器權限執行 WP-Cron

### 2. AI Engine 插件

**必須** 先安裝 AI Engine 插件:

1. 前往 WordPress 後台
2. 插件 → 安裝插件
3. 搜尋 "AI Engine"
4. 安裝並啟用 (作者: Jordy Meow)

### 3. API Key

準備以下任一 API Key:

#### OpenAI (推薦)
1. 前往 [OpenAI Platform](https://platform.openai.com/)
2. 註冊/登入帳號
3. 前往 API Keys 頁面
4. 創建新的 API Key
5. 確保帳號有足夠的餘額

#### Google Gemini
1. 前往 [Google AI Studio](https://makersuite.google.com/)
2. 取得 API Key
3. 啟用 Gemini API

## 安裝步驟

### 方式 1: WordPress 後台上傳 (推薦)

1. **打包插件**
   ```bash
   cd gasker-content-refresher
   zip -r gasker-content-refresher.zip . -x "*.git*" -x "node_modules/*" -x "*.md"
   ```

2. **上傳安裝**
   - 前往 WordPress 後台 → 插件 → 安裝插件
   - 點擊「上傳插件」
   - 選擇 `gasker-content-refresher.zip`
   - 點擊「立即安裝」
   - 安裝完成後點擊「啟用插件」

### 方式 2: FTP/SFTP 上傳

1. **連接到伺服器**
   ```bash
   sftp username@your-server.com
   ```

2. **上傳檔案**
   ```bash
   cd /path/to/wordpress/wp-content/plugins/
   put -r gasker-content-refresher
   ```

3. **設定權限**
   ```bash
   chmod 755 gasker-content-refresher
   chmod 644 gasker-content-refresher/*.php
   ```

4. **啟用插件**
   - 前往 WordPress 後台 → 插件
   - 找到 "Gasker Content Refresher"
   - 點擊「啟用」

### 方式 3: WP-CLI 安裝

```bash
# 複製插件到 plugins 目錄
cp -r gasker-content-refresher /path/to/wordpress/wp-content/plugins/

# 啟用插件
wp plugin activate gasker-content-refresher
```

## 配置 AI Engine

插件安裝後,需要先配置 AI Engine:

1. 前往 **Meow Apps → AI Engine**
2. 點擊 **Settings** 標籤
3. 選擇 **OpenAI** 或 **Google** 標籤
4. 輸入您的 API Key
5. 點擊「Save」儲存

### 測試 AI Engine

```bash
# 使用 WP-CLI 測試
wp eval "
  if (class_exists('Meow_MWAI_Core')) {
    echo 'AI Engine is active!';
  } else {
    echo 'AI Engine is NOT active!';
  }
"
```

## 初始設定

### 1. 前往設定頁面

WordPress 後台 → 設定 → Content Refresher

### 2. 基本配置

```
每日處理篇數: 5-10 篇 (建議從 5 篇開始)
冷卻天數: 30 天
最大文章長度: 5000 字
```

### 3. AI 模型選擇

```
AI 模型: GPT-4o (推薦)
目標語言: 繁體中文
```

### 4. 發布模式

**初期強烈建議使用「待審閱」模式:**
- 改寫後的文章會設為「待審閱」狀態
- 您可以先檢查品質
- 確認沒問題再手動發布

### 5. 排除設定

設定哪些內容不應被自動改寫:

```
排除分類:
- 公司簡介
- 關於我們
- 隱私政策
- 服務條款

排除文章 ID: 1, 5, 10 (用逗號分隔)
```

### 6. Email 通知 (選用)

```
☑ 啟用通知
通知信箱: your-email@example.com
```

## 測試運行

### 1. 手動測試

1. 點擊「立即執行一次」按鈕
2. 等待執行完成 (可能需要 30-60 秒)
3. 查看執行結果
4. 前往文章列表,檢查「待審閱」的文章

### 2. 檢查日誌

在設定頁面下方的「執行日誌」區域:
- 查看處理了哪些文章
- 檢查成功/失敗狀態
- 查看 Token 消耗量
- 閱讀錯誤訊息 (如果有)

### 3. 驗證 Cron 排程

```bash
# 使用 WP-CLI 檢查
wp cron event list

# 應該看到 gcr_daily_rewrite_event
```

或透過插件如 "WP Crontrol" 來檢查。

## 伺服器配置

### 1. PHP 設定建議

編輯 `php.ini` 或在 WordPress 的 `wp-config.php` 中添加:

```php
// 增加執行時間限制
define('WP_CRON_LOCK_TIMEOUT', 60);
set_time_limit(300); // 5 分鐘

// 增加記憶體限制
define('WP_MEMORY_LIMIT', '256M');
define('WP_MAX_MEMORY_LIMIT', '512M');
```

### 2. 啟用真實 Cron (建議)

WordPress 預設使用 WP-Cron,在流量低的網站可能不會準時執行。

**停用 WP-Cron:**

在 `wp-config.php` 添加:
```php
define('DISABLE_WP_CRON', true);
```

**設定系統 Cron:**

編輯 crontab:
```bash
crontab -e
```

添加:
```bash
*/15 * * * * wget -q -O - https://your-site.com/wp-cron.php?doing_wp_cron >/dev/null 2>&1
```

或使用 WP-CLI:
```bash
*/15 * * * * cd /path/to/wordpress && wp cron event run --due-now >/dev/null 2>&1
```

### 3. 防火牆設定

如果使用 Cloudflare 或其他 CDN:
- 確保 `wp-cron.php` 可以被訪問
- 不要快取 `wp-admin` 路徑

## 故障排除

### 問題 1: AI Engine 未啟用

**症狀:** 設定頁面顯示警告訊息

**解決方法:**
```bash
# 檢查 AI Engine 是否已安裝
wp plugin list | grep ai-engine

# 如果已安裝但未啟用
wp plugin activate ai-engine

# 如果未安裝
wp plugin install ai-engine --activate
```

### 問題 2: Cron 任務未執行

**症狀:** 每日沒有自動執行

**檢查方法:**
```bash
# 檢查排程
wp cron event list | grep gcr

# 手動觸發
wp cron event run gcr_daily_rewrite_event
```

**解決方法:**
- 檢查 WP-Cron 是否正常運作
- 考慮改用系統 Cron (見上方說明)

### 問題 3: API 錯誤

**症狀:** 執行日誌顯示 API 錯誤

**檢查清單:**
- API Key 是否正確
- API 帳號是否有餘額
- 網路是否能連接到 OpenAI/Google

**測試 API 連線:**
```bash
# 測試 OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"

# 測試 Gemini
curl "https://generativelanguage.googleapis.com/v1/models?key=YOUR_API_KEY"
```

### 問題 4: 執行超時

**症狀:** 插件執行到一半就停止

**解決方法:**
1. 減少「每日處理篇數」(例如從 10 改為 5)
2. 降低「最大文章長度」(例如從 5000 改為 3000)
3. 增加 PHP 執行時間限制 (見上方伺服器配置)

### 問題 5: HTML 結構損壞

**症狀:** 改寫後的文章 HTML 有問題

**解決方法:**
1. 切換到 GPT-4o 模型 (更穩定)
2. 檢查原始文章的 HTML 是否已經有問題
3. 查看執行日誌中的錯誤訊息

## 監控與維護

### 1. 定期檢查

每週檢查:
- 執行日誌中的成功率
- Token 消耗量
- API 費用

### 2. 資料庫備份

**強烈建議** 在啟用自動發布模式前:

```bash
# 使用 WP-CLI 備份
wp db export backup.sql

# 或使用插件如 UpdraftPlus
```

### 3. 效能監控

使用 Google Search Console 監控:
- 索引覆蓋率
- 搜尋結果點擊率
- 平均排名變化

## 升級插件

### 從舊版本升級

1. **備份資料庫**
   ```bash
   wp db export pre-upgrade-backup.sql
   ```

2. **停用插件**
   ```bash
   wp plugin deactivate gasker-content-refresher
   ```

3. **更新檔案**
   - 刪除舊版本
   - 上傳新版本

4. **重新啟用**
   ```bash
   wp plugin activate gasker-content-refresher
   ```

## 卸載插件

### 完整移除步驟

1. **停用插件**
   ```bash
   wp plugin deactivate gasker-content-refresher
   ```

2. **刪除插件**
   ```bash
   wp plugin delete gasker-content-refresher
   ```

3. **清理資料庫 (選用)**
   ```sql
   DELETE FROM wp_options WHERE option_name LIKE 'gcr_%';
   DELETE FROM wp_postmeta WHERE meta_key = '_gcr_last_rewrite';
   ```

## 支援

如需協助,請聯絡技術支援或查閱 README.md。

---

**安裝完成!** 現在可以開始使用 Gasker Content Refresher 提升您的內容新鮮度了。
