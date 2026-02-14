=== Gasker Content Refresher ===
Contributors: gaskertec
Tags: seo, content, ai, refresh, openai
Requires at least: 6.0
Tested up to: 6.4
Requires PHP: 7.4
Stable tag: 1.0.2
License: GPLv2 or later
License URI: http://www.gnu.org/licenses/gpl-2.0.html

通過 AI 自動化翻新舊文章,提升內容新鮮度以優化 SEO 排名。

== Description ==

Gasker Content Refresher 是一個專業的 WordPress 插件,能夠自動化地使用 AI 技術翻新您網站上的舊文章,幫助提升內容新鮮度和 SEO 排名。

= 主要功能 =

* 每日自動處理最舊的文章
* 支援 OpenAI GPT-4o / GPT-4o-mini / Gemini 1.5 Pro
* 內建待審閱模式,確保內容質量
* 自動驗證 HTML 結構完整性
* 可自訂處理數量、冷卻期、排除規則
* 完整的執行日誌記錄
* Email 通知功能

= 為什麼需要這個插件? =

* **提升 SEO**: 定期更新文章可以向搜索引擎發送「新鮮內容」的信號
* **節省時間**: 自動化處理,無需手動編輯每篇文章
* **保持現代**: 使用 AI 將舊內容的語氣現代化
* **安全可靠**: 內建多重安全檢查,保護您的內容

= 系統需求 =

本插件需要安裝並啟用 **AI Engine by Jordy Meow** 插件。

== Installation ==

1. 安裝並啟用 AI Engine 插件
2. 在 AI Engine 中配置您的 OpenAI 或 Gemini API Key
3. 上傳 `gasker-content-refresher` 資料夾到 `/wp-content/plugins/` 目錄
4. 在 WordPress 後台啟用插件
5. 前往 設定 → Content Refresher 進行配置

== Frequently Asked Questions ==

= 需要付費嗎? =

插件本身免費,但需要 AI Engine 和 API Key (OpenAI/Gemini),API 使用會產生費用。

= 會不會破壞我的文章? =

插件內建多重安全檢查,並提供「待審閱」模式。初期建議人工審查幾天,確認穩定後再啟用自動發布。

= 如何停止自動執行? =

停用插件即可,或將「每日處理篇數」設為 0。

= 支援哪些 AI 模型? =

支援 OpenAI GPT-4o、GPT-4o-mini 和 Gemini 1.5 Pro。

== Screenshots ==

1. 設定頁面 - 配置插件參數
2. 執行日誌 - 查看處理歷史
3. 系統狀態 - 即時監控

== Changelog ==

= 1.0.2 =
* 修正: 新增 environment 設定以相容最新版 AI Engine
* 修正: 解決 "The environment is required" 錯誤

= 1.0.1 =
* 修正: 更新 AI Engine API 相容性 (移除已棄用的 get_instance() 方法)
* 修正: 改用全域變數 $mwai_core 執行查詢
* 改進: 增強除錯日誌記錄功能

= 1.0.0 =
* 初始版本發布
* 支援每日自動改寫
* 整合 AI Engine
* 待審閱/自動發布雙模式
* 完整的安全驗證機制
* 詳細執行日誌
* Email 通知功能
* 排除規則設定

== Upgrade Notice ==

= 1.0.2 =
重要修正: 解決與最新版 AI Engine 的 environment 設定問題。強烈建議更新。

= 1.0.1 =
重要修正: 解決了與新版 AI Engine 的相容性問題。建議所有使用者更新。

= 1.0.0 =
初始版本發布。

== Additional Info ==

使用本插件前請務必備份資料庫!
