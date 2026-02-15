/**
 * Gasker Content Refresher - Admin JavaScript
 */

(function($) {
    'use strict';

    const GCR = {

        /**
         * 初始化
         */
        init: function() {
            this.bindEvents();
        },

        /**
         * 綁定事件
         */
        bindEvents: function() {
            // 立即執行改寫按鈕
            $('.gcr-run-now').on('click', this.runNow.bind(this));

            // 立即生成新文章按鈕
            $('.gcr-generate-now').on('click', this.generateNow.bind(this));

            // 清除日誌按鈕
            $('.gcr-clear-logs').on('click', this.clearLogs.bind(this));

            // 清除除錯日誌按鈕
            $('.gcr-clear-debug-logs').on('click', this.clearDebugLogs.bind(this));

            // 查看詳細按鈕
            $('.gcr-view-details').on('click', this.toggleDetails.bind(this));

            // 表單提交時的確認
            $('form').on('submit', function(e) {
                const autoPublish = $('input[name="gcr_settings[auto_publish]"]:checked').val();
                if (autoPublish === '1') {
                    if (!confirm(gcrAjax.strings.confirm_auto_publish || '確定要啟用自動發布模式嗎？建議先使用待審閱模式測試幾天。')) {
                        e.preventDefault();
                        return false;
                    }
                }
            });
        },

        /**
         * 立即執行
         */
        runNow: function() {
            const $btn = $('.gcr-run-now');

            if ($btn.hasClass('loading')) {
                return;
            }

            if (!confirm('確定要立即執行一次改寫任務嗎？')) {
                return;
            }

            $btn.addClass('loading').prop('disabled', true);

            // 添加載入動畫
            const originalText = $btn.text();
            $btn.html('<span class="gcr-spinner"></span>' + gcrAjax.strings.running);

            $.ajax({
                url: gcrAjax.ajax_url,
                type: 'POST',
                data: {
                    action: 'gcr_run_now',
                    nonce: gcrAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        const result = response.data;
                        const message = `執行完成！\n總計: ${result.total} 篇\n成功: ${result.success} 篇\n失敗: ${result.failed} 篇\n跳過: ${result.skipped} 篇`;

                        GCR.showNotification(message, 'success');

                        // 重新載入頁面以顯示新日誌
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    } else {
                        GCR.showNotification(response.data.message || gcrAjax.strings.error, 'error');
                    }
                },
                error: function(xhr, status, error) {
                    GCR.showNotification('發生錯誤: ' + error, 'error');
                },
                complete: function() {
                    $btn.removeClass('loading').prop('disabled', false).html(originalText);
                }
            });
        },

        /**
         * 立即生成新文章
         */
        generateNow: function() {
            const $btn = $('.gcr-generate-now');

            if ($btn.hasClass('loading')) {
                return;
            }

            if (!confirm('確定要立即生成新文章嗎？')) {
                return;
            }

            $btn.addClass('loading').prop('disabled', true);

            const originalText = $btn.text();
            $btn.html('<span class="gcr-spinner"></span>AI 生成中...');

            $.ajax({
                url: gcrAjax.ajax_url,
                type: 'POST',
                data: {
                    action: 'gcr_generate_now',
                    nonce: gcrAjax.nonce
                },
                timeout: 120000, // 2 分鐘超時（AI 生成較慢）
                success: function(response) {
                    if (response.success) {
                        const result = response.data;
                        const message = `新文章生成完成！\n成功: ${result.success} 篇\n失敗: ${result.failed} 篇`;

                        GCR.showNotification(message, 'success');

                        // 重新載入頁面以顯示新日誌
                        setTimeout(function() {
                            location.reload();
                        }, 2000);
                    } else {
                        GCR.showNotification(response.data.message || '生成失敗', 'error');
                    }
                },
                error: function(xhr, status, error) {
                    let errorMsg = '發生錯誤: ';
                    if (status === 'timeout') {
                        errorMsg += 'AI 生成超時，請稍後再試';
                    } else {
                        errorMsg += error;
                    }
                    GCR.showNotification(errorMsg, 'error');
                },
                complete: function() {
                    $btn.removeClass('loading').prop('disabled', false).html(originalText);
                }
            });
        },

        /**
         * 清除日誌
         */
        clearLogs: function() {
            if (!confirm(gcrAjax.strings.confirm_clear)) {
                return;
            }

            $.ajax({
                url: gcrAjax.ajax_url,
                type: 'POST',
                data: {
                    action: 'gcr_clear_logs',
                    nonce: gcrAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        GCR.showNotification(response.data.message, 'success');

                        // 重新載入頁面
                        setTimeout(function() {
                            location.reload();
                        }, 1000);
                    } else {
                        GCR.showNotification(response.data.message || gcrAjax.strings.error, 'error');
                    }
                },
                error: function(xhr, status, error) {
                    GCR.showNotification('發生錯誤: ' + error, 'error');
                }
            });
        },

        /**
         * 清除除錯日誌
         */
        clearDebugLogs: function() {
            if (!confirm('確定要清除所有除錯日誌嗎?')) {
                return;
            }

            $.ajax({
                url: gcrAjax.ajax_url,
                type: 'POST',
                data: {
                    action: 'gcr_clear_debug_logs',
                    nonce: gcrAjax.nonce
                },
                success: function(response) {
                    if (response.success) {
                        GCR.showNotification(response.data.message, 'success');

                        // 重新載入頁面
                        setTimeout(function() {
                            location.reload();
                        }, 1000);
                    } else {
                        GCR.showNotification(response.data.message || gcrAjax.strings.error, 'error');
                    }
                },
                error: function(xhr, status, error) {
                    GCR.showNotification('發生錯誤: ' + error, 'error');
                }
            });
        },

        /**
         * 切換詳細資訊顯示
         */
        toggleDetails: function(e) {
            const $btn = $(e.currentTarget);
            const index = $btn.data('index');
            const $details = $('#gcr-log-details-' + index);

            if ($details.is(':visible')) {
                $details.hide();
                $btn.text('查看');
            } else {
                // 隱藏其他詳細資訊
                $('.gcr-log-details').hide();
                $('.gcr-view-details').text('查看');

                // 顯示當前詳細資訊
                $details.show();
                $btn.text('隱藏');
            }
        },

        /**
         * 顯示通知
         */
        showNotification: function(message, type) {
            type = type || 'info';

            const $notification = $('<div class="gcr-notification ' + type + '"></div>');
            $notification.html('<p>' + message.replace(/\n/g, '<br>') + '</p>');

            $('body').append($notification);

            setTimeout(function() {
                $notification.fadeOut(300, function() {
                    $(this).remove();
                });
            }, 5000);
        }
    };

    // 當文檔準備好時初始化
    $(document).ready(function() {
        GCR.init();
    });

})(jQuery);
