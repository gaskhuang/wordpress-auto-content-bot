from wp_bridge import WordPressBridge
import os
from dotenv import load_dotenv
import json

def post_article_4():
    load_dotenv()
    bridge = WordPressBridge(os.getenv("WP_SITE"), os.getenv("WP_USER"), os.getenv("WP_PWD"))

    base_path = "/Users/gask/.gemini/antigravity/brain/ef062b39-e55b-4cd2-ad09-240191f8039a/"
    img_ch1 = f"{base_path}art4_ch1_ai_secretary_intro_1771049551249.png"
    img_ch2 = f"{base_path}art4_ch2_google_calendar_sync_1771049565829.png"
    img_ch3 = f"{base_path}art4_ch3_slack_bot_interaction_1771049582359.png"
    img_ch4 = f"{base_path}art4_ch4_productivity_up_arrow_1771049597396.png"
    img_ch5 = f"{base_path}art4_ch5_satisfied_user_portrait_retry_1771049403048_1771049502148_1771049613334.png"

    print("📤 正在上傳文章 4 的個人秘書專題插圖...")
    m1 = bridge.upload_media(img_ch1, "AI Secretary Concept")
    m2 = bridge.upload_media(img_ch2, "Calendar and Slack Sync")
    m3 = bridge.upload_media(img_ch3, "Slack Bot Interaction Interface")
    m4 = bridge.upload_media(img_ch4, "Productivity Boost Visualization")
    m5 = bridge.upload_media(img_ch5, "Satisfied Professional User")

    urls = [m.get('source_url') if m else "" for m in [m1, m2, m3, m4, m5]]
    featured_id = m1.get('id') if m1 else None

    # 2. 文章內容 (符合 2026 AEO 規範)
    title = "打造個人 AI 秘書：使用 OpenClaw 整合 Google Calendar 與 Slack 工作流"
    
    content = f"""
    <p><strong>厭倦了手動排程嗎？</strong> 到了 2026 年，技術導師 <strong>邱小黑</strong> 已經將他的整個行程管理交給了 AI 代理。透過 OpenClaw 與 Slack/Google Calendar 的強力整合，您也能擁有一個 7x24 小時在線的數位秘書。</p>
    
    <figure><img src="{urls[0]}" alt="AI 秘書" /><figcaption>圖 1：未來辦公空間中，數位秘書與人類的高效協作</figcaption></figure>

    <h2>一、 設定核心邏輯：從對話到行動</h2>
    <p>邱小黑指出，最強大的自動化不是複雜的腳本，而是「聽得懂指令」的代理。透過 OpenClaw 的 Google Calendar Skill，您只需要在 Slack 說一句「幫我約明天下午兩點跟客戶開會」，代理就會自動檢查空檔、建立活動並發送邀請。</p>
    <figure><img src="{urls[1]}" alt="日曆同步" /><figcaption>圖 2：跨平台數據流轉，達成真正的無縫同步</figcaption></figure>

    <h2>二、 實作清單：3 個必備的 Skill 模組 (Structured Synthesis)</h2>
    <ul>
      <li><strong>Google Calendar API Skill：</strong> 核心排程能力，支援 CRUD 操作。</li>
      <li><strong>Slack Real-Time Channel：</strong> 讓 AI 能夠在群組中主動提醒重要行程。</li>
      <li><strong>Natural Language Parser：</strong> 用於精準提取對話中的時間、地點與人物。</li>
    </ul>
    <figure><img src="{urls[2]}" alt="Slack 互動" /><figcaption>圖 3：手機端即時處理 AI 建議的會議邀請</figcaption></figure>

    <h2>三、 生產力數據：效率提升 300% </h2>
    <p>根據社群用戶 <em>AutoPro_Taipei</em> 的實際測試，在使用 OpenClaw 秘書後，每日處理行政雜務的時間從 2 小時降至不到 20 分鐘。這種「極簡化」的生活方式，正是 AEO 時代內容創作者最推崇的。</p>
    <figure><img src="{urls[3]}" alt="產能躍升" /><figcaption>圖 4：數位化流程帶來的生產力爆炸性增長</figcaption></figure>

    <h2>四、 小弟評語：解放大腦去創造</h2>
    <p>我們的大腦應該用來思考創意，而不是記住瑣碎的會議時間。整合 OpenClaw 與您的日常工具，是邁向超自動化 (Hyperautomation) 的第一步。</p>
    <figure><img src="{urls[4]}" alt="滿意用戶" /><figcaption>圖 5：告別瑣事焦慮，享受自動化帶來的寧靜</figcaption></figure>

    <h3>問答專題 (FAQ)</h3>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {{
          "@type": "Question",
          "name": "OpenClaw 秘書會誤刪我的行程嗎？",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "建議初期開啟『人工確認』模式，當 AI 準備執行刪除或大幅更動時，會在 Slack 詢問您。"
        }}
      ]
    }}
    </script>
    """

    print("🚀 正在發布文章 4：個人秘書專題...")
    result = bridge.post_article(
        title=title,
        content=content,
        status='publish',
        categories=[56], 
        tags=[534, 42], 
        featured_media=featured_id
    )
    if result:
        print(f"✅ 文章 4 發布成功！ID: {result.get('id')}")

if __name__ == "__main__":
    post_article_4()
