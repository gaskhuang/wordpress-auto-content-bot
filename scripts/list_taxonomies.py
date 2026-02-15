import os
import sys
# 將專案根目錄加入 sys.path，讓 core/ 套件可被引入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.wp_bridge import WordPressBridge
from dotenv import load_dotenv
import json

def list_categories_and_tags():
    load_dotenv()
    WP_SITE = os.getenv("WP_SITE")
    WP_USER = os.getenv("WP_USER")
    WP_PWD = os.getenv("WP_PWD")
    
    bridge = WordPressBridge(WP_SITE, WP_USER, WP_PWD)
    
    cats = bridge.get_categories()
    tags = bridge.get_tags()
    
    print("--- Categories ---")
    for c in cats:
        print(f"ID: {c['id']}, Name: {c['name']}")
        
    print("\n--- Tags ---")
    for t in tags:
        print(f"ID: {t['id']}, Name: {t['name']}")

if __name__ == "__main__":
    list_categories_and_tags()
