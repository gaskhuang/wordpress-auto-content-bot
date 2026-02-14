from wp_bridge import WordPressBridge
import os
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
