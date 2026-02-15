import requests
import json
import os
import logging
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv
from datetime import datetime

# 設定日誌
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(handler)

class WordPressBridge:
    def __init__(self, site_url, username, app_password):
        """
        初始化 WordPress 串接工具
        :param site_url: 網站網址 (例如 https://example.com)
        :param username: WordPress 使用者名稱
        :param app_password: 在後台產生的「應用程式密碼」
        """
        self.site_url = site_url.rstrip('/')
        self.posts_url = f"{self.site_url}/wp-json/wp/v2/posts"
        self.media_url = f"{self.site_url}/wp-json/wp/v2/media"
        self.categories_url = f"{self.site_url}/wp-json/wp/v2/categories"
        self.tags_url = f"{self.site_url}/wp-json/wp/v2/tags"
        self.auth = HTTPBasicAuth(username, app_password)
        # 使用 Session 保持 Cookie 狀態
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive"
        }

    def get_categories(self):
        """獲取所有分類"""
        try:
            response = self.session.get(self.categories_url, auth=self.auth, headers=self.headers, params={"per_page": 100})
            if response.status_code == 200:
                return response.json()
            logger.warning(f"取得分類失敗，狀態碼: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"取得分類時發生錯誤: {e}")
            return []

    def get_tags(self):
        """獲取所有標籤"""
        try:
            response = self.session.get(self.tags_url, auth=self.auth, headers=self.headers, params={"per_page": 100})
            if response.status_code == 200:
                return response.json()
            logger.warning(f"取得標籤失敗，狀態碼: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"取得標籤時發生錯誤: {e}")
            return []

    def upload_media(self, file_path, title=None):
        """
        上傳圖片到 WordPress 媒體庫
        :param file_path: 圖片檔案的本地路徑
        :param title: 媒體標題 (可選)
        :return: 成功則回傳媒體物件的 JSON 資料，失敗則回傳 None
        """
        if not os.path.exists(file_path):
            print(f"❌ 錯誤: 檔案不存在 {file_path}")
            return None

        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            media_headers = self.headers.copy()
            media_headers['Content-Disposition'] = f'attachment; filename={file_name}'
            # WordPress 需要正確的 Content-Type，常見圖片格式判斷
            if file_name.endswith('.png'):
                media_headers['Content-Type'] = 'image/png'
            elif file_name.endswith(('.jpg', '.jpeg')):
                media_headers['Content-Type'] = 'image/jpeg'
            elif file_name.endswith('.webp'):
                media_headers['Content-Type'] = 'image/webp'
            else:
                # 預設為通用二進位流，WordPress 會嘗試自動判斷
                media_headers['Content-Type'] = 'application/octet-stream'

            try:
                logger.info(f"📤 正在上傳媒體: {file_name}...")
                response = self.session.post(
                    self.media_url,
                    data=f,
                    auth=self.auth,
                    headers=media_headers,
                    timeout=30
                )
                if response.status_code == 201:
                    data = response.json()
                    logger.info(f"✅ 媒體上傳成功! ID: {data.get('id')}")
                    return data
                else:
                    logger.error(f"❌ 媒體上傳失敗! 狀態碼: {response.status_code}")
                    logger.debug(f"回應內容: {response.text}")
                    return None
            except Exception as e:
                logger.error(f"‼️ 上傳過程出錯: {e}")
                return None

    def post_article(self, title, content, status='pending', categories=None, tags=None, featured_media=None):
        """
        發布文章至 WordPress
        :param title: 文章標題
        :param content: 文章內容 (支持 HTML)
        :param status: 發布狀態 ('publish', 'pending', 'draft')
        :param categories: 分類 ID 列表 [1, 2]
        :param tags: 標籤 ID 列表 [3, 4]
        :param featured_media: 精選圖片的媒體 ID
        :return: 回傳 API 響應結果
        """
        data = {
            "title": title,
            "content": content,
            "status": status
        }
        
        if categories:
            data["categories"] = categories
        if tags:
            data["tags"] = tags
        if featured_media:
            data["featured_media"] = featured_media

        # 1. 先嘗試造訪首頁獲取 Cookie (規避 WAF)
        try:
            self.session.get(self.site_url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"⚠️ 預存取網站失敗: {e}")

        # 2. 正式發送 POST 請求
        post_headers = self.headers.copy()
        post_headers["Origin"] = self.site_url
        post_headers["Referer"] = self.site_url + "/"
        
        try:
            response = self.session.post(
                self.posts_url, 
                json=data, 
                auth=self.auth, 
                headers=post_headers,
                timeout=15
            )
            
            if response.status_code == 201:
                logger.info(f"✅ 成功發布文章: {title}")
                return response.json()
            else:
                logger.error(f"❌ 發布失敗! 狀態碼: {response.status_code}")
                if response.status_code == 403:
                    logger.warning("💡 提示: 伺服器拒絕了發文請求。這通常是防火牆(WAF)阻擋了 API 寫入動作。")
                    if "<title>" in response.text:
                        error_title = response.text.split('<title>')[1].split('</title>')[0]
                        logger.warning(f"伺服器回應標題: {error_title}")
                return None
        except Exception as e:
            logger.error(f"‼️ 請求過程發生錯誤: {e}")
            return None

    def update_article(self, post_id, title=None, content=None, status=None, categories=None, tags=None, featured_media=None):
        """
        更新已發布的文章
        :param post_id: 文章 ID
        :param title: 新標題 (可選)
        :param content: 新內容 (可選)
        :param status: 新狀態 (可選)
        :param categories: 新分類 ID 列表 (可選)
        :param tags: 新標籤 ID 列表 (可選)
        :param featured_media: 新精選圖片 ID (可選)
        :return: 回傳 API 響應結果
        """
        update_url = f"{self.posts_url}/{post_id}"
        data = {}
        
        if title: data["title"] = title
        if content: data["content"] = content
        if status: data["status"] = status
        if categories: data["categories"] = categories
        if tags: data["tags"] = tags
        if featured_media: data["featured_media"] = featured_media

        # 1. 預存取 (WAF Bypass)
        try:
            self.session.get(self.site_url, headers=self.headers, timeout=10)
        except Exception as e:
            print(f"⚠️ 預存取網站失敗: {e}")

        # 2. 發送 POST 請求 (WordPress API 更新也是用 POST)
        post_headers = self.headers.copy()
        post_headers["Origin"] = self.site_url
        post_headers["Referer"] = self.site_url + "/"

        try:
            logger.info(f"🔄 正在更新文章 ID: {post_id}...")
            response = self.session.post(
                update_url, 
                json=data, 
                auth=self.auth, 
                headers=post_headers,
                timeout=15
            )
            
            if response.status_code == 200:
                logger.info(f"✅ 成功更新文章: {post_id}")
                return response.json()
            else:
                logger.error(f"❌ 更新失敗! 狀態碼: {response.status_code}")
                if response.status_code == 403 and "<title>" in response.text:
                   error_title = response.text.split('<title>')[1].split('</title>')[0]
                   logger.warning(f"伺服器回應標題: {error_title}")
                return None
        except Exception as e:
            logger.error(f"‼️ 更新請求過程發生錯誤: {e}")
            return None

if __name__ == "__main__":
    # 載入環境變數
    load_dotenv()
    
    WP_SITE = os.getenv("WP_SITE")
    WP_USER = os.getenv("WP_USER")
    WP_PWD = os.getenv("WP_PWD")

    if not all([WP_SITE, WP_USER, WP_PWD]):
        print("❌ 錯誤: .env 檔案資訊不完整，請檢查 WP_SITE, WP_USER, WP_PWD")
    else:
        bridge = WordPressBridge(WP_SITE, WP_USER, WP_PWD)
        
        # 測試發文
        sample_title = f"來自 OpenCrawl 的診斷測試 ({datetime.now().strftime('%H:%M:%S')})"
        sample_content = "<p>這是一篇自動化發布的測試文章，用於診斷 API 存取權限。</p>"
        
        bridge.post_article(sample_title, sample_content)
