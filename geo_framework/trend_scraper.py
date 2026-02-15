"""
trend_scraper.py — AEO/GEO 趨勢爬蟲 (Zero-API Mode + API Fallback)

用途：每週定時執行，採集關於 AEO、GEO、SEO 最新寫作技巧的討論貼文。
輸出：raw_trends.json

V2 升級說明：
  - 優先使用零 API 模式（requests 直接讀取 Reddit 公開 JSON + Google 搜尋）
  - 若有設定 API key，則自動升級為 API 模式（praw / tweepy）
  - 完全不需設定任何 API 憑證即可運作

使用方式：
    python trend_scraper.py                 # 完整爬取（自動選擇最佳模式）
    python trend_scraper.py --dry-run       # 測試模式，僅顯示搜尋結果數量
    python trend_scraper.py --source reddit # 僅爬 Reddit
    python trend_scraper.py --source web    # 僅爬 Google 搜尋
    python trend_scraper.py --mode api      # 強制使用 API 模式
"""

import os
import sys
import json
import logging
import argparse
import re
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))
from retry_utils import retry_with_backoff

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(handler)

# 搜尋關鍵字組
SEARCH_QUERIES = [
    "AEO SEO 2026",
    "GEO optimization generative engine",
    "AI search ranking tips",
    "answer engine optimization",
    "generative engine optimization strategy",
]

# Reddit 目標子版
REDDIT_SUBREDDITS = ["SEO", "bigseo", "TechSEO", "digital_marketing"]

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "raw_trends.json")

# ────────────────────────────────────────────
#  零 API 模式：Reddit 公開 JSON + requests
# ────────────────────────────────────────────

def scrape_reddit_zero_api(dry_run=False):
    """零 API 模式：透過 Reddit 公開 JSON 端點採集 AEO/GEO 討論"""
    import requests

    results = []
    headers = {
        "User-Agent": "GEO-Framework-Bot/2.0 (Zero-API Trend Scraper)"
    }

    for sub_name in REDDIT_SUBREDDITS:
        for query in SEARCH_QUERIES:
            url = f"https://www.reddit.com/r/{sub_name}/search.json"
            params = {
                "q": query,
                "sort": "new",
                "t": "month",
                "limit": 10,
                "restrict_sr": "true",
            }
            logger.info(f"🔍 [Zero-API] 搜尋 r/{sub_name}: {query}")

            try:
                def _fetch_reddit():
                    r = requests.get(url, headers=headers, params=params, timeout=10)
                    r.raise_for_status()
                    return r.json()

                try:
                    data = retry_with_backoff(
                        _fetch_reddit,
                        max_retries=3,
                        base_delay=2.0,
                        retryable_exceptions=(requests.exceptions.RequestException,),
                    )
                except requests.exceptions.RequestException:
                    logger.warning(f"r/{sub_name} 搜尋 '{query}' 重試後仍失敗，跳過")
                    continue
                posts = data.get("data", {}).get("children", [])

                for post_wrapper in posts:
                    post = post_wrapper.get("data", {})
                    # 過濾不相關內容（標題或內文中需包含關鍵字）
                    title = post.get("title", "")
                    selftext = post.get("selftext", "")
                    combined = (title + " " + selftext).lower()

                    # 至少需包含一個核心關鍵字
                    keywords = ["aeo", "geo", "generative engine", "answer engine",
                                "ai search", "ai optimization", "llm", "seo"]
                    if not any(kw in combined for kw in keywords):
                        continue

                    engagement = post.get("score", 0) + post.get("num_comments", 0)
                    created_utc = post.get("created_utc", 0)
                    post_date = datetime.utcfromtimestamp(created_utc).strftime("%Y-%m-%d") if created_utc else ""

                    results.append({
                        "source": "reddit",
                        "subreddit": sub_name,
                        "author": str(post.get("author", "unknown")),
                        "date": post_date,
                        "title": title,
                        "text": selftext[:1000] if selftext else "",
                        "engagement": engagement,
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                    })

                # 禮貌性延遲，避免被 Reddit 封鎖
                time.sleep(1)

            except Exception as e:
                logger.error(f"r/{sub_name} 搜尋 '{query}' 失敗: {e}")

    # 去重（依 URL）
    seen_urls = set()
    unique_results = []
    for r in results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    logger.info(f"📊 [Zero-API] Reddit 共採集 {len(unique_results)} 篇相關貼文")
    if dry_run:
        logger.info("[DRY RUN] 不寫入檔案")
    return unique_results


# ────────────────────────────────────────────
#  零 API 模式：Google 搜尋結果摘要
# ────────────────────────────────────────────

def scrape_web_search(dry_run=False):
    """
    零 API 模式：透過 requests 抓取 SEO/GEO 文章。
    注意：此函數設計為搭配外部工具 (search_web / read_url_content) 使用，
    或由使用者提供 URL 清單。

    單獨執行時，會嘗試讀取已知的高質量 SEO 網站 RSS/最新文章頁面。
    """
    import requests

    # 已知高品質 SEO 來源的 RSS / JSON feeds
    KNOWN_SOURCES = [
        {
            "name": "Search Engine Journal",
            "url": "https://www.searchenginejournal.com/category/seo/feed/",
            "type": "rss"
        },
        {
            "name": "Search Engine Land",
            "url": "https://searchengineland.com/feed",
            "type": "rss"
        },
    ]

    results = []
    headers = {
        "User-Agent": "GEO-Framework-Bot/2.0 (Zero-API Trend Scraper)"
    }

    for source in KNOWN_SOURCES:
        try:
            logger.info(f"🔍 [Zero-API] 讀取 {source['name']} RSS...")

            def _fetch_rss():
                r = requests.get(source["url"], headers=headers, timeout=10)
                r.raise_for_status()
                return r.text

            try:
                content = retry_with_backoff(
                    _fetch_rss,
                    max_retries=3,
                    base_delay=2.0,
                    retryable_exceptions=(requests.exceptions.RequestException,),
                )
            except requests.exceptions.RequestException:
                logger.warning(f"{source['name']} 重試後仍失敗，跳過")
                continue
            # 使用正則表達式提取 <item> 中的 <title> 和 <link>
            items = re.findall(
                r'<item>.*?<title><!\[CDATA\[(.*?)\]\]></title>.*?<link>(.*?)</link>.*?</item>',
                content,
                re.DOTALL
            )
            if not items:
                # 嘗試不帶 CDATA 的格式
                items = re.findall(
                    r'<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?</item>',
                    content,
                    re.DOTALL
                )

            geo_keywords = ["aeo", "geo", "generative engine", "answer engine",
                            "ai search", "ai overview", "llm optimization",
                            "structured data", "schema markup", "e-e-a-t"]

            for title, link in items[:30]:
                title_clean = title.strip()
                if any(kw in title_clean.lower() for kw in geo_keywords):
                    results.append({
                        "source": "web",
                        "site": source["name"],
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "title": title_clean,
                        "text": "",
                        "engagement": 0,
                        "url": link.strip(),
                    })

        except Exception as e:
            logger.error(f"{source['name']} 讀取失敗: {e}")

    logger.info(f"📊 [Zero-API] Web 共採集 {len(results)} 篇相關文章")
    if dry_run:
        logger.info("[DRY RUN] 不寫入檔案")
    return results


# ────────────────────────────────────────────
#  API 模式 (Fallback)：需要 API Key
# ────────────────────────────────────────────

def scrape_reddit_api(dry_run=False):
    """API 模式：使用 praw 採集 Reddit（需 REDDIT_CLIENT_ID / SECRET）"""
    try:
        import praw
    except ImportError:
        logger.warning("praw 未安裝，跳過 API 模式 Reddit 爬取")
        return []

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "GEO-Framework-Bot/2.0")

    if not client_id or not client_secret:
        logger.info("未設定 Reddit API 憑證，跳過 API 模式")
        return []

    reddit = praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )

    results = []
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    for sub_name in REDDIT_SUBREDDITS:
        try:
            subreddit = reddit.subreddit(sub_name)
            for query in SEARCH_QUERIES:
                logger.info(f"🔍 [API] 搜尋 r/{sub_name}: {query}")
                for post in subreddit.search(query, sort="new", time_filter="week", limit=10):
                    post_time = datetime.utcfromtimestamp(post.created_utc)
                    if post_time < one_week_ago:
                        continue
                    results.append({
                        "source": "reddit",
                        "subreddit": sub_name,
                        "author": str(post.author),
                        "date": post_time.strftime("%Y-%m-%d"),
                        "title": post.title,
                        "text": post.selftext[:1000] if post.selftext else "",
                        "engagement": post.score + post.num_comments,
                        "url": f"https://reddit.com{post.permalink}",
                    })
        except Exception as e:
            logger.error(f"r/{sub_name} 爬取失敗: {e}")

    logger.info(f"📊 [API] Reddit 共採集 {len(results)} 篇貼文")
    return results


def scrape_x_api(dry_run=False):
    """API 模式：使用 tweepy 採集 X（需 X_BEARER_TOKEN）"""
    try:
        import tweepy
    except ImportError:
        logger.warning("tweepy 未安裝，跳過 X 爬取")
        return []

    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        logger.info("未設定 X_BEARER_TOKEN，跳過 X 爬取")
        return []

    client = tweepy.Client(bearer_token=bearer_token)
    results = []

    for query in SEARCH_QUERIES:
        try:
            logger.info(f"🔍 [API] 搜尋 X: {query}")
            tweets = client.search_recent_tweets(
                query=f"{query} -is:retweet lang:en",
                max_results=20,
                tweet_fields=["created_at", "public_metrics", "author_id"],
            )
            if tweets.data:
                for tweet in tweets.data:
                    metrics = tweet.public_metrics or {}
                    engagement = (metrics.get("like_count", 0) +
                                  metrics.get("retweet_count", 0) +
                                  metrics.get("reply_count", 0))
                    if engagement < 5:
                        continue
                    results.append({
                        "source": "x",
                        "author": str(tweet.author_id),
                        "date": tweet.created_at.strftime("%Y-%m-%d") if tweet.created_at else "",
                        "text": tweet.text,
                        "engagement": engagement,
                        "url": f"https://x.com/i/status/{tweet.id}",
                    })
        except Exception as e:
            logger.error(f"X 搜尋 '{query}' 失敗: {e}")

    logger.info(f"📊 [API] X 共採集 {len(results)} 則推文")
    return results


# ────────────────────────────────────────────
#  主程式
# ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AEO/GEO 趨勢爬蟲 (Zero-API + API Fallback)")
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不寫入檔案")
    parser.add_argument("--source", choices=["reddit", "web", "x", "all"], default="all",
                        help="選擇爬取來源")
    parser.add_argument("--mode", choices=["auto", "api", "zero"], default="auto",
                        help="auto=自動偵測, api=強制 API, zero=強制零 API")
    args = parser.parse_args()

    all_results = []

    # 決定是否使用 API 模式
    has_reddit_api = bool(os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"))
    has_x_api = bool(os.getenv("X_BEARER_TOKEN"))

    use_api = (args.mode == "api") or (args.mode == "auto" and (has_reddit_api or has_x_api))
    use_zero = (args.mode == "zero") or (args.mode == "auto")

    if use_api:
        logger.info("🔑 偵測到 API 憑證，使用 API 模式")
    if use_zero:
        logger.info("🌐 啟用零 API 模式")

    # Reddit 爬取
    if args.source in ("reddit", "all"):
        if use_api and has_reddit_api and args.mode != "zero":
            all_results.extend(scrape_reddit_api(dry_run=args.dry_run))
        if use_zero:
            all_results.extend(scrape_reddit_zero_api(dry_run=args.dry_run))

    # Web 搜尋爬取
    if args.source in ("web", "all"):
        if use_zero:
            all_results.extend(scrape_web_search(dry_run=args.dry_run))

    # X 爬取（僅 API 模式）
    if args.source in ("x", "all"):
        if use_api and has_x_api:
            all_results.extend(scrape_x_api(dry_run=args.dry_run))

    # 去重 + 按互動量排序
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    unique_results.sort(key=lambda x: x.get("engagement", 0), reverse=True)

    logger.info(f"✅ 總共採集 {len(unique_results)} 篇內容（去重後）")

    if not args.dry_run and unique_results:
        output = {
            "scrape_date": datetime.now().strftime("%Y-%m-%d"),
            "scrape_method": "Zero-API" if use_zero else "API",
            "total_posts": len(unique_results),
            "posts": unique_results,
        }
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 已儲存至 {OUTPUT_FILE}")
    elif not unique_results:
        logger.warning("⚠️ 未採集到任何內容。")


if __name__ == "__main__":
    main()
