import os
import sys
# 將專案根目錄加入 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.wp_bridge import WordPressBridge
from dotenv import load_dotenv
import json

def get_post_content(post_id):
    load_dotenv()
    WP_SITE = os.getenv("WP_SITE")
    WP_USER = os.getenv("WP_USER")
    WP_PWD = os.getenv("WP_PWD")
    
    bridge = WordPressBridge(WP_SITE, WP_USER, WP_PWD)
    
    post_url = f"{bridge.site_url}/wp-json/wp/v2/posts/{post_id}"
    response = bridge.session.get(post_url, auth=bridge.auth, headers=bridge.headers)
    
    if response.status_code == 200:
        post = response.json()
        output = {
            "id": post["id"],
            "title": post["title"]["rendered"],
            "content": post["content"]["rendered"],
            "categories": post["categories"],
            "tags": post["tags"],
            "featured_media": post["featured_media"]
        }
        with open(f"post_{post_id}.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"✅ Post {post_id} content saved to post_{post_id}.json")
    else:
        print(f"Failed to fetch post {post_id}: {response.status_code}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        get_post_content(sys.argv[1])
    else:
        print("Please provide a post ID.")
