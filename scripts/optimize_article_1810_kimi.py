import os
import sys
import json
import re

# 將專案根目錄加入 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.wp_bridge import WordPressBridge
from core.kimi_bridge import KimiBridge
from dotenv import load_dotenv

# 嚴格的寫作架構提示詞
STRUCTURE_LOCK_PROMPT = """
你是一位結合 SEO、AEO 與 GEO 的專業內容策略顧問。請依照以下嚴格規範，為主題「國際研討會 – 臨時IT網路支援」重新撰寫一篇文章。

⚠️ **重要規範：所有輸出內容必須使用「繁體中文 (台灣使用者習慣用語)」。嚴禁使用簡體中文或中國大陸用語（如：信息、質量、視頻、互聯網等，請改為：資訊、品質、影片、網際網路）。**

一、角色與寫作定位
- 以產業內行人/專家視角撰寫
- 滿足：人類讀者（好讀）、搜尋引擎（好收錄）、AI 助手（好引用）
- 採用倒金字塔結構 + 問題導向
- 每一段都必須能獨立被擷取摘要

二、文章固定骨架 (Structure Lock) - 嚴禁更動順序與數量！

1. 導言 (5-7行)
   - 第一句：直接給出摘要答案 (AEO)
   - 必須包含：地點/主題、關鍵優勢、讀者痛點、本文承諾、專家立場
   - 禁止故事鋪陳

2. H2-1：核心條件 A (原因→結果)
   - 第一行：因果句型回答「為什麼 A 重要？」
   - H3：A 的獨特之處 (3點，完整事實)
   - H3：A 如何帶來好處 (3點，具體結果)
   - H3：友善做法 (具体做法 + 價值總結句)

3. H2-2：核心條件 B (條件→結果)
   - 第一行：AI 知識型回答
   - H3：B 的條件 (引言 + 3點標準)
   - H3：B × 實際做法 (引言 + 3點結果)
   - 段末收束：B 為何不可取代

4. 圖片區塊 (必須存在)
   - 放置一個 <!-- IMAGE_PLACEHOLDER -->
   - 下方一句 Caption (可獨立成立)

5. H2-3：關鍵生產/執行流程 (方法→結果)
   - H3-1：方法類別 1 (條列 + 1句價值總結)
   - H3-2：方法類別 2 (同上)
   - H3-3：方法類別 3 (同上)
   - 本節總結句：將流程轉為信任感

6. 表格區塊 (必須存在)
   - 欄位：| 類別 | 材料/條件 | 做法 | 優點 |
   - 每一列都是決策資訊，無行銷形容詞

7. H2-4：安全與風險控管 (管理→安心)
   - H3：自然/非侵入式管理 (5點具體方法)
   - H3：品質控管與認證 (檢測方式、追溯機制、第三方角色)

8. H2：結論 (僅1段)
   - 壓縮前述核心價值
   - 明確下一步行動 (了解/選擇/支持)

9. H2：快速 FAQ (固定3題)
   - 問句 + 第一句直接答案 (≤4行)

10. 價值確認與行動引導 (GEO)
    - Checklist：怎麼選/判斷 (3點決策準則)
    - 下一步行動 (3個：了解/支持/選擇)

三、輸出格式
- 請直接輸出 HTML 程式碼 (不含 ```html 標記)
- 標題使用對應的 <h2>, <h3>, <ul>, <li>, <table> 等標籤
- **嚴禁**出現「本文將介紹」、「接下來」等轉折廢話
- **嚴禁**空泛形容詞

請開始撰寫：
"""

def optimize_article_kimi():
    load_dotenv()
    
    # 1. 初始化
    wp = WordPressBridge(os.getenv("WP_SITE"), os.getenv("WP_USER"), os.getenv("WP_PWD"))
    kimi = KimiBridge(os.getenv("MOONSHOT_API_KEY"))
    post_id = 1810

    if not kimi.api_key:
        print("❌ 錯誤: 未設定 MOONSHOT_API_KEY，無法執行 Kimi 優化。")
        return

    print(f"🚀 開始使用 Kimi 2.5 優化文章 {post_id} (強制繁體中文)...")

    # 2. 呼叫 Kimi 生成內容
    messages = [
        {"role": "system", "content": "You are a strict content strategist. You MUST write in Traditional Chinese (Taiwan)."},
        {"role": "user", "content": STRUCTURE_LOCK_PROMPT}
    ]
    
    content = kimi.chat_completion(messages, use_thinking=True)
    
    if not content:
        print("❌ Kimi 生成失敗，終止程序。")
        return

    # 移除可能的 markdown code block 標記
    content = re.sub(r"^```html", "", content, flags=re.MULTILINE)
    content = re.sub(r"^```", "", content, flags=re.MULTILINE)
    
    # 3. 補充 JSON-LD (壓縮為單行以避免 wpautop 或 WordPress 編輯器破壞 <script> 標籤)
    # 使用 json.dumps 確保格式正確且無換行
    faq_data = {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": [
        {
          "@type": "Question",
          "name": "為什麼國際研討會需要企業級 WiFi？",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "因為家用設備無法負荷數百人同時連線的高密度壓力，只有企業級 AP 能透過負載平衡確保連線穩定不中斷。"
          }
        },
        {
          "@type": "Question",
          "name": "臨時網路支援包含哪些具體服務？",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "包含活動前的場域訊號勘查、熱圖規劃，以及活動期間的資深工程師全程駐點，確保 5 分鐘內排除故障。"
          }
        },
        {
          "@type": "Question",
          "name": "如何確保活動期間的網路資安？",
          "acceptedAnswer": {
            "@type": "Answer",
            "text": "透過獨立的 VLAN 切割、用戶隔離技術以及強制登入頁面 (Captive Portal) 來管理存取權限並阻擋惡意攻擊。"
          }
        }
      ]
    }
    
    import base64
    # 轉換為 JSON string
    json_string = json.dumps(faq_data, ensure_ascii=False)
    
    # Base64 編碼以避免 WordPress Shortcode 解析問題 (特別是 ] 符號)
    json_b64 = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
    
    # 使用 Shortcode 包裝
    faq_schema = f'[gasker_schema]{json_b64}[/gasker_schema]'
    
    final_content = content + "\n\n" + faq_schema

    # 4. 生成與上傳圖片
    try:
        from core.image_gen_bridge import ImageGenBridge
        img_gen = ImageGenBridge()
        
        if img_gen.client:
            print("🎨 開始生成圖片...")
            
            # A. 精選圖片 (Title)
            feat_img_prompt = f"A professional, high-quality, realistic photo for a business article titled: {new_title}. Concept: Modern IT support, seminars, high-tech network stability."
            feat_img_url = img_gen.generate_image(feat_img_prompt)
            feat_media_id = None
            
            if feat_img_url:
                local_path = f"featured_{post_id}.png"
                if img_gen.download_image(feat_img_url, local_path):
                    media_res = wp.upload_media(local_path, title=new_title)
                    if media_res:
                        feat_media_id = media_res.get('id')
                        print(f"✅ 精選圖片上傳成功 ID: {feat_media_id}")
                    os.remove(local_path)

            # B. 內文圖片 (取代 <!-- IMAGE_PLACEHOLDER --> 及插入其他段落)
            # 這裡簡單解析前幾段文字作為 Prompt
            # 移除 HTML 標籤取純文字
            clean_text = re.sub(r'<[^>]+>', '', content)
            paragraphs = [p.strip() for p in clean_text.split('\n') if len(p.strip()) > 20]
            
            # 產生 3 張內文圖
            content_images = []
            for i in range(min(3, len(paragraphs))):
                prompt = f"Professional photo illustrating: {paragraphs[i][:100]}. Context: IT support, conference, network engineering, realistic style."
                img_url = img_gen.generate_image(prompt)
                if img_url:
                    l_path = f"content_{post_id}_{i}.png"
                    if img_gen.download_image(img_url, l_path):
                        m_res = wp.upload_media(l_path, title=f"Content Image {i+1}")
                        if m_res:
                            src = m_res.get('source_url') # 或 'guid' -> 'rendered'
                            # 嘗試獲取 source_url，如果是 None 則 fallback
                            if not src and 'guid' in m_res:
                                src = m_res['guid']['rendered']
                                
                            img_html = f'<figure class="wp-block-image size-large"><img src="{src}" alt="Content Image {i+1}"/></figure>'
                            content_images.append(img_html)
                        os.remove(l_path)
            
            # 插入圖片到內容中
            # 1. 取代 Placeholder
            if content_images:
                if "<!-- IMAGE_PLACEHOLDER -->" in final_content:
                    final_content = final_content.replace("<!-- IMAGE_PLACEHOLDER -->", content_images[0], 1)
                    # 剩餘圖片插入到 H2 之前
                    remaining_imgs = content_images[1:]
                else:
                    remaining_imgs = content_images

                # 簡單插入邏輯：插在 H2 標籤前
                parts = final_content.split('<h2>')
                new_assembled = parts[0]
                img_idx = 0
                for part in parts[1:]:
                    if img_idx < len(remaining_imgs):
                        new_assembled += remaining_imgs[img_idx] + "\n"
                        img_idx += 1
                    new_assembled += "<h2>" + part
                final_content = new_assembled

    except Exception as e:
        print(f"⚠️ 圖片生成流程發生錯誤 (不影響文章發布): {e}")

    # 5. 更新 WordPress
    new_title = "國際研討會臨時 IT 網路支援：高密度連線解決方案 (2026 AEO版)"
    
    print("🔄 正在寫入 WordPress...")
    result = wp.update_article(
        post_id=post_id,
        title=new_title,
        content=final_content,
        status="publish",
        featured_media=feat_media_id 
    )

    if result:
        print(f"✅ Kimi 優化成功！文章連結: {result.get('link')}")
    else:
        print("❌ 文章更新失敗。")

if __name__ == "__main__":
    optimize_article_kimi()
