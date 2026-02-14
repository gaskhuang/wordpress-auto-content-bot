# 更新日誌

本文件記錄 Gasker Content Refresher 的所有重要變更。

格式基於 [Keep a Changelog](https://keepachangelog.com/zh-TW/1.0.0/),
版本號遵循 [Semantic Versioning](https://semver.org/lang/zh-TW/)。

## [1.0.0] - 2025-01-24

### 新增
- ✨ 初始版本發布
- ✨ 每日自動排程改寫舊文章功能
- ✨ 支援 OpenAI GPT-4o / GPT-4o-mini 模型
- ✨ 支援 Google Gemini 1.5 Pro 模型
- ✨ 待審閱模式 (改寫後設為 pending 狀態)
- ✨ 自動發布模式 (直接更新已發布文章)
- ✨ HTML 結構完整性驗證
- ✨ 內容長度安全檢查
- ✨ 圖片保護機制
- ✨ 詳細執行日誌 (保留最近 50 筆)
- ✨ 手動「立即執行」功能
- ✨ Email 通知摘要
- ✨ 分類排除功能
- ✨ 文章 ID 排除功能
- ✨ 冷卻期設定 (避免重複改寫)
- ✨ 最大文章長度限制
- ✨ Token 使用量記錄
- ✨ 繁體中文/簡體中文/英文介面
- ✨ 完整的管理後台介面
- ✨ AJAX 即時操作
- ✨ 響應式設計

### 安全性
- 🔒 NONCE 驗證
- 🔒 權限檢查 (manage_options)
- 🔒 輸入清理 (sanitize_text_field, absint 等)
- 🔒 輸出跳脫 (esc_html, esc_attr 等)
- 🔒 SQL 注入防護
- 🔒 XSS 防護
- 🔒 CSRF 防護

### 文件
- 📝 README.md (繁體中文)
- 📝 INSTALL.md (詳細安裝指南)
- 📝 CHANGELOG.md (更新日誌)
- 📝 LICENSE (GPL v2)
- 📝 readme.txt (WordPress.org 格式)
- 📝 程式碼註解 (PHPDoc)

## [未來計畫]

### 計畫中的功能 (v1.1.0)
- [ ] 批次處理優化 (支援更大量文章)
- [ ] 自訂 Prompt 模板
- [ ] 多語言翻譯功能
- [ ] 圖片 Alt 文字優化
- [ ] 內部連結自動新增
- [ ] 關鍵字密度分析
- [ ] SEO 分數評估
- [ ] 改寫歷史記錄 (版本控制)
- [ ] A/B 測試功能
- [ ] 排程時間自訂 (不只是每日)
- [ ] Webhook 通知 (Slack, Discord 等)
- [ ] 進階統計報表
- [ ] 匯出/匯入設定

### 考慮中的功能 (v2.0.0)
- [ ] 支援頁面 (Page) 改寫
- [ ] 支援自訂文章類型
- [ ] AI 生成精選圖片
- [ ] 自動生成 Meta Description
- [ ] 標題優化建議
- [ ] 競爭對手分析
- [ ] 內容品質評分
- [ ] 多站點 (Multisite) 支援
- [ ] API 端點 (供外部呼叫)
- [ ] WP-CLI 指令

### 已知問題

目前無已知重大問題。

## 版本號說明

格式: MAJOR.MINOR.PATCH

- **MAJOR**: 重大變更,可能不向下相容
- **MINOR**: 新功能,向下相容
- **PATCH**: 錯誤修正,向下相容

---

## 貢獻指南

如果您想貢獻代碼或報告問題,請參考以下流程:

### 報告 Bug

1. 檢查是否已有相同問題被回報
2. 提供詳細的重現步驟
3. 包含 WordPress/PHP 版本資訊
4. 附上錯誤日誌或截圖

### 建議新功能

1. 描述功能的使用場景
2. 說明預期行為
3. 提供設計草圖 (如果有)

### 提交 Pull Request

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

---

**感謝您使用 Gasker Content Refresher!**
