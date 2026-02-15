
import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

class ImageGenBridge:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("❌ Warning: OPENAI_API_KEY not found. Image generation will fail.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)

    def generate_image(self, prompt, size="1024x1024", quality="standard"):
        """
        使用 DALL-E 3 生成圖片
        :param prompt: 圖片描述
        :return: 圖片的 URL 或 None
        """
        if not self.client:
            return None

        try:
            print(f"🎨 Generating image for: {prompt[:50]}...")
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality=quality,
                n=1,
            )
            image_url = response.data[0].url
            return image_url
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            return None

    def download_image(self, url, save_path):
        """下載圖片到本地"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            return False
        except Exception as e:
            print(f"❌ Image download failed: {e}")
            return False
