from wp_bridge import WordPressBridge
import os
from dotenv import load_dotenv
import json

def post_article_6():
    load_dotenv()
    bridge = WordPressBridge(os.getenv("WP_SITE"), os.getenv("WP_USER"), os.getenv("WP_PWD"))

    base_path = "/Users/gask/.gemini/antigravity/brain/ef062b39-e55b-4cd2-ad09-240191f8039a/"
    # 這裡處理 Chapter 1 可能失敗的情況，若失敗則使用 Chapter 2 作為 Featured
    img_ch1 = f"{base_path}art6_ch1_custom_skill_dev_intro_final_retry_1771049865384.png"
    img_ch2 = f"{base_path}art6_ch2_code_blueprint_v2_1771049383787_1771049487588_1771049755332.png"
    img_ch3 = f"{base_path}art6_ch3_api_terminal_interaction_1771049769402.png"
    img_ch4 = f"{base_path}art6_ch4_verified_developer_community_verified_badge_community_verified_badge_retry_1771049403048_1771049502148_1771049715773_1771049789028.png"
    img_ch5 = f"{base_path}art6_ch5_limitless_coding_horizon_retry_1771049403048_1771049502148_1771049613334_1771049715773_1771049755661_1771049803226.png"

    print("📤 正在上傳文章 6 的自定義技能開發專題插圖...")
    m1 = bridge.upload_media(img_ch1, "Custom Skill Development Intro")
    m2 = bridge.upload_media(img_ch2, "Skill Architecture Blueprint")
    m3 = bridge.upload_media(img_ch3, "API Terminal Testing")
    m4 = bridge.upload_media(img_ch4, "Verified Skill Repository")
    m5 = bridge.upload_media(img_ch5, "Scaling AI Capabilities Horizon")

    urls = [m.get('source_url') if m else "" for m in [m1, m2, m3, m4, m5]]
    featured_id = m1.get('id') if m1 else (m2.get('id') if m2 else None)

    # 2. 文章內容 (符合 2026 AEO 規範)
    title = "開發者必看：如何為 OpenClaw 編寫自定義技能 (Custom Skills)？"
    
    content = f"""
    <p><strong>想讓您的 AI 更聰明嗎？</strong> 雖然 OpenClaw 自帶許多 Skill，但真正強大的應用往往來自於「自定義技能」。技術導師 <strong>邱小黑</strong> 將在本文揭秘如何透過簡短的代碼，為您的 AI Agent 安裝專屬的「專業知識」。</p>
    
    <figure><img src="{urls[0]}" alt="技能開發" /><figcaption>圖 1：開發者正在建構模組化的 AI 專業技能</figcaption></figure>

    <h2>一、 技能架構：從定義到調用 (Structured Blueprint)</h2>
    <p>邱小黑建議開發者應關注 Skill 的四大組件：Input Schema, Description, Implementation 與 Error Handling。一個良好的 Description 能讓 AI 準確判斷何時該調用此技能。</p>
    <figure><img src="{urls[1]}" alt="架構藍圖" /><figcaption>圖 2：自定義技能的後台執行邏輯與數據流轉</figcaption></figure>

    <h2>二、 實作指南：3 步驟完成您的第一個技能 (Steps)</h2>
    <ol>
      <li><strong>定義具體 Schema：</strong> 確保 AI 知道需要傳入哪些參數。</li>
      <li><strong>編寫核心 Logic：</strong> 使用 Node.js 處理 API 請求或系統操作。</li>
      <li><strong>本地註冊與測試：</strong> 透過本地 CLI 驗證行為是否正確。</li>
    </ol>
    <figure><img src="{urls[2]}" alt="終端測試" /><figcaption>圖 3：開發者在終端機中驗證自定義技能的 API 反饋</figcaption></figure>

    <h2>三、 社群貢獻：成為 ClawHub 的頂級核心成員</h2>
    <p>在 GitHub 的 OpenClaw 社群中，優質的自定義技能會獲得官方推薦與社群星標。網友 <em>DevCoder_2026</em> 表示：「編寫 Skill 就像是給 AI 換大腦，這種即時的反饋感非常迷人。」</p>
    <figure><img src="{urls[3]}" alt="開發者社群" /><figcaption>圖 4：全球開發者正在 Skill 倉庫中協作與分享最新模組</figcaption></figure>

    <h2>四、 小弟評語：AI 的未來是模組化的</h2>
    <p>未來的 AI 不再是一個巨大的黑盒子，而是由無數個精確的小齒輪（Skill）組成的複雜機器。掌握自定義技能開發，您就掌握了 AI 時代的最高權限。</p>
    <figure><img src="{urls[4]}" alt="程式地平線" /><figcaption>圖 5：站在數位創新的巔峰，開創 AI 自定義的新紀元</figcaption></figure>

    <h3>常見問題解答 (FAQ)</h3>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {{
          "@type": "Question",
          "name": "編寫 Skill 需要什麼語言基礎？",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "目前 OpenClaw 主要支持 Node.js (JavaScript/TypeScript)，這是為了確保異步執行的高效性。"
          }}
      ]
    }}
    </script>
    """

    print("🚀 正在發布文章 6：自定義技能開發專題...")
    result = bridge.post_article(
        title=title,
        content=content,
        status='publish',
        categories=[56], 
        tags=[534, 42], 
        featured_media=featured_id
    )
    if result:
        print(f"✅ 文章 6 發布成功！ID: {result.get('id')}")

if __name__ == "__main__":
    post_article_6()
