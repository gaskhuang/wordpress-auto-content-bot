"""
trend_scraper.py — X (Twitter) 與 Reddit AEO/GEO 趨勢爬蟲

用途：每週定時執行，採集關於 AEO、GEO、SEO 最新寫作技巧的討論貼文。
輸出：raw_trends.json

使用方式：
    python trend_scraper.py                 # 完整爬取
    python trend_scraper.py --dry-run       # 測試模式，僅顯示搜尋結果數量
    python trend_scraper.py --source reddit # 僅爬 Reddit
    python trend_scraper.py --source x      # 僅爬 X
"""

import os
import json
import logging
import argparse
from datetime import datetime, timedelta
from dotenv import load_dotenv

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


def scrape_reddit(dry_run=False):
    """從 Reddit 採集 AEO/GEO 相關討論"""
    try:
        import praw
    except ImportError:
        logger.error("請先安裝 praw: pip install praw")
        return []

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT", "GEO-Framework-Bot/1.0")

    if not client_id or not client_secret:
        logger.warning("⚠️ 未設定 REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET，跳過 Reddit 爬取。")
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
                logger.info(f"🔍 搜尋 r/{sub_name}: {query}")
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

    logger.info(f"📊 Reddit 共採集 {len(results)} 篇貼文")
    if dry_run:
        logger.info("[DRY RUN] 不寫入檔案")
    return results


def scrape_x(dry_run=False):
    """從 X (Twitter) 採集 AEO/GEO 相關推文"""
    try:
        import tweepy
    except ImportError:
        logger.error("請先安裝 tweepy: pip install tweepy")
        return []

    bearer_token = os.getenv("X_BEARER_TOKEN")
    if not bearer_token:
        logger.warning("⚠️ 未設定 X_BEARER_TOKEN，跳過 X 爬取。")
        return []

    client = tweepy.Client(bearer_token=bearer_token)
    results = []
    one_week_ago = datetime.utcnow() - timedelta(days=7)

    for query in SEARCH_QUERIES:
        try:
            logger.info(f"🔍 搜尋 X: {query}")
            tweets = client.search_recent_tweets(
                query=f"{query} -is:retweet lang:en",
                max_results=20,
                tweet_fields=["created_at", "public_metrics", "author_id"],
            )
            if tweets.data:
                for tweet in tweets.data:
                    metrics = tweet.public_metrics or {}
                    engagement = metrics.get("like_count", 0) + metrics.get("retweet_count", 0) + metrics.get("reply_count", 0)
                    # 僅保留互動數 > 5 的推文（過濾垃圾訊息）
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

    logger.info(f"📊 X 共採集 {len(results)} 則推文")
    if dry_run:
        logger.info("[DRY RUN] 不寫入檔案")
    return results


def main():
    parser = argparse.ArgumentParser(description="AEO/GEO 趨勢爬蟲")
    parser.add_argument("--dry-run", action="store_true", help="測試模式，不寫入檔案")
    parser.add_argument("--source", choices=["x", "reddit", "all"], default="all", help="選擇爬取來源")
    args = parser.parse_args()

    all_results = []

    if args.source in ("reddit", "all"):
        all_results.extend(scrape_reddit(dry_run=args.dry_run))

    if args.source in ("x", "all"):
        all_results.extend(scrape_x(dry_run=args.dry_run))

    # 按互動量排序
    all_results.sort(key=lambda x: x.get("engagement", 0), reverse=True)

    logger.info(f"✅ 總共採集 {len(all_results)} 篇內容")

    if not args.dry_run and all_results:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 已儲存至 {OUTPUT_FILE}")
    elif not all_results:
        logger.warning("⚠️ 未採集到任何內容。請確認 API 憑證是否正確。")


if __name__ == "__main__":
    main()
