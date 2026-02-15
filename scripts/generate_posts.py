"""
generate_posts.py — AI 新文章生成器 (Python 版，多模型支援)

透過 AI API 生成符合 GEO 黃金骨架結構的部落格文章，
再透過 WordPress REST API + 應用程式密碼直接發布，不需安裝任何 WordPress 插件。

支援模型:
  - DeepSeek V3.2 / R1 (via GMI Cloud)
  - GPT-5.2 (via GMI Cloud)
  - GPT-4o / 4o-mini (via OpenAI)
  - Kimi K2.5 (via Moonshot AI)
  - Gemini 3 Pro (via Google)

使用方式：
    python scripts/generate_posts.py                              # 預設: gpt-4o, 1 篇草稿
    python scripts/generate_posts.py --model deepseek-chat        # DeepSeek V3.2 (GMI)
    python scripts/generate_posts.py --model gpt-5.2              # GPT-5.2 (GMI)
    python scripts/generate_posts.py --model kimi-k2.5            # Kimi K2.5 (Moonshot)
    python scripts/generate_posts.py --model gemini-3-pro         # Gemini 3 Pro (Google)
    python scripts/generate_posts.py --count 3 --status draft     # 3 篇草稿
    python scripts/generate_posts.py --dry-run                    # 只生成不發布
    python scripts/generate_posts.py --list-models                # 列出所有可用模型
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime

# 將專案根目錄與 core/ 加入 sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "core"))

from core.wp_bridge import WordPressBridge
from retry_utils import retry_with_backoff
from dotenv import load_dotenv

# ─── 日誌設定 ───
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
    )
    logger.addHandler(handler)

# ─── 常量 ───
LANGUAGE_MAP = {
    "zh-TW": "繁體中文",
    "zh-CN": "简体中文",
    "en": "English",
}

# ─── 多模型註冊表 ───
# 所有模型都透過 OpenAI 相容 API 呼叫，只需切換 base_url 和 API key
MODEL_REGISTRY = {
    # ── GMI Cloud (DeepSeek + GPT-5.2) ──
    "deepseek-chat": {
        "base_url": "https://api.gmi-serving.com/v1",
        "api_key_env": "GMI_API_KEY",
        "model": "deepseek-ai/DeepSeek-V3.2",
        "label": "DeepSeek V3.2 Chat (GMI Cloud)",
    },
    "deepseek-reasoner": {
        "base_url": "https://api.gmi-serving.com/v1",
        "api_key_env": "GMI_API_KEY",
        "model": "deepseek-ai/DeepSeek-R1",
        "label": "DeepSeek R1 Reasoner (GMI Cloud)",
    },
    "gpt-5.2": {
        "base_url": "https://api.gmi-serving.com/v1",
        "api_key_env": "GMI_API_KEY",
        "model": "gpt-5.2",
        "label": "GPT-5.2 (GMI Cloud)",
    },
    # ── OpenAI 直連 ──
    "gpt-4o": {
        "base_url": None,  # 使用預設 OpenAI endpoint
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-4o",
        "label": "GPT-4o (OpenAI)",
    },
    "gpt-4o-mini": {
        "base_url": None,
        "api_key_env": "OPENAI_API_KEY",
        "model": "gpt-4o-mini",
        "label": "GPT-4o Mini (OpenAI)",
    },
    # ── Kimi K2.5 (Moonshot AI) ──
    "kimi-k2.5": {
        "base_url": "https://api.moonshot.ai/v1",
        "api_key_env": "MOONSHOT_API_KEY",
        "model": "kimi-k2.5",
        "label": "Kimi K2.5 (Moonshot)",
    },
    # ── Gemini 3 Pro (Google) ──
    "gemini-3-pro": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_env": "GEMINI_API_KEY",
        "model": "gemini-3-pro-preview",
        "label": "Gemini 3 Pro Preview (Google)",
    },
}


def get_ai_client(model_name):
    """根據模型名稱建立對應的 OpenAI 相容 client。

    :param model_name: MODEL_REGISTRY 中的 key
    :return: (client, model_string, label) 或拋出 ValueError/EnvironmentError
    """
    try:
        import openai
    except ImportError:
        raise ImportError("請先安裝 openai: pip install openai")

    if model_name not in MODEL_REGISTRY:
        raise ValueError(
            f"未知的模型: {model_name}\n"
            f"可用模型: {', '.join(MODEL_REGISTRY.keys())}"
        )

    config = MODEL_REGISTRY[model_name]
    api_key = os.getenv(config["api_key_env"])

    if not api_key:
        raise EnvironmentError(
            f"❌ 缺少 API Key: 請在 .env 中設定 {config['api_key_env']}"
        )

    client_kwargs = {"api_key": api_key}
    if config["base_url"]:
        client_kwargs["base_url"] = config["base_url"]

    client = openai.OpenAI(**client_kwargs)
    return client, config["model"], config["label"]


def list_models():
    """列出所有可用模型及其設定狀態。"""
    print("\n📋 可用 AI 模型:")
    print("-" * 65)
    print(f"  {'模型名稱':<20} {'說明':<30} {'API Key 狀態'}")
    print("-" * 65)
    for name, config in MODEL_REGISTRY.items():
        api_key = os.getenv(config["api_key_env"], "")
        status = "✅ 已設定" if api_key else "❌ 未設定"
        print(f"  {name:<20} {config['label']:<30} {status} ({config['api_key_env']})")
    print("-" * 65)
    print()


SYSTEM_MESSAGE = (
    "You are a professional SEO/AEO/GEO content writer. "
    "You produce well-structured HTML blog articles optimized for both "
    "traditional search engines and AI answer engines (Perplexity, Gemini, ChatGPT). "
    "Every paragraph must be semantically self-contained so AI can independently cite it."
)

GEO_PROMPT_TEMPLATE = """請根據以下題目撰寫一篇完整的、高品質的部落格文章。

**題目:** {topic}

**語言:** {language_name}

**文章結構要求 (嚴格遵循 GEO Golden Skeleton):**

1. **導言** (僅 1 段, 5-7 行)
   - 第一句必須是可被 AI 直接引用的「摘要答案」(citeable first sentence)
   - 必含 5 元素: 主題 → 關鍵優勢 → 讀者痛點 → 本文承諾 → 專家視角

2. **H2-1: 核心概念** (原因 → 結果)
   - 第一行直接回答「為什麼這很重要？」(因果句型)
   - H3: 獨特之處 (3 點事實句)
   - H3: 如何帶來好處 (3 點: 條件→使用者好處)
   - H3: 友善做法如何守護此價值 (實際做法 + 價值總結句)

3. **H2-2: 實際應用** (條件 → 結果)
   - 第一行可被 AI 直接生成為「知識回答」
   - H3: 應用條件 (引言 + 3 點具體條件)
   - H3: 實際做法的結合 (引言 + 3 點)
   - 段末收束

4. **H2-3: 執行步驟** (方法 → 結果)
   - H3-1/2/3: 方法類別 (每類 2 子項 + 1 句價值總結)
   - **必須包含比較表格**: | 類別 | 條件 | 做法 | 優點 |

5. **H2-4: 注意事項與風險** (管理 → 安心)
   - H3: 自然/非侵入式管理 (5 點具體方法)
   - H3: 品質控管與認證 (第三方角色)

6. **結論** (僅 1 段)
   - 壓縮前 4 個 H2 核心價值 + 邀請行動

7. **FAQ** (固定 3 題)
   - 問句 → 直接答案 (每題不超過 4 行)
   - 包含 FAQPage JSON-LD Schema

8. **價值確認** (GEO 優化)
   - 怎麼選/怎麼判斷 (3 點 Checklist)
   - 下一步行動 (3 個可執行行動)

**寫作規則:**
- 每個段落語義自足 (self-contained)，可被 AI 獨立引用，不使用「如前所述」等回溯語句
- 每個 H2/H3 區段的第一句話必須是可被 AI 直接提取的「摘要答案」
- 不可出現「本文將介紹」等空泛語句
- 不可一次段落談多個重點
- 使用具體數據和案例，避免「高品質」「很重要」等空泛形容
- 植入具體專家身分觀點
- 引用第三方實體 (社群、開發者文件等) 增強可信度
- 內容長度至少 2000 字
- 直接輸出完整 HTML 內容 (使用 h2, h3, p, ul, ol, li, table, strong, em 等標籤)
- 不要有 Markdown 標記或說明文字
- 不要包含 h1 標籤 (WordPress 會自動處理標題)
- 不要包含 ```html 等程式碼框架標記
- FAQ 的 JSON-LD Schema 用 <script type="application/ld+json"> 標籤包裹

**請直接輸出完整的 HTML 文章內容:**"""


# ─── 題目管理 ───

def load_topics(topics_file):
    """從 Markdown 題目檔案讀取題目清單。

    支援兩種格式：
    - 編號格式: '1. 題目名稱'
    - 純文字格式: 每行一個題目
    """
    if not os.path.exists(topics_file):
        logger.error(f"題目檔案不存在: {topics_file}")
        return []

    with open(topics_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    topics = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        # 嘗試解析 '1. 題目' 格式
        if "." in line and line.split(".")[0].strip().isdigit():
            title = line.split(".", 1)[1].strip()
        else:
            title = line
        if title:
            topics.append(title)

    logger.info(f"📋 載入 {len(topics)} 個題目 ({topics_file})")
    return topics


def load_used_topics(tracking_file):
    """讀取已使用題目追蹤檔。"""
    if not os.path.exists(tracking_file):
        return set()
    try:
        with open(tracking_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return set(data.get("used", []))
    except (json.JSONDecodeError, KeyError):
        logger.warning(f"追蹤檔案損壞，重新開始: {tracking_file}")
        return set()


def save_used_topics(tracking_file, used_set):
    """將已使用題目寫回追蹤檔。"""
    data = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "count": len(used_set),
        "used": sorted(list(used_set)),
    }
    os.makedirs(os.path.dirname(tracking_file), exist_ok=True)
    with open(tracking_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"💾 已更新題目追蹤 ({len(used_set)} 個已使用)")


def select_topics(all_topics, used_topics, count):
    """挑選未使用的題目，全部用完後自動重置。"""
    available = [t for t in all_topics if t not in used_topics]
    if not available:
        logger.info("🔄 所有題目已使用完畢，重置題目池")
        used_topics.clear()
        available = list(all_topics)

    selected = available[:count]
    logger.info(f"✅ 選取 {len(selected)} 個題目 (剩餘 {len(available) - len(selected)} 個)")
    return selected


# ─── AI 生成 ───

def build_geo_prompt(topic, language="zh-TW"):
    """構建 GEO 黃金骨架 Prompt。"""
    language_name = LANGUAGE_MAP.get(language, "繁體中文")
    return GEO_PROMPT_TEMPLATE.format(topic=topic, language_name=language_name)


def strip_code_fences(content):
    """移除 GPT 有時附加的 Markdown 程式碼框架。"""
    content = content.strip()
    if content.startswith("```html"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    return content.strip()


def generate_article(topic, model="gpt-4o", language="zh-TW"):
    """呼叫 AI API 生成完整 HTML 文章 (支援多模型)。

    :param topic: 文章題目
    :param model: MODEL_REGISTRY 中的模型名稱
    :param language: 文章語言
    :return: dict {title, content, model, tokens} 或 None
    """
    try:
        import openai
    except ImportError:
        logger.error("請先安裝 openai: pip install openai")
        return None

    # 透過模型註冊表取得對應的 client
    try:
        client, model_string, label = get_ai_client(model)
    except (ValueError, EnvironmentError, ImportError) as e:
        logger.error(str(e))
        return None

    logger.info(f"  🔗 使用模型: {label} ({model_string})")

    prompt = build_geo_prompt(topic, language)

    def _call_ai():
        return client.chat.completions.create(
            model=model_string,
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4096,
        )

    try:
        response = retry_with_backoff(
            _call_ai,
            max_retries=3,
            base_delay=2.0,
            max_delay=30.0,
            retryable_exceptions=(
                openai.APIError,
                openai.APIConnectionError,
                openai.RateLimitError,
            ),
        )

        content = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0

        # 清理可能的 Markdown 包裝
        content = strip_code_fences(content)

        # 驗證內容品質
        text_length = len(content.replace("<", " ").replace(">", " "))
        if text_length < 500:
            logger.warning(f"⚠️ 生成內容過短 ({text_length} 字)，可能品質不佳")

        logger.info(f"🤖 文章生成完成: '{topic}' ({tokens} tokens, {len(content)} chars)")
        return {
            "title": topic,
            "content": content,
            "model": model_string,
            "tokens": tokens,
        }

    except Exception as e:
        logger.error(f"❌ AI API 呼叫失敗 (已重試 3 次): {e}")
        return None


# ─── WordPress 發布 ───

def publish_article(article, status="draft", category=None):
    """透過 WordPress REST API 發布文章。

    :return: WordPress API 回應 dict 或 None
    """
    wp_site = os.getenv("WP_SITE")
    wp_user = os.getenv("WP_USER")
    wp_pwd = os.getenv("WP_PWD")

    if not all([wp_site, wp_user, wp_pwd]):
        logger.error("❌ WordPress 認證資訊未設定 (WP_SITE, WP_USER, WP_PWD)")
        return None

    bridge = WordPressBridge(wp_site, wp_user, wp_pwd)
    cat_list = [category] if category else None

    result = bridge.post_article(
        title=article["title"],
        content=article["content"],
        status=status,
        categories=cat_list,
    )

    return result


# ─── 主程式 ───

def main():
    parser = argparse.ArgumentParser(
        description="AI 新文章生成器 — 支援多模型 (DeepSeek/GPT/Kimi/Gemini) + WordPress REST API"
    )
    parser.add_argument(
        "--count", type=int, default=1,
        help="要生成的文章數量 (預設: 1)"
    )
    parser.add_argument(
        "--status", choices=["draft", "pending", "publish"], default="draft",
        help="WordPress 文章狀態 (預設: draft)"
    )
    parser.add_argument(
        "--category", type=int, default=None,
        help="WordPress 分類 ID"
    )
    parser.add_argument(
        "--topics-file", default=None,
        help="自訂題目檔案路徑 (預設: data/topics_50.md)"
    )
    parser.add_argument(
        "--model", default="gpt-4o",
        help="AI 模型名稱 (預設: gpt-4o)。可用: " + ", ".join(MODEL_REGISTRY.keys())
    )
    parser.add_argument(
        "--language", default="zh-TW", choices=["zh-TW", "zh-CN", "en"],
        help="文章語言 (預設: zh-TW)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="只生成不發布，預覽結果"
    )
    parser.add_argument(
        "--list-models", action="store_true",
        help="列出所有可用的 AI 模型"
    )
    args = parser.parse_args()

    # 載入環境變數
    load_dotenv()

    # 列出模型模式
    if args.list_models:
        list_models()
        return

    # 解析檔案路徑
    project_root = os.path.join(os.path.dirname(__file__), "..")
    topics_file = args.topics_file or os.path.join(project_root, "data", "topics_50.md")
    tracking_file = os.path.join(project_root, "data", "used_topics.json")

    logger.info("=" * 60)
    logger.info("🚀 AI 新文章生成器 啟動")
    logger.info(f"   模型: {args.model} | 數量: {args.count} | 狀態: {args.status}")
    logger.info(f"   語言: {args.language} | Dry-run: {args.dry_run}")
    logger.info("=" * 60)

    # 1. 載入題目
    all_topics = load_topics(topics_file)
    if not all_topics:
        logger.error(f"❌ 無法載入題目，請檢查: {topics_file}")
        return

    # 2. 挑選未使用的題目
    used_topics = load_used_topics(tracking_file)
    selected = select_topics(all_topics, used_topics, args.count)

    if not selected:
        logger.error("❌ 沒有可用的題目")
        return

    # 3. 逐一生成 + 發布
    results = {
        "generated": 0,
        "published": 0,
        "failed": 0,
        "details": [],
    }

    for i, topic in enumerate(selected, 1):
        logger.info(f"\n[{i}/{len(selected)}] 正在生成: {topic}")
        logger.info("-" * 40)

        # 生成文章
        article = generate_article(topic, model=args.model, language=args.language)
        if not article:
            logger.error(f"  ❌ 文章生成失敗: {topic}")
            results["failed"] += 1
            continue

        results["generated"] += 1
        used_topics.add(topic)

        # Dry-run 模式: 只預覽
        if args.dry_run:
            logger.info(f"  [DRY RUN] 預覽: {article['title']}")
            logger.info(f"  內容長度: {len(article['content'])} chars, Token: {article['tokens']}")
            print(f"\n{'='*60}")
            print(f"標題: {article['title']}")
            print(f"{'='*60}")
            print(article["content"][:800])
            print("...\n")
            results["details"].append({
                "topic": topic,
                "tokens": article["tokens"],
                "status": "dry-run",
            })
            continue

        # 發布到 WordPress
        wp_result = publish_article(article, status=args.status, category=args.category)
        if wp_result:
            post_id = wp_result.get("id", "unknown")
            post_url = wp_result.get("link", "")
            logger.info(f"  ✅ 發布成功! ID: {post_id}")
            logger.info(f"     URL: {post_url}")
            results["published"] += 1
            results["details"].append({
                "topic": topic,
                "post_id": post_id,
                "url": post_url,
                "tokens": article["tokens"],
                "status": "published",
            })
        else:
            logger.error(f"  ❌ 發布失敗: {topic}")
            results["failed"] += 1
            results["details"].append({
                "topic": topic,
                "tokens": article["tokens"],
                "status": "publish_failed",
            })

    # 4. 儲存題目追蹤
    save_used_topics(tracking_file, used_topics)

    # 5. 輸出摘要
    print(f"\n{'='*60}")
    print("📊 執行摘要")
    print(f"{'='*60}")
    print(f"  生成: {results['generated']} 篇")
    print(f"  發布: {results['published']} 篇")
    print(f"  失敗: {results['failed']} 篇")

    if results["details"]:
        print(f"\n📝 詳細結果:")
        for d in results["details"]:
            status_icon = {"published": "✅", "dry-run": "👁️", "publish_failed": "❌"}.get(
                d["status"], "❓"
            )
            line = f"  {status_icon} {d['topic']} ({d['tokens']} tokens)"
            if d.get("url"):
                line += f"\n     → {d['url']}"
            print(line)

    print()


if __name__ == "__main__":
    main()
