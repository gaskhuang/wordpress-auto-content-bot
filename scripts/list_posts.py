import os
import sys
# 將專案根目錄加入 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.wp_bridge import WordPressBridge
from dotenv import load_dotenv

def list_posts():
    load_dotenv()
    WP_SITE = os.getenv("WP_SITE")
    WP_USER = os.getenv("WP_USER")
    WP_PWD = os.getenv("WP_PWD")
    
    bridge = WordPressBridge(WP_SITE, WP_USER, WP_PWD)
    
    # 获取最近的 10 篇文章
    posts_url = f"{bridge.site_url}/wp-json/wp/v2/posts"
    params = {"per_page": 10, "status": "publish"}
    response = bridge.session.get(posts_url, auth=bridge.auth, headers=bridge.headers, params=params)
    
    if response.status_code == 200:
        posts = response.json()
        print("--- Recent Posts ---")
        for p in posts:
            print(f"ID: {p['id']}, Title: {p['title']['rendered']}")
    else:
        print(f"Failed to fetch posts: {response.status_code}")

if __name__ == "__main__":
    list_posts()
