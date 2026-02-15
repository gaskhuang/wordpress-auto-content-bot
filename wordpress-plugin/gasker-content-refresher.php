<?php
/**
 * Plugin Name: Gasker Content Refresher
 * Plugin URI: https://gasker.tech
 * Description: AI 內容管理系統：自動改寫舊文章 + AI 生成全新文章,提升 SEO 新鮮度
 * Version: 1.1.0
 * Author: Gasker Tech
 * Author URI: https://gasker.tech
 * License: GPL v2 or later
 * License URI: https://www.gnu.org/licenses/gpl-2.0.html
 * Text Domain: gasker-content-refresher
 * Domain Path: /languages
 * Requires at least: 6.0
 * Requires PHP: 7.4
 */

// 防止直接訪問
if (!defined('ABSPATH')) {
    exit;
}

// 定義插件常量
define('GCR_VERSION', '1.1.0');
define('GCR_PLUGIN_DIR', plugin_dir_path(__FILE__));
define('GCR_PLUGIN_URL', plugin_dir_url(__FILE__));
define('GCR_PLUGIN_FILE', __FILE__);

/**
 * 主插件類別
 */
class Gasker_Content_Refresher
{

    /**
     * 單例實例
     */
    private static $instance = null;

    /**
     * 選項名稱
     */
    const OPTION_NAME = 'gcr_settings';
    const LOG_OPTION_NAME = 'gcr_logs';

    /**
     * Cron Hook 名稱
     */
    const CRON_HOOK = 'gcr_daily_rewrite_event';
    const CRON_HOOK_NEW = 'gcr_daily_new_post_event';

    /**
     * 獲取單例實例
     */
    public static function get_instance()
    {
        if (null === self::$instance) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * 構造函數
     */
    private function __construct()
    {
        $this->init_hooks();
    }

    /**
     * 初始化 Hooks
     */
    private function init_hooks()
    {
        // 插件啟用/停用
        register_activation_hook(GCR_PLUGIN_FILE, array($this, 'activate'));
        register_deactivation_hook(GCR_PLUGIN_FILE, array($this, 'deactivate'));

        // 管理員介面
        add_action('admin_menu', array($this, 'add_admin_menu'));
        add_action('admin_init', array($this, 'register_settings'));
        add_action('admin_enqueue_scripts', array($this, 'enqueue_admin_assets'));

        // AJAX 處理
        add_action('wp_ajax_gcr_run_now', array($this, 'ajax_run_now'));
        add_action('wp_ajax_gcr_generate_now', array($this, 'ajax_generate_now'));
        add_action('wp_ajax_gcr_clear_logs', array($this, 'ajax_clear_logs'));
        add_action('wp_ajax_gcr_clear_debug_logs', array($this, 'ajax_clear_debug_logs'));

        // Cron 任務
        add_action(self::CRON_HOOK, array($this, 'process_old_posts'));
        add_action(self::CRON_HOOK_NEW, array($this, 'generate_new_posts'));

        // 載入文字域
        add_action('plugins_loaded', array($this, 'load_textdomain'));
    }

    /**
     * 插件啟用
     */
    public function activate()
    {
        // 設置預設選項
        $default_settings = array(
            // 改寫舊文章設定
            'posts_per_day' => 10,
            'cooldown_days' => 30,
            'language' => 'zh-TW',
            'ai_model' => 'gpt-4o',
            'auto_publish' => false, // 預設為待審閱模式
            'max_post_length' => 5000,
            'enable_email_notification' => false,
            'notification_email' => get_option('admin_email'),
            'exclude_categories' => array(),
            'exclude_post_ids' => '',
            // 新增文章設定
            'enable_new_posts' => false,
            'new_posts_per_day' => 1,
            'new_post_topics' => '',
            'new_post_category' => 0,
            'new_post_status' => 'draft',
        );

        if (!get_option(self::OPTION_NAME)) {
            add_option(self::OPTION_NAME, $default_settings);
        }

        // 初始化日誌
        if (!get_option(self::LOG_OPTION_NAME)) {
            add_option(self::LOG_OPTION_NAME, array());
        }

        // 設置 Cron 排程
        if (!wp_next_scheduled(self::CRON_HOOK)) {
            wp_schedule_event(time(), 'daily', self::CRON_HOOK);
        }
        if (!wp_next_scheduled(self::CRON_HOOK_NEW)) {
            wp_schedule_event(time(), 'daily', self::CRON_HOOK_NEW);
        }

        // 清空 rewrite rules
        flush_rewrite_rules();
    }

    /**
     * 插件停用
     */
    public function deactivate()
    {
        // 移除 Cron 排程
        $timestamp = wp_next_scheduled(self::CRON_HOOK);
        if ($timestamp) {
            wp_unschedule_event($timestamp, self::CRON_HOOK);
        }
        $timestamp_new = wp_next_scheduled(self::CRON_HOOK_NEW);
        if ($timestamp_new) {
            wp_unschedule_event($timestamp_new, self::CRON_HOOK_NEW);
        }

        // 清空 rewrite rules
        flush_rewrite_rules();
    }

    /**
     * 載入文字域
     */
    public function load_textdomain()
    {
        load_plugin_textdomain(
            'gasker-content-refresher',
            false,
            dirname(plugin_basename(GCR_PLUGIN_FILE)) . '/languages'
        );
    }

    /**
     * 添加管理員選單
     */
    public function add_admin_menu()
    {
        add_options_page(
            __('Gasker Content Refresher', 'gasker-content-refresher'),
            __('Content Refresher', 'gasker-content-refresher'),
            'manage_options',
            'gasker-content-refresher',
            array($this, 'render_admin_page')
        );
    }

    /**
     * 註冊設定
     */
    public function register_settings()
    {
        register_setting(
            'gcr_settings_group',
            self::OPTION_NAME,
            array($this, 'sanitize_settings')
        );
    }

    /**
     * 清理設定資料
     */
    public function sanitize_settings($input)
    {
        $sanitized = array();

        $sanitized['posts_per_day'] = absint($input['posts_per_day']);
        $sanitized['cooldown_days'] = absint($input['cooldown_days']);
        $sanitized['language'] = sanitize_text_field($input['language']);
        $sanitized['ai_model'] = sanitize_text_field($input['ai_model']);
        $sanitized['auto_publish'] = isset($input['auto_publish']) ? true : false;
        $sanitized['max_post_length'] = absint($input['max_post_length']);
        $sanitized['enable_email_notification'] = isset($input['enable_email_notification']) ? true : false;
        $sanitized['notification_email'] = sanitize_email($input['notification_email']);
        $sanitized['exclude_categories'] = isset($input['exclude_categories']) ? array_map('absint', $input['exclude_categories']) : array();
        $sanitized['exclude_post_ids'] = sanitize_text_field($input['exclude_post_ids']);

        // 新增文章設定
        $sanitized['enable_new_posts'] = isset($input['enable_new_posts']) ? true : false;
        $sanitized['new_posts_per_day'] = absint($input['new_posts_per_day'] ?? 1);
        $sanitized['new_post_topics'] = sanitize_textarea_field($input['new_post_topics'] ?? '');
        $sanitized['new_post_category'] = absint($input['new_post_category'] ?? 0);
        $sanitized['new_post_status'] = sanitize_text_field($input['new_post_status'] ?? 'draft');

        return $sanitized;
    }

    /**
     * 載入管理員資源
     */
    public function enqueue_admin_assets($hook)
    {
        if ('settings_page_gasker-content-refresher' !== $hook) {
            return;
        }

        wp_enqueue_style(
            'gcr-admin-styles',
            GCR_PLUGIN_URL . 'assets/css/admin.css',
            array(),
            GCR_VERSION
        );

        wp_enqueue_script(
            'gcr-admin-scripts',
            GCR_PLUGIN_URL . 'assets/js/admin.js',
            array('jquery'),
            GCR_VERSION,
            true
        );

        wp_localize_script('gcr-admin-scripts', 'gcrAjax', array(
            'ajax_url' => admin_url('admin-ajax.php'),
            'nonce' => wp_create_nonce('gcr_ajax_nonce'),
            'strings' => array(
                'running' => __('執行中...', 'gasker-content-refresher'),
                'generating' => __('生成中...', 'gasker-content-refresher'),
                'success' => __('成功完成!', 'gasker-content-refresher'),
                'error' => __('發生錯誤', 'gasker-content-refresher'),
                'confirm_clear' => __('確定要清除所有日誌嗎?', 'gasker-content-refresher'),
            )
        ));
    }

    /**
     * 渲染管理員頁面
     */
    public function render_admin_page()
    {
        if (!current_user_can('manage_options')) {
            wp_die(__('您沒有權限訪問此頁面', 'gasker-content-refresher'));
        }

        require_once GCR_PLUGIN_DIR . 'includes/admin-page.php';
    }

    /**
     * AJAX: 立即執行
     */
    public function ajax_run_now()
    {
        check_ajax_referer('gcr_ajax_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('權限不足', 'gasker-content-refresher')));
        }

        try {
            // 記錄開始執行
            $this->debug_log('=== 開始執行手動改寫任務 ===');

            // 先測試 AI Engine 連線
            $this->debug_log('測試 AI Engine 連線...');
            if (!$this->test_ai_engine()) {
                $this->debug_log('AI Engine 連線測試失敗');
                wp_send_json_error(array(
                    'message' => 'AI Engine 連線失敗,請檢查 API Key 設定'
                ));
                return;
            }
            $this->debug_log('AI Engine 連線測試通過');

            // 設定 PHP 執行時間和記憶體限制
            set_time_limit(600); // 10 分鐘
            ini_set('memory_limit', '512M');

            $result = $this->process_old_posts();

            // 記錄執行結果
            $this->debug_log('執行完成: ' . json_encode($result, JSON_UNESCAPED_UNICODE));

            wp_send_json_success($result);
        } catch (Exception $e) {
            // 記錄錯誤
            $this->debug_log('AJAX 執行錯誤: ' . $e->getMessage());
            $this->debug_log('錯誤堆疊: ' . $e->getTraceAsString());

            wp_send_json_error(array(
                'message' => '執行失敗: ' . $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ));
        } catch (Error $e) {
            // 捕獲 PHP 致命錯誤
            $this->debug_log('PHP 錯誤: ' . $e->getMessage());
            $this->debug_log('錯誤檔案: ' . $e->getFile() . ':' . $e->getLine());

            wp_send_json_error(array(
                'message' => 'PHP 錯誤: ' . $e->getMessage()
            ));
        }
    }

    /**
     * AJAX: 清除日誌
     */
    public function ajax_clear_logs()
    {
        check_ajax_referer('gcr_ajax_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('權限不足', 'gasker-content-refresher')));
        }

        update_option(self::LOG_OPTION_NAME, array());

        wp_send_json_success(array('message' => __('日誌已清除', 'gasker-content-refresher')));
    }

    /**
     * AJAX: 清除除錯日誌
     */
    public function ajax_clear_debug_logs()
    {
        check_ajax_referer('gcr_ajax_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('權限不足', 'gasker-content-refresher')));
        }

        self::clear_debug_logs();

        wp_send_json_success(array('message' => __('除錯日誌已清除', 'gasker-content-refresher')));
    }

    /**
     * AJAX: 立即生成新文章
     */
    public function ajax_generate_now()
    {
        check_ajax_referer('gcr_ajax_nonce', 'nonce');

        if (!current_user_can('manage_options')) {
            wp_send_json_error(array('message' => __('權限不足', 'gasker-content-refresher')));
        }

        try {
            $this->debug_log('=== 開始執行手動生成新文章任務 ===');

            $this->debug_log('測試 AI Engine 連線...');
            if (!$this->test_ai_engine()) {
                $this->debug_log('AI Engine 連線測試失敗');
                wp_send_json_error(array(
                    'message' => 'AI Engine 連線失敗,請檢查 API Key 設定'
                ));
                return;
            }
            $this->debug_log('AI Engine 連線測試通過');

            set_time_limit(600);
            ini_set('memory_limit', '512M');

            $result = $this->generate_new_posts();

            $this->debug_log('生成完成: ' . json_encode($result, JSON_UNESCAPED_UNICODE));

            wp_send_json_success($result);
        } catch (Exception $e) {
            $this->debug_log('AJAX 生成錯誤: ' . $e->getMessage());
            wp_send_json_error(array(
                'message' => '執行失敗: ' . $e->getMessage()
            ));
        } catch (Error $e) {
            $this->debug_log('PHP 錯誤: ' . $e->getMessage());
            wp_send_json_error(array(
                'message' => 'PHP 錯誤: ' . $e->getMessage()
            ));
        }
    }

    /**
     * 核心功能: 生成全新文章
     */
    public function generate_new_posts()
    {
        $this->debug_log('--- 開始生成新文章 ---');

        $settings = get_option(self::OPTION_NAME);

        // 檢查是否啟用新文章功能
        $enable = $settings['enable_new_posts'] ?? false;
        if (!$enable) {
            $this->debug_log('新增文章功能未啟用');
            return array(
                'total' => 0,
                'success' => 0,
                'failed' => 0,
                'skipped' => 0,
                'posts' => array(),
                'type' => 'generate',
            );
        }

        $count = $settings['new_posts_per_day'] ?? 1;
        $topics_raw = $settings['new_post_topics'] ?? '';
        $category_id = $settings['new_post_category'] ?? 0;
        $post_status = $settings['new_post_status'] ?? 'draft';
        $ai_model = $settings['ai_model'] ?? 'gpt-4o';
        $language = $settings['language'] ?? 'zh-TW';

        // 解析題目清單
        $topics = array_filter(array_map('trim', explode("\n", $topics_raw)));
        if (empty($topics)) {
            $this->debug_log('警告: 沒有設定任何題目');
            return array(
                'total' => 0,
                'success' => 0,
                'failed' => 0,
                'skipped' => 0,
                'posts' => array(),
                'type' => 'generate',
            );
        }

        // 取得已使用過的題目 (避免重複)
        $used_topics = get_option('gcr_used_topics', array());

        // 從題目清單中挑選未使用過的
        $available_topics = array_diff($topics, $used_topics);
        if (empty($available_topics)) {
            // 所有題目都用過了，重置
            $this->debug_log('所有題目已使用完畢，重置題目池');
            $used_topics = array();
            $available_topics = $topics;
        }

        $selected_topics = array_slice(array_values($available_topics), 0, $count);
        $this->debug_log('本次選取 ' . count($selected_topics) . ' 個題目');

        $results = array(
            'total' => count($selected_topics),
            'success' => 0,
            'failed' => 0,
            'skipped' => 0,
            'posts' => array(),
            'type' => 'generate',
        );

        foreach ($selected_topics as $topic) {
            $this->debug_log('開始生成文章: ' . $topic);

            $result = array(
                'post_id' => 0,
                'post_title' => $topic,
                'status' => 'failed',
                'message' => '',
                'tokens_used' => 0,
            );

            try {
                // 構建新文章 prompt
                $prompt = $this->build_new_post_prompt($topic, $settings);
                $this->debug_log('  Prompt 長度: ' . mb_strlen($prompt) . ' 字');

                // 呼叫 AI Engine
                $this->debug_log('  呼叫 AI Engine (模型: ' . $ai_model . ')...');
                $ai_result = $this->call_ai_engine($prompt, $ai_model);

                if (!$ai_result['success']) {
                    $result['message'] = 'AI Engine 錯誤: ' . $ai_result['error'];
                    $this->debug_log('  AI Engine 呼叫失敗: ' . $ai_result['error']);
                    $results['failed']++;
                    $results['posts'][] = $result;
                    continue;
                }

                $this->debug_log('  AI Engine 回應成功');
                $result['tokens_used'] = $ai_result['tokens_used'];

                $content = $ai_result['content'];

                // 驗證新文章內容
                if (empty($content) || mb_strlen(strip_tags($content)) < 200) {
                    $result['message'] = __('AI 生成內容過短,已跳過', 'gasker-content-refresher');
                    $this->debug_log('  跳過: 內容過短');
                    $results['skipped']++;
                    $results['posts'][] = $result;
                    continue;
                }

                // 建立新文章
                $post_data = array(
                    'post_title'   => $topic,
                    'post_content' => $content,
                    'post_status'  => $post_status,
                    'post_type'    => 'post',
                    'post_author'  => get_current_user_id() ?: 1,
                );

                if ($category_id > 0) {
                    $post_data['post_category'] = array($category_id);
                }

                $new_post_id = wp_insert_post($post_data, true);

                if (is_wp_error($new_post_id)) {
                    $result['message'] = __('建立文章失敗: ', 'gasker-content-refresher') . $new_post_id->get_error_message();
                    $this->debug_log('  建立失敗: ' . $new_post_id->get_error_message());
                    $results['failed']++;
                } else {
                    $result['post_id'] = $new_post_id;
                    $result['status'] = 'success';
                    $result['message'] = __('成功生成新文章', 'gasker-content-refresher');

                    // 記錄元資料
                    update_post_meta($new_post_id, '_gcr_generated', current_time('mysql'));
                    update_post_meta($new_post_id, '_gcr_topic', $topic);

                    // 標記已使用的題目
                    $used_topics[] = $topic;

                    $this->debug_log('  文章建立成功! ID: ' . $new_post_id);
                    $results['success']++;
                }

            } catch (Exception $e) {
                $result['message'] = '異常錯誤: ' . $e->getMessage();
                $this->debug_log('  捕獲異常: ' . $e->getMessage());
                $results['failed']++;
            }

            $results['posts'][] = $result;
        }

        // 更新已使用題目
        update_option('gcr_used_topics', $used_topics);

        // 記錄日誌
        $this->log_execution($results);

        // 發送通知
        if ($settings['enable_email_notification'] ?? false) {
            $this->send_notification_email($results);
        }

        $this->debug_log('--- 新文章生成完成 ---');
        $this->debug_log('總計: ' . $results['total'] . ', 成功: ' . $results['success'] . ', 失敗: ' . $results['failed'] . ', 跳過: ' . $results['skipped']);

        return $results;
    }

    /**
     * 構建新文章的 AI Prompt (遵循 GEO 黃金骨架)
     */
    private function build_new_post_prompt($topic, $settings)
    {
        $language = $settings['language'] ?? 'zh-TW';
        $language_map = array(
            'zh-TW' => '繁體中文',
            'zh-CN' => '简体中文',
            'en' => 'English',
        );
        $language_name = $language_map[$language] ?? '繁體中文';

        $prompt = <<<PROMPT
你是一位專業的 SEO/AEO 內容撰寫專家。請根據以下題目撰寫一篇完整的、高品質的部落格文章。

**題目:** {$topic}

**語言:** {$language_name}

**文章結構要求 (嚴格遵循):**

1. **導言** (1 段, 5-7 行)
   - 第一句必須是可被 AI 直接引用的摘要答案
   - 包含: 主題 → 關鍵優勢 → 讀者痛點 → 本文承諾 → 專家視角

2. **H2-1: 核心概念** (原因 → 結果)
   - 第一行直接回答「為什麼這很重要？」
   - 包含 2-3 個 H3 小節,每節 3 個要點

3. **H2-2: 實際應用** (條件 → 結果)
   - 第一行可被 AI 直接生成為知識回答
   - 包含具體條件和實踐方法

4. **H2-3: 執行步驟** (方法 → 結果)
   - 2-3 個具體方法類別
   - 包含一個比較表格: | 類別 | 條件 | 做法 | 優點 |

5. **H2-4: 注意事項與風險** (管理 → 安心)
   - 安全/品質相關建議 (至少 3 點)

6. **結論** (1 段)
   - 壓縮前面核心價值 + 行動呼籲

7. **FAQ** (3 題)
   - 問句 → 直接答案 (每題不超過 4 行)

**寫作規則:**
- 每個段落語義自足,可被 AI 獨立引用
- 不可出現「本文將介紹」等空泛語句
- 不可一次段落談多個重點
- 使用具體數據和案例,避免空泛形容
- 內容長度至少 1500 字
- 直接輸出完整 HTML 內容 (使用 h2, h3, p, ul, ol, li, table, strong 等標籤)
- 不要有 Markdown 標記或說明文字
- 不要包含 h1 標籤 (WordPress 會自動處理標題)

**請直接輸出完整的 HTML 文章內容:**
PROMPT;

        return $prompt;
    }

    /**
     * 核心功能: 處理舊文章
     */
    public function process_old_posts()
    {
        $this->debug_log('--- 開始處理舊文章 ---');

        $settings = get_option(self::OPTION_NAME);
        $this->debug_log('載入設定: ' . json_encode($settings, JSON_UNESCAPED_UNICODE));

        $posts_per_day = $settings['posts_per_day'] ?? 10;
        $cooldown_days = $settings['cooldown_days'] ?? 30;
        $exclude_categories = $settings['exclude_categories'] ?? array();
        $exclude_post_ids = $settings['exclude_post_ids'] ?? '';

        // 解析排除的文章 ID
        $exclude_ids = array();
        if (!empty($exclude_post_ids)) {
            $exclude_ids = array_map('intval', array_filter(array_map('trim', explode(',', $exclude_post_ids))));
        }

        // 查詢參數
        $args = array(
            'post_type' => 'post',
            'post_status' => 'publish',
            'posts_per_page' => $posts_per_day,
            'orderby' => 'modified',
            'order' => 'ASC',
            'date_query' => array(
                array(
                    'column' => 'post_modified_gmt',
                    'before' => $cooldown_days . ' days ago',
                ),
            ),
        );

        // 排除分類
        if (!empty($exclude_categories)) {
            $args['category__not_in'] = $exclude_categories;
        }

        // 排除文章 ID
        if (!empty($exclude_ids)) {
            $args['post__not_in'] = $exclude_ids;
        }

        $this->debug_log('查詢參數: ' . json_encode($args, JSON_UNESCAPED_UNICODE));

        $old_posts = get_posts($args);
        $this->debug_log('找到 ' . count($old_posts) . ' 篇符合條件的文章');

        if (empty($old_posts)) {
            $this->debug_log('警告: 沒有找到符合條件的文章');
        }

        $results = array(
            'total' => count($old_posts),
            'success' => 0,
            'failed' => 0,
            'skipped' => 0,
            'posts' => array(),
        );

        foreach ($old_posts as $post) {
            $this->debug_log('開始處理文章 ID: ' . $post->ID . ' - ' . $post->post_title);

            $result = $this->rewrite_single_post($post);

            $this->debug_log('文章 ID ' . $post->ID . ' 處理結果: ' . $result['status'] . ' - ' . $result['message']);

            if ($result['status'] === 'success') {
                $results['success']++;
            } elseif ($result['status'] === 'skipped') {
                $results['skipped']++;
            } else {
                $results['failed']++;
            }

            $results['posts'][] = $result;
        }

        // 記錄日誌
        $this->log_execution($results);

        // 發送通知郵件
        if ($settings['enable_email_notification'] ?? false) {
            $this->send_notification_email($results);
        }

        $this->debug_log('--- 處理完成 ---');
        $this->debug_log('總計: ' . $results['total'] . ', 成功: ' . $results['success'] . ', 失敗: ' . $results['failed'] . ', 跳過: ' . $results['skipped']);

        return $results;
    }

    /**
     * 改寫單篇文章
     */
    private function rewrite_single_post($post)
    {
        $settings = get_option(self::OPTION_NAME);
        $max_length = $settings['max_post_length'] ?? 5000;

        $result = array(
            'post_id' => $post->ID,
            'post_title' => $post->post_title,
            'status' => 'failed',
            'message' => '',
            'tokens_used' => 0,
        );

        // 檢查文章長度
        $content_length = mb_strlen(strip_tags($post->post_content));
        $this->debug_log('  文章長度: ' . $content_length . ' 字 (上限: ' . $max_length . ')');

        if ($content_length > $max_length) {
            $result['status'] = 'skipped';
            $result['message'] = sprintf(__('文章過長 (%d 字), 已跳過', 'gasker-content-refresher'), $content_length);
            $this->debug_log('  跳過: 文章過長');
            return $result;
        }

        // 檢查 AI Engine 是否啟用
        $this->debug_log('  檢查 AI Engine 狀態...');
        if (!class_exists('Meow_MWAI_Core')) {
            $result['message'] = __('AI Engine 插件未啟用', 'gasker-content-refresher');
            $this->debug_log('  錯誤: AI Engine 未啟用');
            return $result;
        }
        $this->debug_log('  AI Engine 已啟用');

        try {
            // 準備 Prompt
            $this->debug_log('  構建 Prompt...');
            $prompt = $this->build_prompt($post->post_content, $settings);
            $this->debug_log('  Prompt 長度: ' . mb_strlen($prompt) . ' 字');

            // 呼叫 AI Engine
            $ai_model = $settings['ai_model'] ?? 'gpt-4o';
            $this->debug_log('  呼叫 AI Engine (模型: ' . $ai_model . ')...');

            $ai_result = $this->call_ai_engine($prompt, $ai_model);

            if (!$ai_result['success']) {
                $result['message'] = 'AI Engine 錯誤: ' . $ai_result['error'];
                $this->debug_log('  AI Engine 呼叫失敗: ' . $ai_result['error']);
                return $result;
            }

            $this->debug_log('  AI Engine 回應成功,Token 使用: ' . ($ai_result['tokens_used'] ?? 0));

            $new_content = $ai_result['content'];
            $result['tokens_used'] = $ai_result['tokens_used'];

            // 安全驗證
            $this->debug_log('  驗證內容安全性...');
            $validation_result = $this->validate_content($post->post_content, $new_content);

            if (!$validation_result) {
                $result['message'] = __('內容驗證失敗,未更新', 'gasker-content-refresher');
                $this->debug_log('  驗證失敗: 內容不符合安全標準');
                return $result;
            }
            $this->debug_log('  內容驗證通過');

            // 更新文章
            $auto_publish = $settings['auto_publish'] ?? false;
            $this->debug_log('  更新文章 (自動發布: ' . ($auto_publish ? '是' : '否') . ')...');

            $update_result = $this->update_post($post->ID, $new_content, $auto_publish);

            if ($update_result) {
                $result['status'] = 'success';
                $result['message'] = __('成功改寫', 'gasker-content-refresher');
                $this->debug_log('  文章更新成功');
            } else {
                $result['message'] = __('更新文章失敗', 'gasker-content-refresher');
                $this->debug_log('  錯誤: 文章更新失敗');
            }

        } catch (Exception $e) {
            $result['message'] = '異常錯誤: ' . $e->getMessage();
            $this->debug_log('  捕獲異常: ' . $e->getMessage());
            $this->debug_log('  堆疊追蹤: ' . $e->getTraceAsString());
        }

        return $result;
    }

    /**
     * 構建 AI Prompt
     */
    private function build_prompt($content, $settings)
    {
        $language = $settings['language'] ?? 'zh-TW';
        $language_map = array(
            'zh-TW' => '繁體中文',
            'zh-CN' => '简体中文',
            'en' => 'English',
        );
        $language_name = $language_map[$language] ?? '繁體中文';

        $prompt = <<<PROMPT
你是一位專業的 SEO 內容編輯。請重寫以下 HTML 內容。

**嚴格規則:**
1. 必須保持原有的所有 HTML 標籤結構 (h1, h2, h3, h4, p, ul, ol, li, img, a 等)
2. 絕對不可改變或刪除任何圖片連結 (<img> 標籤的 src 屬性必須完整保留)
3. 保留所有連結 (<a> 標籤的 href 屬性)
4. 用更現代、專業的語氣潤飾文字內容
5. 修正任何過時的資訊或表達方式
6. 使用 {$language_name} 語言
7. 不要新增未經證實的數據或資訊
8. 僅潤飾語氣和表達方式,不要大幅改變原文意思
9. 直接回傳完整的 HTML 內容,不要有 Markdown 標記或說明文字
10. 回傳的內容長度應與原文相近 (不可少於原文的 70%)

**原始內容:**
{$content}

**請直接輸出重寫後的完整 HTML 內容:**
PROMPT;

        return $prompt;
    }

    /**
     * 呼叫 AI Engine
     */
    private function call_ai_engine($prompt, $model)
    {
        $this->debug_log('    AI Engine 呼叫開始...');
        $this->debug_log('    模型: ' . $model);

        try {
            // 檢查類別是否存在
            if (!class_exists('Meow_MWAI_Core')) {
                throw new Exception('Meow_MWAI_Core 類別不存在');
            }

            if (!class_exists('Meow_MWAI_Query_Text')) {
                throw new Exception('Meow_MWAI_Query_Text 類別不存在');
            }

            // 檢查 AI Engine 設定
            $this->debug_log('    檢查 AI Engine 設定...');
            $ai_settings = get_option('mwai_options');
            if (empty($ai_settings)) {
                $this->debug_log('    警告: AI Engine 設定為空');
            } else {
                $this->debug_log('    AI Engine 設定已載入');
            }

            $this->debug_log('    創建查詢物件...');
            $query = new Meow_MWAI_Query_Text($prompt);

            // 設定 environment (新版 AI Engine 要求)
            $this->debug_log('    設定 environment...');
            if (method_exists($query, 'set_env')) {
                $query->set_env('gasker-content-refresher');
                $this->debug_log('    environment 已設定');
            }

            $this->debug_log('    設定模型: ' . $model);
            $query->set_model($model);

            $this->debug_log('    設定 max_tokens: 4000');
            $query->set_max_tokens(4000);

            $this->debug_log('    執行查詢...');
            $this->debug_log('    [重要] 正在呼叫 OpenAI API,請稍候...');

            // 設定 PHP 執行時間限制
            set_time_limit(300); // 5 分鐘

            // 使用全域函數執行查詢
            global $mwai_core;
            if (!$mwai_core) {
                throw new Exception('AI Engine 未正確初始化');
            }

            $start_time = microtime(true);
            $reply = $mwai_core->run_query($query);
            $execution_time = microtime(true) - $start_time;

            $this->debug_log('    API 呼叫完成,耗時: ' . round($execution_time, 2) . ' 秒');

            if (!$reply) {
                throw new Exception('AI Engine 沒有回傳結果');
            }

            if (empty($reply->result)) {
                throw new Exception('AI Engine 回傳空白內容');
            }

            $this->debug_log('    查詢成功');
            $this->debug_log('    回應長度: ' . mb_strlen($reply->result) . ' 字');
            $this->debug_log('    Token 使用: ' . $reply->get_total_tokens());

            return array(
                'success' => true,
                'content' => $reply->result,
                'tokens_used' => $reply->get_total_tokens(),
            );

        } catch (Exception $e) {
            $this->debug_log('    AI Engine 錯誤: ' . $e->getMessage());
            $this->debug_log('    錯誤堆疊: ' . $e->getTraceAsString());

            return array(
                'success' => false,
                'error' => $e->getMessage(),
            );
        }
    }

    /**
     * 驗證內容安全性
     */
    private function validate_content($original, $new)
    {
        // 檢查新內容是否為空
        if (empty($new) || strlen($new) < 100) {
            return false;
        }

        // 檢查長度 (新內容不應少於原內容的 50%)
        $original_length = strlen($original);
        $new_length = strlen($new);

        if ($new_length < ($original_length * 0.5)) {
            return false;
        }

        // 檢查圖片數量 (新內容的圖片不應少於原內容)
        $original_img_count = substr_count($original, '<img');
        $new_img_count = substr_count($new, '<img');

        if ($new_img_count < $original_img_count) {
            return false;
        }

        // 檢查 HTML 標籤是否平衡
        $tags_to_check = array('h2', 'h3', 'ul', 'ol', 'p');
        foreach ($tags_to_check as $tag) {
            $original_count = substr_count($original, "<{$tag}");
            $new_count = substr_count($new, "<{$tag}");

            // 允許少量差異 (±20%)
            if ($new_count < ($original_count * 0.8)) {
                return false;
            }
        }

        return true;
    }

    /**
     * 更新文章
     */
    private function update_post($post_id, $new_content, $auto_publish)
    {
        $update_data = array(
            'ID' => $post_id,
            'post_content' => $new_content,
        );

        // 根據設定決定是否自動發布
        if (!$auto_publish) {
            $update_data['post_status'] = 'pending';
        }

        $result = wp_update_post($update_data, true);

        if (is_wp_error($result)) {
            return false;
        }

        // 更新 post_modified 時間 (wp_update_post 會自動更新)
        // 添加自訂欄位記錄改寫時間
        update_post_meta($post_id, '_gcr_last_rewrite', current_time('mysql'));

        return true;
    }

    /**
     * 記錄執行日誌
     */
    private function log_execution($results)
    {
        $logs = get_option(self::LOG_OPTION_NAME, array());

        $log_entry = array(
            'timestamp' => current_time('mysql'),
            'type' => $results['type'] ?? 'rewrite',
            'total' => $results['total'],
            'success' => $results['success'],
            'failed' => $results['failed'],
            'skipped' => $results['skipped'],
            'posts' => $results['posts'],
        );

        // 保留最近 50 筆記錄
        array_unshift($logs, $log_entry);
        $logs = array_slice($logs, 0, 50);

        update_option(self::LOG_OPTION_NAME, $logs);
    }

    /**
     * 測試 AI Engine 連線
     */
    private function test_ai_engine()
    {
        try {
            // 檢查 AI Engine 類別
            if (!class_exists('Meow_MWAI_Query_Text')) {
                $this->debug_log('  測試失敗: AI Engine 未安裝或版本不相容');
                return false;
            }

            // 嘗試創建測試查詢物件
            $test_query = new Meow_MWAI_Query_Text('測試');
            if (!$test_query) {
                $this->debug_log('  測試失敗: 無法創建查詢物件');
                return false;
            }

            $this->debug_log('  測試通過: AI Engine 可正常使用');
            return true;

        } catch (Exception $e) {
            $this->debug_log('  測試失敗: ' . $e->getMessage());
            return false;
        } catch (Error $e) {
            $this->debug_log('  測試失敗 (PHP Error): ' . $e->getMessage());
            return false;
        }
    }

    /**
     * 發送通知郵件
     */
    private function send_notification_email($results)
    {
        $settings = get_option(self::OPTION_NAME);
        $to = $settings['notification_email'] ?? get_option('admin_email');

        $subject = sprintf(
            __('[%s] 內容更新報告 - %s', 'gasker-content-refresher'),
            get_bloginfo('name'),
            date('Y-m-d')
        );

        $message = sprintf(
            __("今日內容更新摘要:\n\n總計: %d 篇\n成功: %d 篇\n失敗: %d 篇\n跳過: %d 篇\n\n詳細資訊請至後台查看。", 'gasker-content-refresher'),
            $results['total'],
            $results['success'],
            $results['failed'],
            $results['skipped']
        );

        wp_mail($to, $subject, $message);
    }

    /**
     * 獲取日誌
     */
    public static function get_logs($limit = 50)
    {
        $logs = get_option(self::LOG_OPTION_NAME, array());
        return array_slice($logs, 0, $limit);
    }

    /**
     * 除錯日誌記錄
     */
    private function debug_log($message)
    {
        // 如果啟用 WP_DEBUG_LOG,寫入 debug.log
        if (defined('WP_DEBUG') && WP_DEBUG && defined('WP_DEBUG_LOG') && WP_DEBUG_LOG) {
            error_log('[GCR] ' . $message);
        }

        // 同時儲存到選項中供前端查看
        $debug_logs = get_option('gcr_debug_logs', array());

        // 保留最近 100 筆
        if (count($debug_logs) >= 100) {
            $debug_logs = array_slice($debug_logs, -99);
        }

        $debug_logs[] = array(
            'time' => current_time('mysql'),
            'message' => $message
        );

        update_option('gcr_debug_logs', $debug_logs);
    }

    /**
     * 清除除錯日誌
     */
    public static function clear_debug_logs()
    {
        delete_option('gcr_debug_logs');
    }

    /**
     * 獲取除錯日誌
     */
    public static function get_debug_logs($limit = 100)
    {
        $logs = get_option('gcr_debug_logs', array());
        return array_slice($logs, -$limit);
    }
}

// 初始化插件
function gcr_init()
{
    return Gasker_Content_Refresher::get_instance();
}

// 啟動插件
add_action('plugins_loaded', 'gcr_init');
