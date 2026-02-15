"""
trend_analyzer.py — AI 趨勢分析器

用途：讀取 raw_trends.json，用 LLM 篩選出有價值的 AEO/GEO 寫作技巧。
輸出：analyzed_tips.json

使用方式：
    python trend_analyzer.py                        # 分析 raw_trends.json
    python trend_analyzer.py --input custom.json    # 分析指定檔案
    python trend_analyzer.py --dry-run              # 僅顯示分析結果，不寫入
"""

import os
import json
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(handler)

BASE_DIR = os.path.dirname(__file__)
DEFAULT_INPUT = os.path.join(BASE_DIR, "raw_trends.json")
DEFAULT_OUTPUT = os.path.join(BASE_DIR, "analyzed_tips.json")
FRAMEWORK_PATH = os.path.join(BASE_DIR, "geo_framework.md")

# AI 分析 Prompt
ANALYSIS_PROMPT = """你是 SEO/AEO/GEO 寫作規範的維護者。你的任務是從社群媒體貼文中提取「可直接應用於繁體中文部落格」的寫作技巧。

## 現有規範摘要
{existing_framework}

## 本週採集的社群討論
{raw_posts}

## 輸出要求
請篩選出最多 5 條有價值的新技巧，以 JSON 陣列格式回傳：
```json
[
  {{
    "tip": "技巧描述 (繁體中文，一句話)",
    "detail": "詳細說明如何在文章中應用此技巧 (2-3 句)",
    "applicable_section": "適用的骨架區塊 (如：導言、H2-1、FAQ 等)",
    "expected_effect": "預期效果 (如：提升 AI 引用率 20%)",
    "source_url": "原始貼文 URL",
    "confidence": "high/medium/low"
  }}
]
```

## 篩選規則
1. 排除純推銷或自我宣傳的貼文
2. 排除無數據支撐的個人猜測
3. 排除僅適用於英文的技巧
4. 優先保留有具體數據或案例支持的技巧
5. 與現有規範重複的技巧不要列入
"""


def load_existing_framework():
    """讀取現有的 geo_framework.md 作為比對基準"""
    try:
        with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        # 只取「核心骨架」區塊作為摘要 (節省 Token)
        if "## 二、進階技巧庫" in content:
            return content.split("## 二、進階技巧庫")[0]
        return content[:2000]
    except FileNotFoundError:
        logger.warning(f"找不到 {FRAMEWORK_PATH}，將使用預設規範")
        return "(尚無現有規範)"


def analyze_with_openai(raw_posts, existing_framework):
    """使用 OpenAI API 進行趨勢分析"""
    try:
        import openai
    except ImportError:
        logger.error("請先安裝 openai: pip install openai")
        return []

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("⚠️ 未設定 OPENAI_API_KEY，嘗試使用本地分析模式")
        return analyze_locally(raw_posts)

    client = openai.OpenAI(api_key=api_key)

    # 準備貼文摘要 (限制 Token 消耗)
    posts_text = ""
    for i, post in enumerate(raw_posts[:30]):  # 最多 30 篇
        posts_text += f"\n---\n[{i+1}] 來源: {post.get('source')} | 互動: {post.get('engagement', 0)}\n"
        posts_text += f"內容: {post.get('text', '')[:300]}\n"
        posts_text += f"URL: {post.get('url', '')}\n"

    prompt = ANALYSIS_PROMPT.format(
        existing_framework=existing_framework[:1500],
        raw_posts=posts_text
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        result_text = response.choices[0].message.content
        result = json.loads(result_text)
        # 支援 {"tips": [...]} 或直接 [...]
        if isinstance(result, dict) and "tips" in result:
            return result["tips"]
        elif isinstance(result, list):
            return result
        else:
            logger.warning(f"AI 回傳格式異常: {type(result)}")
            return []
    except Exception as e:
        logger.error(f"OpenAI API 呼叫失敗: {e}")
        return []


def analyze_locally(raw_posts):
    """本地分析模式 (無需 API)：按互動量排序，提取高互動貼文"""
    logger.info("📝 使用本地分析模式 (按互動量排序)")
    tips = []
    seen_urls = set()
    for post in sorted(raw_posts, key=lambda x: x.get("engagement", 0), reverse=True)[:5]:
        url = post.get("url", "")
        if url in seen_urls:
            continue
        seen_urls.add(url)
        tips.append({
            "tip": post.get("title", post.get("text", "")[:80]),
            "detail": post.get("text", "")[:200],
            "applicable_section": "待人工分類",
            "expected_effect": f"互動量: {post.get('engagement', 0)}",
            "source_url": url,
            "confidence": "medium" if post.get("engagement", 0) > 50 else "low",
        })
    return tips


def main():
    parser = argparse.ArgumentParser(description="AEO/GEO 趨勢分析器")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="輸入的原始趨勢 JSON 檔案")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="輸出的分析結果 JSON 檔案")
    parser.add_argument("--dry-run", action="store_true", help="僅顯示結果，不寫入檔案")
    args = parser.parse_args()

    # 讀取原始資料
    if not os.path.exists(args.input):
        logger.error(f"❌ 找不到 {args.input}，請先執行 trend_scraper.py")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        raw_posts = json.load(f)

    logger.info(f"📖 讀取了 {len(raw_posts)} 篇原始貼文")

    # 讀取現有規範
    existing_framework = load_existing_framework()

    # AI 分析
    tips = analyze_with_openai(raw_posts, existing_framework)

    logger.info(f"✅ 分析完成，產出 {len(tips)} 條新技巧")

    for i, tip in enumerate(tips):
        logger.info(f"  [{i+1}] {tip.get('tip', '')} (信心度: {tip.get('confidence', 'unknown')})")

    if not args.dry_run and tips:
        output_data = {
            "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_file": args.input,
            "total_raw_posts": len(raw_posts),
            "tips": tips,
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        logger.info(f"💾 已儲存至 {args.output}")


if __name__ == "__main__":
    main()
