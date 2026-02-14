# 項目結構說明

這份文件說明 Gasker Content Refresher 插件的檔案結構與各檔案的功能。

## 目錄結構

```
gasker-content-refresher/
├── gasker-content-refresher.php    # 主插件文件
├── includes/                        # 核心功能模組
│   └── admin-page.php              # 後台管理介面
├── assets/                          # 前端資源
│   ├── css/
│   │   └── admin.css               # 後台樣式
│   └── js/
│       └── admin.js                # 後台腳本
├── README.md                        # 完整說明文件 (繁體中文)
├── INSTALL.md                       # 詳細安裝指南
├── QUICKSTART.md                    # 快速開始指南
├── CHANGELOG.md                     # 版本更新日誌
├── LICENSE                          # GPL v2 授權
├── readme.txt                       # WordPress.org 標準格式
└── .gitignore                       # Git 忽略清單
```

## 核心文件說明

### gasker-content-refresher.php

**功能**: 插件主文件,包含所有核心邏輯

**主要類別**: `Gasker_Content_Refresher`

**關鍵方法**:
- `activate()` - 插件啟用時執行
- `deactivate()` - 插件停用時執行
- `process_old_posts()` - 處理舊文章 (核心功能)
- `rewrite_single_post()` - 改寫單篇文章
- `build_prompt()` - 構建 AI Prompt
- `call_ai_engine()` - 呼叫 AI Engine API
- `validate_content()` - 驗證內容安全性
- `update_post()` - 更新文章
- `log_execution()` - 記錄執行日誌
- `send_notification_email()` - 發送通知郵件

**WordPress Hooks**:
- `register_activation_hook` - 註冊啟用 Hook
- `register_deactivation_hook` - 註冊停用 Hook
- `admin_menu` - 添加管理選單
- `admin_init` - 註冊設定
- `admin_enqueue_scripts` - 載入管理員資源
- `wp_ajax_gcr_run_now` - AJAX 立即執行
- `wp_ajax_gcr_clear_logs` - AJAX 清除日誌
- `gcr_daily_rewrite_event` - Cron 任務 Hook

**常量定義**:
- `GCR_VERSION` - 插件版本
- `GCR_PLUGIN_DIR` - 插件目錄路徑
- `GCR_PLUGIN_URL` - 插件 URL
- `GCR_PLUGIN_FILE` - 插件文件路徑

### includes/admin-page.php

**功能**: 後台管理介面 HTML

**包含區塊**:
1. **基本設定區** - 每日篇數、冷卻天數、最大長度
2. **AI 設定區** - 模型選擇、目標語言
3. **發布模式區** - 待審閱/自動發布
4. **排除設定區** - 分類排除、文章 ID 排除
5. **通知設定區** - Email 通知開關
6. **系統狀態區** - AI Engine 狀態、排程狀態
7. **手動操作區** - 立即執行按鈕
8. **執行日誌區** - 歷史執行記錄表格

**表單處理**:
- 使用 WordPress Settings API
- 自動 NONCE 驗證
- 自動權限檢查

### assets/css/admin.css

**功能**: 後台介面樣式

**主要樣式**:
- `.gcr-admin-container` - Grid 佈局
- `.gcr-settings-panel` - 左側設定面板
- `.gcr-sidebar` - 右側操作面板
- `.gcr-logs-section` - 日誌區域
- `.gcr-notification` - 通知訊息
- `.gcr-status-*` - 狀態指示器
- 響應式設計 (1200px 斷點)

**設計特色**:
- 使用 WordPress 原生配色
- Grid 佈局 (左右分欄)
- 響應式設計
- 動畫效果 (slideIn, spin)

### assets/js/admin.js

**功能**: 後台互動功能

**主要功能**:
- `runNow()` - 立即執行 AJAX 請求
- `clearLogs()` - 清除日誌 AJAX 請求
- `toggleDetails()` - 展開/收合日誌詳情
- `showNotification()` - 顯示通知訊息

**AJAX 通訊**:
- 使用 WordPress AJAX API
- 自動 NONCE 驗證
- 錯誤處理
- 載入狀態顯示

**jQuery 使用**:
- 事件綁定
- DOM 操作
- AJAX 請求
- 動畫效果

## 資料庫結構

### wp_options 表

| Option Name | 說明 | 資料類型 |
|------------|------|---------|
| `gcr_settings` | 插件設定 | 序列化陣列 |
| `gcr_logs` | 執行日誌 (最多 50 筆) | 序列化陣列 |
| `cron` | WP-Cron 排程資訊 | 序列化陣列 |

### wp_postmeta 表

| Meta Key | 說明 | 資料類型 |
|----------|------|---------|
| `_gcr_last_rewrite` | 最後改寫時間 | MySQL datetime |

## 設定資料結構

### gcr_settings (陣列)

```php
array(
    'posts_per_day' => 10,              // 每日處理篇數
    'cooldown_days' => 30,              // 冷卻天數
    'language' => 'zh-TW',              // 目標語言
    'ai_model' => 'gpt-4o',             // AI 模型
    'auto_publish' => false,            // 自動發布
    'max_post_length' => 5000,          // 最大文章長度
    'enable_email_notification' => false, // 啟用通知
    'notification_email' => '',         // 通知信箱
    'exclude_categories' => array(),    // 排除分類 ID
    'exclude_post_ids' => '',           // 排除文章 ID (逗號分隔)
)
```

### gcr_logs (陣列)

```php
array(
    array(
        'timestamp' => '2025-01-24 10:00:00',
        'total' => 10,
        'success' => 8,
        'failed' => 1,
        'skipped' => 1,
        'posts' => array(
            array(
                'post_id' => 123,
                'post_title' => '文章標題',
                'status' => 'success',      // success|failed|skipped
                'message' => '成功改寫',
                'tokens_used' => 1500,
            ),
            // ...更多文章
        ),
    ),
    // ...更多執行記錄 (最多 50 筆)
)
```

## 工作流程圖

```
                    WP-Cron 每日觸發
                           ↓
            [process_old_posts() 被呼叫]
                           ↓
           查詢符合條件的舊文章 (最多 N 篇)
                           ↓
                ┌──────────┴──────────┐
                ↓                     ↓
        有符合文章               無符合文章
                ↓                     ↓
        逐篇處理                   結束
                ↓
    [rewrite_single_post()]
                ↓
        檢查文章長度
                ↓
        ┌───────┴───────┐
        ↓               ↓
   長度 OK          長度超過
        ↓               ↓
   呼叫 AI          標記跳過
        ↓
   [call_ai_engine()]
        ↓
   AI Engine API
        ↓
    收到回傳內容
        ↓
   [validate_content()]
        ↓
   驗證 HTML 結構
        ↓
   ┌────┴────┐
   ↓         ↓
 驗證通過   驗證失敗
   ↓         ↓
更新文章   放棄更新
   ↓         ↓
   └────┬────┘
        ↓
  記錄執行結果
        ↓
  [log_execution()]
        ↓
   所有文章處理完成
        ↓
  發送通知郵件 (如果啟用)
        ↓
      結束
```

## 安全機制

### 1. 輸入驗證

```php
// 數字驗證
absint($input['posts_per_day']);

// 文字清理
sanitize_text_field($input['language']);

// Email 驗證
sanitize_email($input['notification_email']);

// 陣列清理
array_map('absint', $input['exclude_categories']);
```

### 2. 輸出跳脫

```php
// HTML 跳脫
esc_html($post->post_title);

// 屬性跳脫
esc_attr($settings['posts_per_day']);

// URL 跳脫
esc_url($plugin_url);
```

### 3. 權限檢查

```php
// 管理權限
if (!current_user_can('manage_options')) {
    wp_die(__('您沒有權限', 'gasker-content-refresher'));
}
```

### 4. NONCE 驗證

```php
// 產生 NONCE
wp_create_nonce('gcr_ajax_nonce');

// 驗證 NONCE
check_ajax_referer('gcr_ajax_nonce', 'nonce');
```

### 5. 內容驗證

```php
// 長度檢查
if ($new_length < ($original_length * 0.5)) return false;

// 圖片數量檢查
if ($new_img_count < $original_img_count) return false;

// HTML 標籤檢查
foreach ($tags_to_check as $tag) {
    // 驗證標籤數量
}
```

## 效能優化

### 1. 批次限制
- 每次最多處理 N 篇 (預設 10)
- 避免 PHP 執行逾時
- 避免 API 超時

### 2. 資料庫查詢優化
- 使用 `posts_per_page` 限制
- 使用索引欄位 (post_modified)
- 避免 N+1 查詢

### 3. 快取機制
- 選項使用 WordPress Object Cache
- 避免重複查詢

### 4. 日誌限制
- 僅保留最近 50 筆
- 自動清理舊記錄

## 擴展性

### 添加新的 AI 模型

1. 在 `admin-page.php` 的模型選單添加選項
2. 在 `call_ai_engine()` 中處理新模型
3. 測試新模型的回傳格式

### 自訂 Prompt

修改 `build_prompt()` 方法:
```php
private function build_prompt($content, $settings) {
    // 自訂 Prompt 邏輯
    return $custom_prompt;
}
```

### 添加新的驗證規則

在 `validate_content()` 添加檢查:
```php
// 新的驗證規則
if (!$this->custom_validation($new)) {
    return false;
}
```

## 除錯技巧

### 啟用 WordPress Debug

在 `wp-config.php` 添加:
```php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

### 查看日誌文件

```bash
tail -f /path/to/wordpress/wp-content/debug.log
```

### 檢查 Cron 任務

```bash
wp cron event list
wp cron test
```

### 手動觸發 Cron

```bash
wp cron event run gcr_daily_rewrite_event
```

## 相依性

### 必要
- WordPress 6.0+
- PHP 7.4+
- AI Engine 插件

### 建議
- WP-Crontrol (檢查 Cron)
- Query Monitor (效能監控)
- UpdraftPlus (備份)

## 授權資訊

- 插件授權: GPL v2 or later
- 相容授權: WordPress GPL
- 允許商業使用
- 允許修改與再發布

---

**文件版本**: 1.0.0
**最後更新**: 2025-01-24
**作者**: Gasker Tech
