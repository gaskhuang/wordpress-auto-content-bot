import requests
import base64
import os
from dotenv import load_dotenv

class DataForSEOBridge:
    def __init__(self, login=None, password=None):
        load_dotenv()
        self.login = login or os.getenv("DATAFORSEO_LOGIN")
        self.password = password or os.getenv("DATAFORSEO_PASSWORD")
        self.base_url = "https://api.dataforseo.com/v3"
        
        if not self.login or not self.password:
            print("⚠️ 警告: DataForSEO 憑證未設定。請在 .env 中加入 DATAFORSEO_LOGIN 與 DATAFORSEO_PASSWORD")
        
        # 建立 Basic Auth Header
        auth_bytes = f"{self.login}:{self.password}".encode('ascii')
        base64_auth = base64.b64encode(auth_bytes).decode('ascii')
        self.headers = {
            'Authorization': f'Basic {base64_auth}',
            'Content-Type': 'application/json'
        }

    def post(self, endpoint, data):
        """通用 POST 請求"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.post(url, headers=self.headers, json=data)
            return response.json()
        except Exception as e:
            print(f"❌ DataForSEO API 請求錯誤: {e}")
            return None

    def get_keywords_data(self, keywords, location_code=2158, language_code="zh_TW"):
        """獲取關鍵字搜尋量等數據 (預設台灣/繁中)"""
        endpoint = "keywords_data/google/search_volume/live"
        post_data = [{
            "keywords": keywords,
            "location_code": location_code,
            "language_code": language_code
        }]
        return self.post(endpoint, post_data)

if __name__ == "__main__":
    # 測試程式碼
    bridge = DataForSEOBridge()
    if bridge.login and bridge.password:
        print("🔍 正在嘗試呼叫 DataForSEO API...")
        # 這裡僅作結構測試，實際執行需有效憑證
        # result = bridge.get_keywords_data(["OpenClaw", "AI Automation"])
        # print(result)
    else:
        print("❌ 請先設定 .env 憑證。")
