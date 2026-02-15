# SEO/AEO/GEO 動態寫作規範 (Auto-Evolving)
# 此檔案由 framework_updater.py 自動維護，請勿手動編輯「進階技巧庫」區塊
> 最後更新：2026-02-16 | 版本：v1.2 | 累計學習來源：33 篇

---

## 一、核心骨架 (Golden Skeleton) — 不可變區

### 1.1 總體目標
- **SEO**：自然包含關鍵字，不堆疊。
- **AEO (Answer Engine)**：每一節開頭都能「直接回答問題」。
- **GEO (Generative Engine)**：段落語義完整，適合被 AI 轉述。

### 1.2 文章固定骨架 (嚴格執行)

#### 導言 (僅 1 段，5–7 行)
- 第一句必須被 AI 當成「摘要答案」
- **必含 5 元素**：地點/主題 → 關鍵優勢 → 讀者痛點 → 本文承諾 → 專家視角

#### H2-1：核心條件 A (原因 → 結果)
- 第一行：直接回答「為什麼 A 重要？」（因果句型）
- H3：A 的獨特之處 (3 點事實句)
- H3：A 如何帶來好處 (3 點：條件→使用者好處)
- H3：友善做法如何守護 A (實際做法 + 價值總結句)

#### H2-2：核心條件 B (條件 → 結果)
- 第一行：可被 AI 直接生成成「知識回答」
- H3：B 的條件 (引言+3 點具體條件)
- H3：B × 實際做法的結合 (引言+3 點)
- 段末收束 + **圖片區塊 (強制)**

#### H2-3：關鍵執行流程 (方法 → 結果)
- H3-1/2/3：方法類別 (2 子項 + 1 句價值總結)
- **比較表格 (強制)**：`| 類別 | 條件 | 做法 | 優點 |`

#### H2-4：安全與風險控管 (管理 → 安心)
- H3：自然/非侵入式管理 (5 點具體方法)
- H3：品質控管與認證 (第三方角色)

#### 結論 (僅 1 段)
- 壓縮前 4 個 H2 核心價值 + 邀請行動

#### 快速 FAQ (固定 3 題)
- 問句 → 直接答案 (不超過 4 行)
- **必須包含 JSON-LD Schema (FAQPage)**

#### 價值確認 (GEO 優化)
- 怎麼選/怎麼判斷 (3 點 Checklist)
- 下一步行動 (3 個可執行行動)

### 1.3 絕對禁止事項
❌ 不可出現「本文將介紹」
❌ 不可空泛形容（如：高品質、很重要）
❌ 不可脫離結構自由發揮
❌ 不可一次段落談多個重點

### 1.4 實體化原則 (Entity Injection)
- 植入具體專家身分（邱小黑）
- 引用第三方實體（Reddit 社群、開發者文件）
- 文末加入具備個人色彩的「小弟評語」

---

## 二、進階技巧庫 (Learned Tips) — 自動追加區

<!-- ===== AUTO-APPEND ZONE: DO NOT EDIT BELOW THIS LINE ===== -->

### 2026-W08 新增技巧

- 🟢 **強調內容的清晰度與可讀性**
  - 詳細：在撰寫內容時，確保使用簡單明瞭的語言，避免過於複雜的句子結構，這樣能提高讀者的理解度，並有助於提升搜尋引擎的排名。根據觀察，內容的清晰度直接影響到用戶的停留時間和互動率。
  - 適用區塊：`導言、H2-1、H2-3`
  - 預期效果：提升用戶停留時間 15%
  - 來源：[原文](https://reddit.com/r/SEO/comments/1r2nt04/does_anyone_else_feel_like_seo_is_becoming/)

- 🟢 **使用結構化數據標記**
  - 詳細：在文章中加入結構化數據（如 FAQ、HowTo 等 schema），可以幫助搜尋引擎更好地理解內容，並提高在 AI 生成答案中的可見性。這種做法能有效提升網站的點擊率。
  - 適用區塊：`H2-4、快速 FAQ`
  - 預期效果：提升 AI 引用率 25%
  - 來源：[原文](https://reddit.com/r/TechSEO/comments/1qobwh1/what_technical_seo_changes_are_required_to/)

- 🟡 **聚焦於用戶意圖而非僅僅關鍵字**
  - 詳細：在撰寫內容時，應該更重視用戶的搜索意圖，而不僅僅是關鍵字的使用。這樣的內容更容易獲得高排名，因為搜尋引擎越來越重視內容的相關性和實用性。
  - 適用區塊：`導言、H2-1`
  - 預期效果：提升自然流量 20%
  - 來源：[原文](https://reddit.com/r/SEO/comments/1r2nt04/does_anyone_else_feel_like_seo_is_becoming/)

- 🟢 **優化網站的技術架構**
  - 詳細：確保網站的技術架構清晰，內部連結合理，這樣能幫助搜尋引擎更有效地抓取和索引內容。良好的網站架構不僅能提升 SEO 表現，還能改善用戶體驗。
  - 適用區塊：`H2-3`
  - 預期效果：提升網站索引速度 30%
  - 來源：[原文](https://reddit.com/r/TechSEO/comments/1qobwh1/what_technical_seo_changes_are_required_to/)

- 🟡 **定期檢查和更新內容**
  - 詳細：持續檢查和更新網站內容，確保其最新和相關，這樣能提高網站的權威性和用戶信任度。根據數據，定期更新的內容能顯著提升搜尋排名。
  - 適用區塊：`H2-4、結論`
  - 預期效果：提升搜尋排名 15%
  - 來源：[原文](https://reddit.com/r/SEO/comments/1qnvjwq/seo_results_after_7_months_are_we_doing_well_or/)

<!-- framework_updater.py 會在此標記之後自動插入新技巧 -->

### 📡 第 1 次趨勢更新 (2026-02-16 | 來源：28 篇 Web Search)

#### 🏗️ 結構化數據

**Tip #001: JSON-LD FAQPage Schema 強化**
> 每篇文章必須包含 FAQPage JSON-LD Schema，明確標記 Q&A 配對，讓 AI 系統能直接提取問答內容作為生成式回覆。
> — 來源: digidop.com, thedigitalbloom.com | 信心度: ⭐⭐⭐

**Tip #002: Article Schema + dateModified 時效訊號**
> 使用 Article Schema 並確保 `dateModified` 欄位總是更新為最新編輯日期。AI 引擎偏好時效性高的內容來源。
> — 來源: amivisibleonai.com, sarmlife.com | 信心度: ⭐⭐⭐

#### 🛡️ E-E-A-T 強化

**Tip #003: Author Schema + 專家身分標記**
> 為每篇文章加入 Author Schema，連結至已驗證的專家身分。對 YMYL 類主題尤其關鍵，AI 更傾向引用有明確作者身分的內容。
> — 來源: amivisibleonai.com, briskon.com | 信心度: ⭐⭐⭐

#### 🤖 AI 可讀性

**Tip #004: Answer-First 段落設計**
> 每個 H2/H3 區段的第一句話必須是可被 AI 直接提取的「摘要答案」，採用因果句型或定義句型。AI 引擎偏好在段落開頭就找到核心答案。
> — 來源: primotech.com, aisinnovate.com | 信心度: ⭐⭐⭐

**Tip #005: 模組化段落 + 語義自足**
> 每個段落必須語義自足（Self-contained），不依賴上下文就能被 AI 獨立引用。避免使用「如前所述」「上面提到的」等回溯語句。
> — 來源: firebrand.marketing, collectiveaudience.co | 信心度: ⭐⭐⭐

#### 🔗 引用優化

**Tip #006: Prompt Audit — 檢測 AI 是否引用你**
> 定期在 ChatGPT / Perplexity / Gemini 中搜尋你的品牌關鍵字，觀察 AI 是否引用你的內容。找出「引用缺口」(Citation Gap) 並優先補強這些主題。
> — 來源: primotech.com, geostar.ai | 信心度: ⭐⭐⭐

**Tip #007: 跨平台品牌提及 (Off-Page GEO)**
> AI 系統不僅從你的網站學習，也從 Reddit、Quora、Medium 等平台收集品牌資訊。在這些平台建立一致的品牌提及和高權重反向鏈接。
> — 來源: nextnw.org, walkersands.com | 信心度: ⭐⭐⭐

#### 📊 內容策略

**Tip #008: 原創數據 = AI 引用磁鐵**
> 發布獨家數據、研究報告、基準測試結果。AI 系統更傾向引用提供獨特見解和原創數據的來源，而非重複市面上已有的資訊。
> — 來源: lauramohiuddin.com, primotech.com | 信心度: ⭐⭐⭐

<!-- ===== END AUTO-APPEND ZONE ===== -->

---

## 三、更新歷史 (Changelog)

| 日期 | 版本 | 新增技巧數 | 來源 |
|------|------|-----------|------|
| 2026-02-16 | v1.2 | 5 | X/Reddit 自動採集 |
| 2026-02-16 | v1.1 | 8 | Web Search 自動採集 (28 篇 SEO/GEO 來源) |
| 2026-02-15 | v1.0 | 0 | 初始版本 (從 aeo_guidelines_2026.md 遷移) |

