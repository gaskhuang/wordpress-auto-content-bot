from wp_bridge import WordPressBridge
import os
from dotenv import load_dotenv
import json

def post_structured_article():
    load_dotenv()
    
    WP_SITE = os.getenv("WP_SITE")
    WP_USER = os.getenv("WP_USER")
    WP_PWD = os.getenv("WP_PWD")

    bridge = WordPressBridge(WP_SITE, WP_USER, WP_PWD)

    # 1. 上傳圖片
    img1_path = "/Users/gask/.gemini/antigravity/brain/ef062b39-e55b-4cd2-ad09-240191f8039a/openclaw_master_visual_1771047521908.png"
    img2_path = "/Users/gask/.gemini/antigravity/brain/ef062b39-e55b-4cd2-ad09-240191f8039a/openclaw_features_infographic_1771047592740.png"
    
    media1 = bridge.upload_media(img1_path, "OpenClaw AI Automation Brain")
    media2 = bridge.upload_media(img2_path, "OpenClaw Feature Infographic")
    
    featured_media_id = media1.get('id') if media1 else None
    infographic_url = media2.get('source_url') if media2 else ""

    # 2. 準備符合 AEO/SEO 的內容 (HTML + JSON-LD)
    title = "OpenClaw 完整指南：2025 AI 自動化內容發布與網頁爬取神器"
    
    # 針對 AEO 的 JSON-LD 結構化資料
    faq_schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "什麼是 OpenClaw？",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "OpenClaw 是一個開源的 AI 助手框架，專門設計用於網頁自動化爬取、AI 內容生成與跨平台自動發布。它能幫助用戶自動整合網路資訊並優化發布流程。"
                }
            },
            {
                "@type": "Question",
                "name": "OpenClaw 支援 WordPress 嗎？",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": "是的，透過 WordPress REST API，OpenClaw 可以輕鬆與 WordPress 整合，實現內容的自動撰寫與發布。"
                }
            }
        ]
    }

    content = f"""
    <script type="application/ld+json">{json.dumps(faq_schema)}</script>

    <p><strong>OpenClaw 是什麼？</strong> OpenClaw 是一個開源的 AI 助手框架，專注於網頁自動化爬取、AI 內容生成與跨平台自動發布。它能幫助數位行銷人員與開發者快速採集資訊，並利用大型語言模型 (LLM) 轉化為高品質的文章，是 2025 年內容營運的必備神器。</p>
    
    <div id="ez-toc-container" style="background: #f9f9f9; padding: 15px; border: 1px solid #ddd; margin-bottom: 20px;">
        <p style="font-weight: bold; margin-top: 0;">文章目錄</p>
        <ul>
            <li><a href="#definition">OpenClaw 核心定義與趨勢</a></li>
            <li><a href="#features">三大核心功能解析</a></li>
            <li><a href="#workflow">自動化發布工作流實戰</a></li>
            <li><a href="#faq">常見問題 (FAQ)</a></li>
        </ul>
    </div>

    <h2 id="definition">OpenClaw：開啟 AI 自動化內容的新時代</h2>
    <p>在資訊爆炸的時代，如何快速獲取有價值的內容並進行二次創作是SEO成功的關鍵。OpenClaw 透過強大的瀏覽器模擬技術，能夠穿透複雜的網頁結構。與傳統爬蟲不同，OpenClaw 結合了 AI 的語境理解能力，能自動識別文章主體，剔除廣告與不相干資訊。</p>

    <h2 id="features">OpenClaw 三大核心功能</h2>
    <p>OpenClaw 的強大之處在於其將「採集 -> 處理 -> 發布」三個步驟完美融合。以下是其核心優勢：</p>
    <ul>
        <li><strong>網頁數據採集 (Web Crawling)：</strong> 模擬真實用戶行為，規避 WAF 防火牆，高效獲取原始資料。</li>
        <li><strong>AI 內容生成 (AI Content Generation)：</strong> 支援 GPT-4 等最新模型，根據採集到的素材自動撰寫符合 SEO 標準的文章。</li>
        <li><strong>自動化跨平台發布 (Automated Publishing)：</strong> 一鍵推送到 WordPress、LinkedIn 或 Twitter 分享。</li>
    </ul>

    {"<figure style='text-align:center;'><img src='"+infographic_url+"' alt='OpenClaw 功能說明圖' /><figcaption>OpenClaw 核心運作流程圖</figcaption></figure>" if infographic_url else ""}

    <h2 id="workflow">實戰：將 OpenClaw 與 WordPress 串接</h2>
    <p>透過 WordPress REST API 以及 Application Passwords，您可以建立一個無縫的內容生產線：</p>
    <ol>
        <li><strong>設定環境：</strong> 配置 .env 檔案中的網站 URL 與驗證資訊。</li>
        <li><strong>採集資訊：</strong> 設定 OpenClaw 掃描目標行業的最新資訊。</li>
        <li><strong>AI 優化：</strong> 利用 Gasker Content Refresher 等插件進行 SEO 二次改寫。</li>
        <li><strong>自動排程：</strong> 腳本自動提交至 WordPress 後台，節省 90% 的手動操作時間。</li>
    </ol>

    <h2 id="faq">常見問題 (FAQ)</h2>
    <h3>問：OpenClaw 會影響網站安全性嗎？</h3>
    <p>答：不會。它是透過標準的 API 協議進行存取，且支援最新的驗證機制。只要管理好您的應用程式密碼，安全性非常有保障。</p>
    
    <h3>問：使用 AI 生成的文章會被搜尋引擎懲罰嗎？</h3>
    <p>答：只要文章內容對用戶有價值，且經過適當的編輯與結構化優化（如 AEO 標準），AI 生成內容是被搜尋引擎所接受甚至青睞的。</p>

    <hr />
    <p><em>註：本文內容由 AI 助手透過 OpenClaw 與 WordPress 串接工具自動發布與優化。</em></p>
    """

    print("🚀 正在發布圖文並茂的 AEO/SEO 優化篇文章...")
    result = bridge.post_article(
        title=title, 
        content=content, 
        status='publish', 
        categories=[1], # 您可以根據後台分類 ID 調整
        featured_media=featured_media_id
    )
    
    if result:
        print(f"✅ 完美發布成功！ID: {result.get('id')}")
        print(f"🔗 連結: {result.get('link')}")
    else:
        print("❌ 發布失敗。")

if __name__ == "__main__":
    post_structured_article()
