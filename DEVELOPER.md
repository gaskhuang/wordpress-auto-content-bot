# 開發者指南

這份文件提供給想要修改或擴展 Gasker Content Refresher 的開發者。

## 開發環境設置

### 1. 本地 WordPress 環境

推薦使用以下工具之一:
- [Local by Flywheel](https://localwp.com/)
- [XAMPP](https://www.apachefriends.org/)
- [Docker + WordPress](https://hub.docker.com/_/wordpress)

### 2. 克隆專案

```bash
cd /path/to/wordpress/wp-content/plugins/
git clone [repository-url] gasker-content-refresher
```

### 3. 安裝相依性

```bash
# 安裝 AI Engine 插件
wp plugin install ai-engine --activate

# 啟用本插件
wp plugin activate gasker-content-refresher
```

### 4. 開發工具

推薦使用:
- **IDE**: VSCode / PhpStorm
- **除錯**: Query Monitor 插件
- **Cron**: WP Crontrol 插件
- **程式碼檢查**: PHP CodeSniffer (WordPress Coding Standards)

## 程式碼架構

### 類別結構

```php
class Gasker_Content_Refresher {
    // 單例模式
    private static $instance = null;

    // 常量
    const OPTION_NAME = 'gcr_settings';
    const LOG_OPTION_NAME = 'gcr_logs';
    const CRON_HOOK = 'gcr_daily_rewrite_event';

    // 核心方法
    public function process_old_posts()      // 主要處理邏輯
    private function rewrite_single_post()   // 改寫單篇
    private function build_prompt()          // 構建 Prompt
    private function call_ai_engine()        // AI API 呼叫
    private function validate_content()      // 內容驗證
    private function update_post()           // 更新文章
    private function log_execution()         // 記錄日誌
}
```

### 資料流程

```
用戶觸發 (Cron/手動)
    ↓
process_old_posts()
    ↓
查詢符合條件的文章 (WP_Query)
    ↓
逐篇處理 (foreach)
    ↓
rewrite_single_post($post)
    ↓
build_prompt($content) → Prompt 字串
    ↓
call_ai_engine($prompt) → AI 回傳內容
    ↓
validate_content($original, $new) → true/false
    ↓
update_post($post_id, $new_content)
    ↓
log_execution($results)
```

## Hook 系統

### Action Hooks

插件提供以下 Action Hooks 供擴展使用:

```php
// 在處理文章前觸發
do_action('gcr_before_process_posts', $args);

// 在處理單篇文章前觸發
do_action('gcr_before_rewrite_post', $post);

// 在處理單篇文章後觸發
do_action('gcr_after_rewrite_post', $post, $result);

// 在所有文章處理完畢後觸發
do_action('gcr_after_process_posts', $results);
```

**使用範例:**

```php
// 在改寫前做些事
add_action('gcr_before_rewrite_post', function($post) {
    error_log('準備改寫文章: ' . $post->post_title);
});

// 在改寫後發送通知
add_action('gcr_after_rewrite_post', function($post, $result) {
    if ($result['status'] === 'success') {
        // 發送到 Slack
        send_slack_notification("文章已改寫: {$post->post_title}");
    }
}, 10, 2);
```

### Filter Hooks

插件提供以下 Filter Hooks 供自訂使用:

```php
// 自訂查詢參數
$args = apply_filters('gcr_query_args', $args);

// 自訂 Prompt
$prompt = apply_filters('gcr_prompt', $prompt, $post);

// 自訂驗證規則
$is_valid = apply_filters('gcr_validate_content', $is_valid, $original, $new);

// 自訂日誌格式
$log_entry = apply_filters('gcr_log_entry', $log_entry, $results);
```

**使用範例:**

```php
// 自訂 Prompt 模板
add_filter('gcr_prompt', function($prompt, $post) {
    // 針對特定分類使用不同 Prompt
    if (has_category('tech', $post)) {
        return "你是技術編輯,請改寫以下技術文章...\n" . $post->post_content;
    }
    return $prompt;
}, 10, 2);

// 擴展驗證規則
add_filter('gcr_validate_content', function($is_valid, $original, $new) {
    // 額外檢查:確保關鍵字密度
    if ($is_valid && !check_keyword_density($new)) {
        return false;
    }
    return $is_valid;
}, 10, 3);
```

## 自訂擴展範例

### 範例 1: 自訂 AI 模型

```php
// 添加自訂模型選項
add_filter('gcr_ai_models', function($models) {
    $models['custom-model'] = '自訂模型';
    return $models;
});

// 處理自訂模型
add_filter('gcr_call_ai_engine', function($result, $prompt, $model) {
    if ($model === 'custom-model') {
        // 呼叫自訂 API
        $response = call_custom_ai_api($prompt);
        return array(
            'success' => true,
            'content' => $response,
            'tokens_used' => 0,
        );
    }
    return $result;
}, 10, 3);
```

### 範例 2: 整合 Slack 通知

```php
add_action('gcr_after_process_posts', function($results) {
    $webhook_url = 'https://hooks.slack.com/services/YOUR/WEBHOOK/URL';

    $message = sprintf(
        "內容更新完成\n總計: %d\n成功: %d\n失敗: %d",
        $results['total'],
        $results['success'],
        $results['failed']
    );

    wp_remote_post($webhook_url, array(
        'body' => json_encode(array('text' => $message)),
        'headers' => array('Content-Type' => 'application/json'),
    ));
});
```

### 範例 3: 自動生成摘要

```php
add_action('gcr_after_rewrite_post', function($post, $result) {
    if ($result['status'] === 'success') {
        // 使用 AI 生成新的摘要
        $excerpt_prompt = "請為以下文章生成 150 字的摘要:\n" . $post->post_content;

        if (class_exists('Meow_MWAI_Core')) {
            $ai = Meow_MWAI_Core::get_instance();
            $query = new Meow_MWAI_Query_Text($excerpt_prompt);
            $reply = $ai->run_query($query);

            // 更新摘要
            wp_update_post(array(
                'ID' => $post->ID,
                'post_excerpt' => $reply->result,
            ));
        }
    }
}, 10, 2);
```

### 範例 4: 排除特定作者的文章

```php
add_filter('gcr_query_args', function($args) {
    // 排除 ID 為 1 的作者 (通常是管理員)
    $args['author__not_in'] = array(1);
    return $args;
});
```

## 測試

### 單元測試 (PHPUnit)

```bash
# 安裝 WordPress 測試框架
bash bin/install-wp-tests.sh wordpress_test root '' localhost latest

# 執行測試
phpunit
```

### 手動測試清單

- [ ] 插件啟用/停用正常
- [ ] Cron 任務正確註冊
- [ ] 手動執行功能正常
- [ ] 文章篩選邏輯正確
- [ ] AI 改寫功能正常
- [ ] HTML 結構保持完整
- [ ] 圖片不會遺失
- [ ] 待審閱模式正常
- [ ] 自動發布模式正常
- [ ] 日誌記錄正確
- [ ] Email 通知正常
- [ ] 排除規則生效
- [ ] 設定儲存正確
- [ ] AJAX 功能正常
- [ ] 多語言支援正常

### 除錯技巧

**1. 啟用 Debug 模式**

```php
// wp-config.php
define('WP_DEBUG', true);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);
```

**2. 記錄自訂日誌**

```php
error_log('GCR Debug: ' . print_r($data, true));
```

**3. 使用 Query Monitor**

安裝 Query Monitor 插件查看:
- SQL 查詢
- HTTP 請求
- PHP 錯誤
- Hook 執行順序

**4. 測試 Cron**

```bash
# 列出所有 Cron 任務
wp cron event list

# 執行特定任務
wp cron event run gcr_daily_rewrite_event

# 測試 Cron 系統
wp cron test
```

## 程式碼風格

遵循 [WordPress Coding Standards](https://developer.wordpress.org/coding-standards/wordpress-coding-standards/php/):

### PHP

```php
// 使用 Tab 縮排
if ( condition ) {
    do_something();
}

// 函數命名使用底線
function gcr_custom_function() {
    // ...
}

// 類別命名使用 PascalCase
class GCR_Custom_Class {
    // ...
}

// Yoda 條件 (常數在左)
if ( 'success' === $status ) {
    // ...
}

// 陣列使用短語法
$array = array( 'key' => 'value' );
```

### JavaScript

```javascript
// 使用 Tab 縮排
if (condition) {
    doSomething();
}

// 變數命名使用 camelCase
const myVariable = 'value';

// 函數命名使用 camelCase
function myFunction() {
    // ...
}
```

### CSS

```css
/* 使用 Tab 縮排 */
.my-class {
    property: value;
}

/* 類別命名使用連字號 */
.gcr-admin-wrap {
    /* ... */
}
```

## 程式碼檢查

### PHP CodeSniffer

```bash
# 安裝
composer require --dev squizlabs/php_codesniffer
composer require --dev wp-coding-standards/wpcs

# 設定
./vendor/bin/phpcs --config-set installed_paths vendor/wp-coding-standards/wpcs

# 檢查
./vendor/bin/phpcs --standard=WordPress gasker-content-refresher.php

# 自動修正
./vendor/bin/phpcbf --standard=WordPress gasker-content-refresher.php
```

## 效能優化

### 1. 資料庫查詢優化

```php
// ✗ 錯誤: N+1 查詢
foreach ($posts as $post) {
    $meta = get_post_meta($post->ID);
}

// ✓ 正確: 批次查詢
update_meta_cache('post', wp_list_pluck($posts, 'ID'));
foreach ($posts as $post) {
    $meta = get_post_meta($post->ID);
}
```

### 2. 避免重複查詢

```php
// 使用靜態變數快取
private function get_settings() {
    static $settings = null;
    if (null === $settings) {
        $settings = get_option(self::OPTION_NAME);
    }
    return $settings;
}
```

### 3. 批次處理

```php
// 分批處理大量資料
$batch_size = 10;
$offset = 0;

while ($posts = get_posts(array(
    'posts_per_page' => $batch_size,
    'offset' => $offset,
))) {
    foreach ($posts as $post) {
        // 處理
    }
    $offset += $batch_size;
}
```

## 安全檢查清單

- [ ] 所有用戶輸入都經過清理
- [ ] 所有輸出都經過跳脫
- [ ] 使用 NONCE 驗證
- [ ] 檢查用戶權限
- [ ] 使用預處理語句 (如果直接查詢)
- [ ] 避免暴露敏感資訊
- [ ] API Key 不應硬編碼
- [ ] 檔案上傳有類型限制
- [ ] 避免路徑遍歷攻擊

## 發布流程

### 1. 版本更新

```bash
# 更新版本號
# - gasker-content-refresher.php (Plugin header)
# - gasker-content-refresher.php (GCR_VERSION constant)
# - readme.txt (Stable tag)
# - CHANGELOG.md (新版本區塊)
```

### 2. 測試

```bash
# 執行所有測試
phpunit

# 手動測試
# (參考上方測試清單)
```

### 3. 打包

```bash
# 執行部署腳本
./deploy.sh
```

### 4. 發布

```bash
# 上傳到 WordPress.org (如果有申請)
svn commit -m "Release version x.x.x"

# 或透過 GitHub Release
git tag -a v1.0.0 -m "Version 1.0.0"
git push origin v1.0.0
```

## 貢獻指南

### 提交 Pull Request

1. Fork 專案
2. 創建分支: `git checkout -b feature/amazing-feature`
3. 提交變更: `git commit -m 'Add amazing feature'`
4. 推送分支: `git push origin feature/amazing-feature`
5. 開啟 Pull Request

### Commit 訊息格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type:**
- feat: 新功能
- fix: 錯誤修正
- docs: 文件變更
- style: 程式碼格式
- refactor: 重構
- test: 測試
- chore: 雜項

**範例:**

```
feat(ai): 添加 Claude 3 模型支援

- 新增 Claude 3 Opus 選項
- 新增 Claude 3 Sonnet 選項
- 更新 Prompt 模板

Closes #123
```

## 資源連結

### WordPress 開發
- [WordPress Developer Resources](https://developer.wordpress.org/)
- [Plugin Handbook](https://developer.wordpress.org/plugins/)
- [Coding Standards](https://developer.wordpress.org/coding-standards/)

### AI Engine
- [AI Engine Documentation](https://meowapps.com/ai-engine/)
- [AI Engine GitHub](https://github.com/jordymeow/ai-engine)

### 工具
- [WP-CLI](https://wp-cli.org/)
- [Query Monitor](https://querymonitor.com/)
- [WP Crontrol](https://wordpress.org/plugins/wp-crontrol/)

---

**Happy Coding! 🚀**

如有問題,歡迎開 Issue 或聯絡技術支援。
