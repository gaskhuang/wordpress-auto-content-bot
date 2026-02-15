import os
import json
import time
from dotenv import load_dotenv

# 確保能從任何位置執行
import sys
sys.path.insert(0, os.path.dirname(__file__))

try:
    from core.wp_bridge import WordPressBridge
    from core.dataforseo_bridge import DataForSEOBridge
except ImportError:
    from wp_bridge import WordPressBridge
    from dataforseo_bridge import DataForSEOBridge
# 假設我們有一個 generate_image 的封裝，或是直接在邏輯中處理

class AutoContentFactory:
    def __init__(self):
        load_dotenv()
        self.wp = WordPressBridge(os.getenv("WP_SITE"), os.getenv("WP_USER"), os.getenv("WP_PWD"))
        self.seo = DataForSEOBridge()
        # 動態路徑：從 core/ 往上一層找 data/topics_50.md
        self.topics_file = os.path.join(os.path.dirname(__file__), "..", "data", "topics_50.md")
        
    def load_topics(self):
        with open(self.topics_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        topics = []
        for line in lines:
            if line.strip() and "." in line and not line.startswith("#"):
                # 簡單提取題目
                title = line.split(".", 1)[1].strip()
                topics.append(title)
        return topics

    def produce_article(self, topic):
        print(f"\n🏗️ 開始製作專題 (符合 2026 AEO 規範): {topic}")
        
        # 1. 獲取關鍵字數據 (實體化數據支撐)
        seo_info = self.seo.get_keywords_data([topic])
        # 提取真實數據供文中引用
        search_vol = "正在增長"
        if seo_info and seo_info.get("status_code") == 20000:
            res = seo_info.get("tasks", [{}])[0].get("result", [{}])[0]
            search_vol = f"每月約 {res.get('search_volume', '增長中')}"

        # 2. 規劃章節 (落實結構化萃取與實體化身份)
        chapters = [
            {
                "title": f"{topic}：為什麼專家邱小黑建議現在佈局？", 
                "prompt": f"A high-tech digital concept representing {topic}, futuristic.",
                "type": "entity_injection"
            },
            {
                "title": "核心技術架構：結構化拆解", 
                "prompt": f"Detailed technical blueprint for {topic}.",
                "type": "structured_list"
            },
            {
                "title": "實戰操作：3 步驟快速上手", 
                "prompt": "Automation workflow visualization.",
                "type": "steps"
            },
            {
                "title": "安全性與信任度：網友與社群討論焦點", 
                "prompt": "Secure AI brain visualization.",
                "type": "social_proof"
            },
            {
                "title": "未來展望：小弟的技術評語", 
                "prompt": "Human and AI working together.",
                "type": "personal_note"
            }
        ]
        
        # 3. 組合內容 (符合 Markdown for Agents 優化)
        content_body = f"<h2>{topic} 全方位指南 (AEO Optimized)</h2>"
        content_body += f"<p><strong>摘要：</strong> 根據 2026 最新市場觀察，{topic} 的搜尋趨勢 ({search_vol}) 顯示出強勁的 Agentic AI 特徵。本文將從實體經驗與結構化數據兩方面為您解析。</p>"
        
        for i, ch in enumerate(chapters):
            content_body += f"<h3>{i+1}. {ch['title']}</h3>"
            if ch['type'] == "entity_injection":
                content_body += f"<p>針對 {topic}，技術顧問 <strong>邱小黑</strong> 指出：這不僅是工具的更新，更是工作範式的轉移。根據我們在開發社群的觀察...</p>"
            elif ch['type'] == "structured_list":
                content_body += f"<ul><li><strong>關鍵參數 A</strong>：極致優化 Token</li><li><strong>關鍵參數 B</strong>：結構化讀取</li></ul>"
            elif ch['type'] == "steps":
                content_body += f"<ol><li>準備環境</li><li>串接 API</li><li>自動執行</li></ol>"
            else:
                content_body += f"<p>(此處包含約 200 字符合 AEO 的深度內容，埋入相關實體連結...)</p>"
            
            content_body += f"<!-- IMAGE_PLACEHOLDER_{i} -->"

        # 4. FAQ Schema (雙優化策略)
        content_body += f"""
        <script type="application/ld+json">
        {{
          "@context": "https://schema.org",
          "@type": "FAQPage",
          "mainEntity": [{{
            "@type": "Question",
            "name": "{topic} 的核心價值是什麼？",
            "acceptedAnswer": {{
              "@type": "Answer",
              "text": "其核心價值在於透過結構化資訊與 AI 代理實體，達成高效率的自動化決策。"
            }}
          }}]
        }}
        </script>
        <hr />
        <p><em>本文數據由 DataForSEO 提供，並落實 2026 AEO 實體化原則。</em></p>
        """
        
        return {
            "title": topic,
            "content": content_body,
            "chapters": chapters
        }

    def run_batch(self, count=1):
        all_topics = self.load_topics()
        articles = []
        for i in range(min(count, len(all_topics))):
            article = self.produce_article(all_topics[i])
            articles.append(article)
        return articles

if __name__ == "__main__":
    factory = AutoContentFactory()
    # topics = factory.load_topics()
    # print(topics)
