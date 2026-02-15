import os
import requests
import json
import logging
from dotenv import load_dotenv

# 設定日誌
logger = logging.getLogger(__name__)

class KimiBridge:
    def __init__(self, api_key=None):
        load_dotenv()
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        self.base_url = "https://api.moonshot.ai/v1"
        
        if not self.api_key:
            logger.warning("⚠️ Kimi API Key 未設定。請在 .env 中加入 MOONSHOT_API_KEY")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def chat_completion(self, messages, use_thinking=True):
        """
        呼叫 Kimi 2.5 API
        :param messages: 對話歷史列表 [{"role": "user", "content": "..."}]
        :param use_thinking: 是否啟用思考模式 (預設開啟)
        :return: 回傳生成的內容文字
        """
        endpoint = f"{self.base_url}/chat/completions"
        
        # 建構 payload
        payload = {
            "model": "kimi-k2.5",
            "messages": messages,
            "stream": False
        }
        
        # Kimi 2.5 特殊規範：thinking 開啟時，不能傳送 temperature/top_p/presence_penalty 等參數
        # 官方文件：This parameter cannot be modified for the kimi-k2.5 model.
        if use_thinking:
            payload["thinking"] = {"type": "enabled"}
            # 不設定 temperature, top_p, n, etc.
        else:
            payload["thinking"] = {"type": "disabled"}
            # 即使關閉，針對 k2.5 最好也不要傳送這些參數，除非確認 API 支援修改
            # 為了安全起見，這裡也移除，完全依賴模型預設值

        try:
            # Mask API Key for logging
            masked_key = f"{self.api_key[:6]}...{self.api_key[-4:]}" if self.api_key else "None"
            logger.info(f"🚀 發送 Kimi API 請求 (Thinking: {use_thinking}, Key: {masked_key})...")
            
            response = requests.post(endpoint, headers=self.headers, json=payload, timeout=120)
            
            if response.status_code != 200:
                logger.error(f"❌ Kimi API 錯誤: {response.status_code} - {response.text}")
                return None
                
            result = response.json()
            # 提取回覆內容
            content = result["choices"][0]["message"]["content"]
            return content

        except Exception as e:
            logger.error(f"❌ Kimi API 連線異常: {e}")
            return None

if __name__ == "__main__":
    # 測試
    bridge = KimiBridge()
    if bridge.api_key:
        print(bridge.chat_completion([{"role": "user", "content": "你好，請自我介紹"}]))
