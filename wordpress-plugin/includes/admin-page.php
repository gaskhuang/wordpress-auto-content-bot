<?php
/**
 * 管理員設定頁面
 */

if (!defined('ABSPATH')) {
    exit;
}

$settings = get_option(Gasker_Content_Refresher::OPTION_NAME);
$logs = Gasker_Content_Refresher::get_logs(20);

// 獲取所有分類
$categories = get_categories(array('hide_empty' => false));

// 檢查 AI Engine 狀態
$ai_engine_active = class_exists('Meow_MWAI_Core');
$next_scheduled = wp_next_scheduled(Gasker_Content_Refresher::CRON_HOOK);
?>

<div class="wrap gcr-admin-wrap">
    <h1><?php echo esc_html(get_admin_page_title()); ?></h1>

    <?php if (!$ai_engine_active): ?>
        <div class="notice notice-error">
            <p>
                <strong><?php _e('警告:', 'gasker-content-refresher'); ?></strong>
                <?php _e('需要安裝並啟用 AI Engine 插件才能使用此功能。', 'gasker-content-refresher'); ?>
                <a href="<?php echo admin_url('plugin-install.php?s=AI%20Engine&tab=search&type=term'); ?>" target="_blank">
                    <?php _e('立即安裝', 'gasker-content-refresher'); ?>
                </a>
            </p>
        </div>
    <?php endif; ?>

    <?php settings_errors(); ?>

    <div class="gcr-admin-container">
        <!-- 左側設定面板 -->
        <div class="gcr-settings-panel">
            <form method="post" action="options.php">
                <?php
                settings_fields('gcr_settings_group');
                ?>

                <!-- 基本設定 -->
                <div class="gcr-section">
                    <h2><?php _e('基本設定', 'gasker-content-refresher'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label for="posts_per_day">
                                    <?php _e('每日處理篇數', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <input type="number"
                                       id="posts_per_day"
                                       name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[posts_per_day]"
                                       value="<?php echo esc_attr($settings['posts_per_day'] ?? 10); ?>"
                                       min="1"
                                       max="50"
                                       class="small-text">
                                <p class="description">
                                    <?php _e('每天自動改寫的文章數量 (建議 5-10 篇)', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="cooldown_days">
                                    <?php _e('冷卻天數', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <input type="number"
                                       id="cooldown_days"
                                       name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[cooldown_days]"
                                       value="<?php echo esc_attr($settings['cooldown_days'] ?? 30); ?>"
                                       min="7"
                                       max="365"
                                       class="small-text">
                                <p class="description">
                                    <?php _e('只處理 N 天前未更新過的文章', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="max_post_length">
                                    <?php _e('最大文章長度', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <input type="number"
                                       id="max_post_length"
                                       name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[max_post_length]"
                                       value="<?php echo esc_attr($settings['max_post_length'] ?? 5000); ?>"
                                       min="1000"
                                       max="20000"
                                       class="small-text">
                                <p class="description">
                                    <?php _e('超過此字數的文章將被跳過 (避免 Token 消耗過大)', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- AI 設定 -->
                <div class="gcr-section">
                    <h2><?php _e('AI 模型設定', 'gasker-content-refresher'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label for="ai_model">
                                    <?php _e('AI 模型', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <select id="ai_model"
                                        name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[ai_model]">
                                    <option value="gpt-4o" <?php selected($settings['ai_model'] ?? 'gpt-4o', 'gpt-4o'); ?>>
                                        GPT-4o (推薦)
                                    </option>
                                    <option value="gpt-4o-mini" <?php selected($settings['ai_model'] ?? '', 'gpt-4o-mini'); ?>>
                                        GPT-4o Mini (經濟型)
                                    </option>
                                    <option value="gemini-1.5-pro" <?php selected($settings['ai_model'] ?? '', 'gemini-1.5-pro'); ?>>
                                        Gemini 1.5 Pro
                                    </option>
                                </select>
                                <p class="description">
                                    <?php _e('建議使用 GPT-4o 以確保 HTML 結構穩定性', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="language">
                                    <?php _e('目標語言', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <select id="language"
                                        name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[language]">
                                    <option value="zh-TW" <?php selected($settings['language'] ?? 'zh-TW', 'zh-TW'); ?>>
                                        繁體中文
                                    </option>
                                    <option value="zh-CN" <?php selected($settings['language'] ?? '', 'zh-CN'); ?>>
                                        简体中文
                                    </option>
                                    <option value="en" <?php selected($settings['language'] ?? '', 'en'); ?>>
                                        English
                                    </option>
                                </select>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- 發布模式 -->
                <div class="gcr-section">
                    <h2><?php _e('發布模式', 'gasker-content-refresher'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <?php _e('審核模式', 'gasker-content-refresher'); ?>
                            </th>
                            <td>
                                <fieldset>
                                    <label>
                                        <input type="radio"
                                               name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[auto_publish]"
                                               value="1"
                                               <?php checked($settings['auto_publish'] ?? false, true); ?>>
                                        <?php _e('自動發布 (直接更新已發布文章)', 'gasker-content-refresher'); ?>
                                    </label>
                                    <br>
                                    <label>
                                        <input type="radio"
                                               name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[auto_publish]"
                                               value="0"
                                               <?php checked($settings['auto_publish'] ?? false, false); ?>>
                                        <?php _e('待審閱 (改寫後設為待審狀態) - 推薦', 'gasker-content-refresher'); ?>
                                    </label>
                                    <p class="description">
                                        <?php _e('初期建議使用「待審閱」模式,確認幾天沒問題後再改為自動發布', 'gasker-content-refresher'); ?>
                                    </p>
                                </fieldset>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- 排除設定 -->
                <div class="gcr-section">
                    <h2><?php _e('排除設定', 'gasker-content-refresher'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <label for="exclude_categories">
                                    <?php _e('排除分類', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <select id="exclude_categories"
                                        name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[exclude_categories][]"
                                        multiple
                                        size="5"
                                        style="width: 300px;">
                                    <?php foreach ($categories as $category): ?>
                                        <option value="<?php echo esc_attr($category->term_id); ?>"
                                                <?php selected(in_array($category->term_id, $settings['exclude_categories'] ?? array())); ?>>
                                            <?php echo esc_html($category->name); ?>
                                        </option>
                                    <?php endforeach; ?>
                                </select>
                                <p class="description">
                                    <?php _e('選擇不應被自動改寫的分類 (例如:公司簡介、隱私條款等)', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="exclude_post_ids">
                                    <?php _e('排除文章 ID', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <input type="text"
                                       id="exclude_post_ids"
                                       name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[exclude_post_ids]"
                                       value="<?php echo esc_attr($settings['exclude_post_ids'] ?? ''); ?>"
                                       class="regular-text">
                                <p class="description">
                                    <?php _e('輸入文章 ID,用逗號分隔 (例如: 1, 5, 12)', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- AI 新增文章設定 -->
                <div class="gcr-section">
                    <h2><?php _e('AI 新增文章', 'gasker-content-refresher'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <?php _e('啟用功能', 'gasker-content-refresher'); ?>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox"
                                           name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[enable_new_posts]"
                                           value="1"
                                           <?php checked($settings['enable_new_posts'] ?? false, true); ?>>
                                    <?php _e('啟用 AI 自動生成新文章', 'gasker-content-refresher'); ?>
                                </label>
                                <p class="description">
                                    <?php _e('開啟後,系統會每天根據題目清單自動生成全新文章', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="new_posts_per_day">
                                    <?php _e('每日生成篇數', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <input type="number"
                                       id="new_posts_per_day"
                                       name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[new_posts_per_day]"
                                       value="<?php echo esc_attr($settings['new_posts_per_day'] ?? 1); ?>"
                                       min="1"
                                       max="10"
                                       class="small-text">
                                <p class="description">
                                    <?php _e('每天自動生成的新文章數量 (建議 1-3 篇,避免 Token 消耗過大)', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="new_post_topics">
                                    <?php _e('題目清單', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <textarea id="new_post_topics"
                                          name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[new_post_topics]"
                                          rows="8"
                                          class="large-text"
                                          placeholder="<?php _e("每行一個題目,例如:\nAI 自動化工作流入門指南\nn8n 與 WordPress 整合實戰\nSEO 2026 最新趨勢分析", 'gasker-content-refresher'); ?>"
                                          ><?php echo esc_textarea($settings['new_post_topics'] ?? ''); ?></textarea>
                                <p class="description">
                                    <?php
                                    $used_count = count(get_option('gcr_used_topics', array()));
                                    $total_count = count(array_filter(array_map('trim', explode("\n", $settings['new_post_topics'] ?? ''))));
                                    printf(
                                        __('每行填入一個文章題目。系統會按順序使用,用完後自動重置。(已使用 %d / 共 %d 個)', 'gasker-content-refresher'),
                                        $used_count,
                                        $total_count
                                    );
                                    ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="new_post_category">
                                    <?php _e('目標分類', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <select id="new_post_category"
                                        name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[new_post_category]">
                                    <option value="0"><?php _e('-- 不指定 --', 'gasker-content-refresher'); ?></option>
                                    <?php foreach ($categories as $category): ?>
                                        <option value="<?php echo esc_attr($category->term_id); ?>"
                                                <?php selected($settings['new_post_category'] ?? 0, $category->term_id); ?>>
                                            <?php echo esc_html($category->name); ?>
                                        </option>
                                    <?php endforeach; ?>
                                </select>
                                <p class="description">
                                    <?php _e('新文章會自動歸入此分類', 'gasker-content-refresher'); ?>
                                </p>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <?php _e('新文章狀態', 'gasker-content-refresher'); ?>
                            </th>
                            <td>
                                <fieldset>
                                    <label>
                                        <input type="radio"
                                               name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[new_post_status]"
                                               value="draft"
                                               <?php checked($settings['new_post_status'] ?? 'draft', 'draft'); ?>>
                                        <?php _e('草稿 (需手動審核後發布) - 推薦', 'gasker-content-refresher'); ?>
                                    </label>
                                    <br>
                                    <label>
                                        <input type="radio"
                                               name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[new_post_status]"
                                               value="pending"
                                               <?php checked($settings['new_post_status'] ?? 'draft', 'pending'); ?>>
                                        <?php _e('待審閱', 'gasker-content-refresher'); ?>
                                    </label>
                                    <br>
                                    <label>
                                        <input type="radio"
                                               name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[new_post_status]"
                                               value="publish"
                                               <?php checked($settings['new_post_status'] ?? 'draft', 'publish'); ?>>
                                        <?php _e('直接發布', 'gasker-content-refresher'); ?>
                                    </label>
                                </fieldset>
                            </td>
                        </tr>
                    </table>
                </div>

                <!-- 通知設定 -->
                <div class="gcr-section">
                    <h2><?php _e('Email 通知', 'gasker-content-refresher'); ?></h2>

                    <table class="form-table">
                        <tr>
                            <th scope="row">
                                <?php _e('啟用通知', 'gasker-content-refresher'); ?>
                            </th>
                            <td>
                                <label>
                                    <input type="checkbox"
                                           name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[enable_email_notification]"
                                           value="1"
                                           <?php checked($settings['enable_email_notification'] ?? false, true); ?>>
                                    <?php _e('每日執行完畢後發送摘要郵件', 'gasker-content-refresher'); ?>
                                </label>
                            </td>
                        </tr>

                        <tr>
                            <th scope="row">
                                <label for="notification_email">
                                    <?php _e('通知信箱', 'gasker-content-refresher'); ?>
                                </label>
                            </th>
                            <td>
                                <input type="email"
                                       id="notification_email"
                                       name="<?php echo Gasker_Content_Refresher::OPTION_NAME; ?>[notification_email]"
                                       value="<?php echo esc_attr($settings['notification_email'] ?? get_option('admin_email')); ?>"
                                       class="regular-text">
                            </td>
                        </tr>
                    </table>
                </div>

                <?php submit_button(__('儲存設定', 'gasker-content-refresher')); ?>
            </form>
        </div>

        <!-- 右側操作與狀態面板 -->
        <div class="gcr-sidebar">
            <!-- 系統狀態 -->
            <div class="gcr-panel">
                <h3><?php _e('系統狀態', 'gasker-content-refresher'); ?></h3>
                <table class="gcr-status-table">
                    <tr>
                        <td><?php _e('AI Engine:', 'gasker-content-refresher'); ?></td>
                        <td>
                            <?php if ($ai_engine_active): ?>
                                <span class="gcr-status-active">✓ <?php _e('已啟用', 'gasker-content-refresher'); ?></span>
                            <?php else: ?>
                                <span class="gcr-status-inactive">✗ <?php _e('未啟用', 'gasker-content-refresher'); ?></span>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <tr>
                        <td><?php _e('排程狀態:', 'gasker-content-refresher'); ?></td>
                        <td>
                            <?php if ($next_scheduled): ?>
                                <span class="gcr-status-active">✓ <?php _e('已啟用', 'gasker-content-refresher'); ?></span>
                            <?php else: ?>
                                <span class="gcr-status-inactive">✗ <?php _e('未啟用', 'gasker-content-refresher'); ?></span>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <tr>
                        <td><?php _e('下次執行:', 'gasker-content-refresher'); ?></td>
                        <td>
                            <?php if ($next_scheduled): ?>
                                <?php echo date('Y-m-d H:i', $next_scheduled); ?>
                            <?php else: ?>
                                <?php _e('未排程', 'gasker-content-refresher'); ?>
                            <?php endif; ?>
                        </td>
                    </tr>
                    <tr>
                        <td><?php _e('AI Engine 設定:', 'gasker-content-refresher'); ?></td>
                        <td>
                            <?php
                            $ai_settings = get_option('mwai_options');
                            $has_openai_key = !empty($ai_settings['openai_api_key'] ?? '');
                            $has_google_key = !empty($ai_settings['google_api_key'] ?? '');
                            ?>
                            <?php if ($has_openai_key || $has_google_key): ?>
                                <span class="gcr-status-active">
                                    ✓ <?php echo $has_openai_key ? 'OpenAI' : 'Google'; ?> API Key 已設定
                                </span>
                            <?php else: ?>
                                <span class="gcr-status-inactive">✗ <?php _e('未設定 API Key', 'gasker-content-refresher'); ?></span>
                            <?php endif; ?>
                        </td>
                    </tr>
                </table>
            </div>

            <!-- 手動操作 -->
            <div class="gcr-panel">
                <h3><?php _e('手動操作', 'gasker-content-refresher'); ?></h3>

                <p class="gcr-action-label"><?php _e('改寫舊文章', 'gasker-content-refresher'); ?></p>
                <button type="button" class="button button-primary button-large gcr-run-now" style="width: 100%;">
                    <?php _e('立即改寫', 'gasker-content-refresher'); ?>
                </button>
                <p class="description" style="margin-bottom: 15px;">
                    <?php _e('立即改寫符合條件的舊文章', 'gasker-content-refresher'); ?>
                </p>

                <hr style="margin: 15px 0;">

                <p class="gcr-action-label"><?php _e('生成新文章', 'gasker-content-refresher'); ?></p>
                <button type="button" class="button button-large gcr-generate-now" style="width: 100%; background: #2e7d32; border-color: #1b5e20; color: #fff;">
                    <?php _e('立即生成', 'gasker-content-refresher'); ?>
                </button>
                <p class="description">
                    <?php _e('根據題目清單立即生成新文章', 'gasker-content-refresher'); ?>
                </p>
            </div>

            <!-- 使用提示 -->
            <div class="gcr-panel">
                <h3><?php _e('使用提示', 'gasker-content-refresher'); ?></h3>
                <ul class="gcr-tips">
                    <li><?php _e('初次使用請先設為「待審閱」模式', 'gasker-content-refresher'); ?></li>
                    <li><?php _e('建議每日處理 5-10 篇文章', 'gasker-content-refresher'); ?></li>
                    <li><?php _e('使用 GPT-4o 模型可獲得最佳品質', 'gasker-content-refresher'); ?></li>
                    <li><?php _e('定期檢查日誌確認執行狀態', 'gasker-content-refresher'); ?></li>
                </ul>
            </div>
        </div>
    </div>

    <!-- 執行日誌 -->
    <div class="gcr-logs-section">
        <div class="gcr-logs-header">
            <h2><?php _e('執行日誌', 'gasker-content-refresher'); ?></h2>
            <button type="button" class="button gcr-clear-logs">
                <?php _e('清除日誌', 'gasker-content-refresher'); ?>
            </button>
        </div>

        <?php if (empty($logs)): ?>
            <p class="gcr-no-logs"><?php _e('尚無執行記錄', 'gasker-content-refresher'); ?></p>
        <?php else: ?>
            <table class="widefat gcr-logs-table">
                <thead>
                    <tr>
                        <th><?php _e('執行時間', 'gasker-content-refresher'); ?></th>
                        <th><?php _e('類型', 'gasker-content-refresher'); ?></th>
                        <th><?php _e('總計', 'gasker-content-refresher'); ?></th>
                        <th><?php _e('成功', 'gasker-content-refresher'); ?></th>
                        <th><?php _e('失敗', 'gasker-content-refresher'); ?></th>
                        <th><?php _e('跳過', 'gasker-content-refresher'); ?></th>
                        <th><?php _e('詳細', 'gasker-content-refresher'); ?></th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($logs as $index => $log): ?>
                        <tr>
                            <td><?php echo esc_html($log['timestamp']); ?></td>
                            <td>
                                <?php
                                $log_type = $log['type'] ?? 'rewrite';
                                if ($log_type === 'generate') {
                                    echo '<span class="gcr-type-badge gcr-type-generate">' . __('新增', 'gasker-content-refresher') . '</span>';
                                } else {
                                    echo '<span class="gcr-type-badge gcr-type-rewrite">' . __('改寫', 'gasker-content-refresher') . '</span>';
                                }
                                ?>
                            </td>
                            <td><?php echo esc_html($log['total']); ?></td>
                            <td class="gcr-success"><?php echo esc_html($log['success']); ?></td>
                            <td class="gcr-failed"><?php echo esc_html($log['failed']); ?></td>
                            <td class="gcr-skipped"><?php echo esc_html($log['skipped']); ?></td>
                            <td>
                                <button type="button" class="button button-small gcr-view-details" data-index="<?php echo $index; ?>">
                                    <?php _e('查看', 'gasker-content-refresher'); ?>
                                </button>
                            </td>
                        </tr>
                        <tr class="gcr-log-details" id="gcr-log-details-<?php echo $index; ?>" style="display: none;">
                            <td colspan="7">
                                <table class="widefat">
                                    <thead>
                                        <tr>
                                            <th><?php _e('文章 ID', 'gasker-content-refresher'); ?></th>
                                            <th><?php _e('標題', 'gasker-content-refresher'); ?></th>
                                            <th><?php _e('狀態', 'gasker-content-refresher'); ?></th>
                                            <th><?php _e('訊息', 'gasker-content-refresher'); ?></th>
                                            <th><?php _e('Token 消耗', 'gasker-content-refresher'); ?></th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <?php foreach ($log['posts'] as $post_log): ?>
                                            <tr>
                                                <td><?php echo esc_html($post_log['post_id']); ?></td>
                                                <td>
                                                    <a href="<?php echo get_edit_post_link($post_log['post_id']); ?>" target="_blank">
                                                        <?php echo esc_html($post_log['post_title']); ?>
                                                    </a>
                                                </td>
                                                <td>
                                                    <?php
                                                    $status_class = '';
                                                    $status_text = '';
                                                    switch ($post_log['status']) {
                                                        case 'success':
                                                            $status_class = 'gcr-status-success';
                                                            $status_text = __('成功', 'gasker-content-refresher');
                                                            break;
                                                        case 'failed':
                                                            $status_class = 'gcr-status-failed';
                                                            $status_text = __('失敗', 'gasker-content-refresher');
                                                            break;
                                                        case 'skipped':
                                                            $status_class = 'gcr-status-skipped';
                                                            $status_text = __('跳過', 'gasker-content-refresher');
                                                            break;
                                                    }
                                                    ?>
                                                    <span class="<?php echo $status_class; ?>">
                                                        <?php echo $status_text; ?>
                                                    </span>
                                                </td>
                                                <td><?php echo esc_html($post_log['message']); ?></td>
                                                <td><?php echo esc_html($post_log['tokens_used']); ?></td>
                                            </tr>
                                        <?php endforeach; ?>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        <?php endif; ?>
    </div>

    <!-- 除錯日誌 -->
    <div class="gcr-logs-section" style="margin-top: 20px;">
        <div class="gcr-logs-header">
            <h2><?php _e('除錯日誌 (最近 100 筆)', 'gasker-content-refresher'); ?></h2>
            <button type="button" class="button gcr-clear-debug-logs">
                <?php _e('清除除錯日誌', 'gasker-content-refresher'); ?>
            </button>
        </div>

        <?php
        $debug_logs = Gasker_Content_Refresher::get_debug_logs(100);
        ?>

        <?php if (empty($debug_logs)): ?>
            <p class="gcr-no-logs"><?php _e('尚無除錯記錄', 'gasker-content-refresher'); ?></p>
        <?php else: ?>
            <div style="background: #f9f9f9; border: 1px solid #ddd; padding: 15px; max-height: 400px; overflow-y: scroll; font-family: monospace; font-size: 12px; line-height: 1.6;">
                <?php foreach (array_reverse($debug_logs) as $log): ?>
                    <div style="margin-bottom: 5px; border-bottom: 1px solid #eee; padding-bottom: 5px;">
                        <span style="color: #666;"><?php echo esc_html($log['time']); ?></span>
                        <span style="color: #333; margin-left: 10px;"><?php echo esc_html($log['message']); ?></span>
                    </div>
                <?php endforeach; ?>
            </div>
        <?php endif; ?>
    </div>
</div>
