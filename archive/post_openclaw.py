from wp_bridge import WordPressBridge
import os
from dotenv import load_dotenv

def post_openclaw_article():
    # 載入環境變數
    load_dotenv()
    
    WP_SITE = os.getenv("WP_SITE")
    WP_USER = os.getenv("WP_USER")
    WP_PWD = os.getenv("WP_PWD")

    if not all([WP_SITE, WP_USER, WP_PWD]):
        print("❌ 錯誤: .env 資訊不完整")
        return

    bridge = WordPressBridge(WP_SITE, WP_USER, WP_PWD)

    title = "OpenClaw：強大的開源 AI 自動化內容發布工具"
    content = """
    <h2>什麼是 OpenClaw？</h2>
    <p>OpenClaw 是一款功能強大的開源 AI 助手，專為自動化數位任務而設計。它能夠在用戶的機器上運行，連接各種通訊軟體，並整合眾多第三方工具來執行現實世界的任務。</p>

    <h3>OpenClaw 在內容自動化方面的核心功能</h3>
    <ul>
        <li><strong>內容生成與排程：</strong> OpenClaw 可以自動化內容創作流程，生成社交媒體貼文，並透過 Buffer 或 Hootsuite 等平台進行排程。它可以研究主題、撰寫草稿、格式化內容管理系統 (CMS)，並生成 Meta 描述。</li>
        <li><strong>語法適應與自動發布：</strong> 它能從現有內容中學習用戶的寫作風格（例如推文），並自動以該聲音生成新貼文，確保受眾參與度的一致性。</li>
        <li><strong>跨平台內容再利用：</strong> OpenClaw 可以將單一內容（如部落格文章）轉化為多種平台特定格式，如 Twitter 討論串、LinkedIn 貼文或 Instagram 說明，同時保持核心訊息不變。</li>
        <li><strong>發布工作流自動化：</strong> 用戶可以利用 OpenClaw 監測內容來源（如 YouTube 頻道），自動生成字幕和縮圖，然後定時將內容發布到 LinkedIn 等平台。</li>
    </ul>

    <h3>為什麼選擇 OpenClaw？</h3>
    <p>OpenClaw 能夠與網頁瀏覽器互動、執行腳本、管理檔案並整合各種 API，這使其成為執行進階內容自動化任務的理想選擇。對於希望提升生產力並保持穩定內容產出的數位行銷人員或開發者來說，OpenClaw 是一個值得關注的工具。</p>
    
    <p>透過將 OpenClaw 與 WordPress 結合，您可以實現從資訊採集、內容生成到自動發布的完整閉環，極大地提升內容營運效率。</p>
    """

    print("🚀 正在發布 OpenClaw 相關文章...")
    result = bridge.post_article(title, content, status='publish')
    
    if result:
        print(f"✅ 文章發布成功！ID: {result.get('id')}")
        print(f"🔗 連結: {result.get('link')}")
    else:
        print("❌ 文章發布失敗。")

if __name__ == "__main__":
    post_openclaw_article()
