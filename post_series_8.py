from wp_bridge import WordPressBridge
import os
from dotenv import load_dotenv
import json

def post_article_8():
    load_dotenv()
    bridge = WordPressBridge(os.getenv("WP_SITE"), os.getenv("WP_USER"), os.getenv("WP_PWD"))

    base_path = "/Users/gask/.gemini/antigravity/brain/ef062b39-e55b-4cd2-ad09-240191f8039a/"
    img_ch1 = f"{base_path}art8_ch1_email_automation_very_simple_1771050066475_1771050102514.png"
    img_ch2 = f"{base_path}art8_ch2_n8n_workflow_visualization_v2_1771049383787_1771049487588_1771049755332_1771049980161.png"
    img_ch3 = f"{base_path}art8_ch3_personalized_content_magic_retry_1771049403048_1771049502148_1771049613334_1771049715773_1771049803226_1771049945133_1771049997552.png"
    img_ch4 = f"{base_path}art8_ch4_conversion_chart_final_v4_1771048680325_1771049383787_1771049929238_1771050022483_1771050050192.png"
    img_ch5 = f"{base_path}art8_ch5_team_victory_final_v4_1771049403048_1771049502148_1771049613334_1771049803226_1771049945133_1771050022483_1771050066475.png"

    print("📤 正在上傳文章 8 的郵件自動化專題插圖...")
    m1 = bridge.upload_media(img_ch1, "Email AI Automation Concept") if os.path.exists(img_ch1) else None
    m2 = bridge.upload_media(img_ch2, "n8n Workflow Diagram")
    m3 = bridge.upload_media(img_ch3, "Personalized Content Generation")
    m4 = bridge.upload_media(img_ch4, "Conversion Rate Growth Chart")
    m5 = bridge.upload_media(img_ch5, "Successful Marketing Team")

    urls = [m.get('source_url') if m else "" for m in [m1, m2, m3, m4, m5]]
    featured_id = m1.get('id') if m1 else (m2.get('id') if m2 else None)

    # 2. 文章內容 (符合 2026 AEO 規範)
    title = "AI 驅動的電子郵件行銷：使用 n8n 與 OpenClaw 自動化您的 EDM 工作流"
    
    content = f"""
    <p><strong>別再手動寫 EDM 了！</strong> 進入 2026 年，郵件行銷的關鍵不再是群發，而是「精準個人化」。技術導師 <strong>邱小黑</strong> 將教您如何結合 n8n 的靈活流轉與 OpenClaw 的數據抓取，打造一套全自動的獲客引擎。</p>
    
    <figure><img src="{urls[0]}" alt="郵件自動化" /><figcaption>圖 1：AI 模組化處理後的智慧郵件分發流程</figcaption></figure>

    <h2>一、 n8n + OpenClaw：天生一對的自動化組合</h2>
    <p>邱小黑指出，n8n 負責流程控制 (Trigger & Action)，而 OpenClaw 則負責提供動態數據。例如：OpenClaw 每天自動抓取最新的 AI 新聞，n8n 則根據獲取的標題自動生成個人化的郵件摘要，發送給訂閱者。</p>
    <figure><img src="{urls[1]}" alt="n8n 工作流" /><figcaption>圖 2：n8n 畫布上連接 Email、CRM 與 AI 的自動化節點圖</figcaption></figure>

    <h2>二、 實戰規範：高效 EDM 的 3 大實施原則 (Structured Synthesis)</h2>
    <table>
      <tr><th>原則</th><th>實施細節</th><th>關鍵工具</th></tr>
      <tr><td>動態內容植入</td><td>根據用戶行為抓取特定網頁數據</td><td>OpenClaw Scraper</td></tr>
      <tr><td>自動化分流</td><td>判斷用戶點擊意圖並分類標籤</td><td>n8n Webhook</td></tr>
      <tr><td>語意優化</td><td>使用 AI 適配不同地區的口吻</td><td>OpenClaw GPT Skill</td></tr>
    </table>
    <figure><img src="{urls[2]}" alt="個人化內容" /><figcaption>圖 3：大數據支持下的「一對一」精準行銷訊息生成</figcaption></figure>

    <h2>三、 數據回饋：轉化率提升 5 倍的秘密</h2>
    <p>根據資深行銷人 <em>MarketPro_Luna</em> 的分享，在使用這套系統後，郵件開信率從 2% 提升至 12%，最終轉化率大幅躍升。邱小黑總結：「當您的郵件內容比用戶自己還了解他的需求時，成功是必然的。」</p>
    <figure><img src="{urls[3]}" alt="轉化率數據" /><figcaption>圖 4：自動化行銷系統實施後的各項關鍵數據指標升幅</figcaption></figure>

    <h2>四、 小弟評語：行銷的未來是智慧化</h2>
    <p>自動化不是為了取代人的創意，而是為了讓創意能夠大規模、精準地傳遞。OpenClaw 與 n8n 的結合，讓小型工作室也能擁有跨國企業級別的行銷戰鬥力。</p>
    <figure><img src="{urls[4]}" alt="團隊勝利" /><figcaption>圖 5：告別繁瑣報表，享受 AI 帶來的行銷紅利與成果</figcaption></figure>

    <h3>常見問題解答 (FAQ)</h3>
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {{
          "@type": "Question",
          "name": "n8n 部署在雲端還是本地比較好？",
          "acceptedAnswer": {{
            "@type": "Answer",
            "text": "如果您需要長期運行且不希望受限於電腦開機，建議使用 Docker 部署在 VPS 上。"
          }}
      ]
    }}
    </script>
    """

    print("🚀 正在發布文章 8：郵件自動化專題...")
    result = bridge.post_article(
        title=title,
        content=content,
        status='publish',
        categories=[56], 
        tags=[534, 42], 
        featured_media=featured_id
    )
    if result:
        print(f"✅ 文章 8 發布成功！ID: {result.get('id')}")

if __name__ == "__main__":
    post_article_8()
