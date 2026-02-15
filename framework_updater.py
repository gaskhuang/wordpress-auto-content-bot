"""
framework_updater.py — 動態規範更新器

用途：讀取 analyzed_tips.json，安全地將新技巧插入 geo_framework.md。
      自動更新版本號、Changelog、並執行 git commit + push。

使用方式：
    python framework_updater.py                     # 正式更新
    python framework_updater.py --dry-run           # 預覽變更，不寫入
    python framework_updater.py --no-git            # 更新檔案但不 git commit
"""

import os
import re
import json
import logging
import argparse
import subprocess
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
FRAMEWORK_PATH = os.path.join(BASE_DIR, "geo_framework.md")
TIPS_INPUT = os.path.join(BASE_DIR, "analyzed_tips.json")

# 標記線：framework_updater 會在此標記之後插入新技巧
APPEND_MARKER = "<!-- ===== AUTO-APPEND ZONE: DO NOT EDIT BELOW THIS LINE ===== -->"
END_MARKER = "<!-- ===== END AUTO-APPEND ZONE ===== -->"


def get_current_week():
    """取得 ISO 週數格式，如 2026-W07"""
    now = datetime.now()
    return now.strftime("%G-W%V")


def get_current_version(content):
    """從 geo_framework.md 中解析目前版本號"""
    match = re.search(r'版本：v(\d+\.\d+)', content)
    if match:
        return match.group(1)
    return "1.0"


def bump_version(version):
    """遞增小版本號"""
    parts = version.split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def format_tips_as_markdown(tips, week_label):
    """將技巧列表格式化為 Markdown"""
    lines = [f"\n### {week_label} 新增技巧\n"]
    for tip in tips:
        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(tip.get("confidence", ""), "⚪")
        lines.append(f"- {confidence_emoji} **{tip.get('tip', '')}**")
        lines.append(f"  - 詳細：{tip.get('detail', '')}")
        lines.append(f"  - 適用區塊：`{tip.get('applicable_section', '通用')}`")
        lines.append(f"  - 預期效果：{tip.get('expected_effect', '待驗證')}")
        lines.append(f"  - 來源：[原文]({tip.get('source_url', '#')})")
        lines.append("")
    return "\n".join(lines)


def update_framework(tips, dry_run=False):
    """將新技巧安全地插入 geo_framework.md"""
    if not os.path.exists(FRAMEWORK_PATH):
        logger.error(f"❌ 找不到 {FRAMEWORK_PATH}")
        return False

    with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 解析版本
    old_version = get_current_version(content)
    new_version = bump_version(old_version)
    week_label = get_current_week()
    today = datetime.now().strftime("%Y-%m-%d")

    # 格式化新技巧
    new_tips_md = format_tips_as_markdown(tips, week_label)

    # 插入至 AUTO-APPEND ZONE
    if APPEND_MARKER not in content:
        logger.error(f"❌ 找不到插入標記: {APPEND_MARKER}")
        return False

    # 在 APPEND_MARKER 之後直接插入
    content = content.replace(
        APPEND_MARKER,
        APPEND_MARKER + "\n" + new_tips_md
    )

    # 更新版本號
    content = content.replace(f"版本：v{old_version}", f"版本：v{new_version}")

    # 更新「累計學習來源」數字
    learned_match = re.search(r'累計學習來源：(\d+) 篇', content)
    if learned_match:
        old_count = int(learned_match.group(1))
        new_count = old_count + len(tips)
        content = content.replace(f"累計學習來源：{old_count} 篇", f"累計學習來源：{new_count} 篇")

    # 更新「最後更新」日期
    content = re.sub(r'最後更新：\d{4}-\d{2}-\d{2}', f'最後更新：{today}', content)

    # 更新 Changelog 表格
    changelog_row = f"| {today} | v{new_version} | {len(tips)} | X/Reddit 自動採集 |"
    content = content.replace(
        "| 日期 | 版本 | 新增技巧數 | 來源 |",
        "| 日期 | 版本 | 新增技巧數 | 來源 |\n" + changelog_row
    )
    # 上面的替換會導致 header separator 行移位，修正
    content = content.replace(
        changelog_row + "\n|------|------|-----------|------|",
        "|------|------|-----------|------|\n" + changelog_row
    )

    if dry_run:
        logger.info(f"\n[DRY RUN] 預覽變更 (v{old_version} → v{new_version}):\n")
        logger.info(new_tips_md)
        return True

    # 寫入檔案
    with open(FRAMEWORK_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    logger.info(f"✅ geo_framework.md 已更新至 v{new_version}")
    logger.info(f"   新增 {len(tips)} 條技巧，累計學習來源已更新")
    return True


def git_commit_and_push():
    """自動 commit 並 push 變更"""
    try:
        week = get_current_week()
        subprocess.run(
            ["git", "add", "geo_framework.md", "analyzed_tips.json", "raw_trends.json"],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", f"auto: update geo_framework ({week}) - learned new tips"],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "push"],
            cwd=BASE_DIR, check=True, capture_output=True
        )
        logger.info("🚀 已自動 git commit + push")
    except subprocess.CalledProcessError as e:
        logger.error(f"Git 操作失敗: {e.stderr.decode() if e.stderr else e}")


def main():
    parser = argparse.ArgumentParser(description="GEO 規範更新器")
    parser.add_argument("--input", default=TIPS_INPUT, help="分析結果 JSON 檔案")
    parser.add_argument("--dry-run", action="store_true", help="預覽變更，不寫入")
    parser.add_argument("--no-git", action="store_true", help="更新檔案但不 git commit")
    args = parser.parse_args()

    # 讀取分析結果
    if not os.path.exists(args.input):
        logger.error(f"❌ 找不到 {args.input}，請先執行 trend_analyzer.py")
        return

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    tips = data.get("tips", [])
    if not tips:
        logger.warning("⚠️ 沒有新技巧需要更新")
        return

    logger.info(f"📝 準備更新 {len(tips)} 條新技巧至 geo_framework.md")

    # 執行更新
    success = update_framework(tips, dry_run=args.dry_run)

    if success and not args.dry_run and not args.no_git:
        git_commit_and_push()


if __name__ == "__main__":
    main()
