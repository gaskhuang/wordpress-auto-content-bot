from dataforseo_bridge import DataForSEOBridge
import json

def fetch_and_save_seo_data():
    bridge = DataForSEOBridge()
    keywords = ["OpenClaw", "AI Automation", "WordPress API", "Web Crawling 2026", "AEO vs SEO"]
    
    print(f"🔍 正在獲取關鍵字數據: {keywords}")
    result = bridge.get_keywords_data(keywords)
    
    if result and result.get("status_code") == 20000:
        with open("seo_data_report.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("✅ 數據獲取成功並儲存至 seo_data_report.json")
        
        # 簡單列印概況
        tasks = result.get("tasks", [])
        for task in tasks:
            for item in task.get("result", []):
                print(f"- {item.get('keyword')}: 搜尋量 {item.get('search_volume')}, 競爭度 {item.get('competition')}")
    else:
        print(f"❌ 數據獲取失敗: {result}")

if __name__ == "__main__":
    fetch_and_save_seo_data()
