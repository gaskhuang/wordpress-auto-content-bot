"""
framework_updater.py — 動態規範更新器 (YAML 版)

用途：讀取 analyzed_tips.json，安全地將新技巧插入 geo_framework.md。
      元資料（版本號、changelog、累計來源數）統一由 framework_meta.yaml 管理，
      不再用 regex 操作 markdown 內的數值。

使用方式：
    python framework_updater.py                     # 正式更新
    python framework_updater.py --dry-run           # 預覽變更，不寫入
    python framework_updater.py --no-git            # 更新檔案但不 git commit
"""

import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime
from dotenv import load_dotenv

try:
    import yaml
except ImportError:
    print("請先安裝 PyYAML: pip install pyyaml")
    sys.exit(1)

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', datefmt='%H:%M:%S'))
    logger.addHandler(handler)

BASE_DIR = os.path.dirname(__file__)
FRAMEWORK_PATH = os.path.join(BASE_DIR, "geo_framework.md")
META_PATH = os.path.join(BASE_DIR, "framework_meta.yaml")
TIPS_INPUT = os.path.join(BASE_DIR, "analyzed_tips.json")

APPEND_MARKER = "<!-- ===== AUTO-APPEND ZONE: DO NOT EDIT BELOW THIS LINE ===== -->"
END_MARKER = "<!-- ===== END AUTO-APPEND ZONE ===== -->"


def load_meta():
    """從 framework_meta.yaml 讀取元資料"""
    if not os.path.exists(META_PATH):
        logger.warning(f"找不到 {META_PATH}，使用預設值")
        return {
            "version": "1.0",
            "last_updated": "2026-01-01",
            "learned_sources_count": 0,
            "changelog": [],
        }
    with open(META_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_meta(meta):
    """將元資料寫回 framework_meta.yaml"""
    with open(META_PATH, "w", encoding="utf-8") as f:
        yaml.dump(meta, f, allow_unicode=True, default_flow_style=False, sort_keys=False)


def bump_version(version):
    """遞增小版本號"""
    parts = str(version).split(".")
    parts[-1] = str(int(parts[-1]) + 1)
    return ".".join(parts)


def get_current_week():
    """取得 ISO 週數格式，如 2026-W07"""
    return datetime.now().strftime("%G-W%V")


def format_tips_as_markdown(tips, week_label):
    """將技巧列表格式化為 Markdown"""
    lines = [f"\n### {week_label} 新增技巧\n"]
    for tip in tips:
        confidence_emoji = {"high": "🟢", "medium": "🟡", "low": "🔴"}.get(
            tip.get("confidence", ""), "⚪"
        )
        lines.append(f"- {confidence_emoji} **{tip.get('tip', '')}**")
        lines.append(f"  - 詳細：{tip.get('detail', '')}")
        lines.append(f"  - 適用區塊：`{tip.get('applicable_section', '通用')}`")
        lines.append(f"  - 預期效果：{tip.get('expected_effect', '待驗證')}")
        lines.append(f"  - 來源：[原文]({tip.get('source_url', '#')})")
        lines.append("")
    return "\n".join(lines)


def sync_meta_to_markdown(meta):
    """將 YAML 元資料同步寫回 geo_framework.md 的 header 行與 changelog 表格"""
    if not os.path.exists(FRAMEWORK_PATH):
        logger.error(f"❌ 找不到 {FRAMEWORK_PATH}")
        return False

    with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # 更新 header 行（第 3 行：> 最後更新：...）
    header_line = (
        f"> 最後更新：{meta['last_updated']} | "
        f"版本：v{meta['version']} | "
        f"累計學習來源：{meta['learned_sources_count']} 篇\n"
    )
    for i, line in enumerate(lines):
        if line.startswith("> 最後更新："):
            lines[i] = header_line
            break

    # 重建 changelog 表格
    changelog_start = None
    changelog_end = None
    for i, line in enumerate(lines):
        if "| 日期 | 版本 | 新增技巧數 | 來源 |" in line:
            changelog_start = i
        if changelog_start is not None and i > changelog_start + 1 and line.strip() == "":
            changelog_end = i
            break
    if changelog_start is None:
        changelog_end = len(lines)

    if changelog_start is not None:
        table_lines = [
            "| 日期 | 版本 | 新增技巧數 | 來源 |\n",
            "|------|------|-----------|------|\n",
        ]
        for entry in meta.get("changelog", []):
            table_lines.append(
                f"| {entry['date']} | v{entry['version']} | {entry['tips_added']} | {entry['source']} |\n"
            )
        table_lines.append("\n")

        if changelog_end is None:
            changelog_end = len(lines)
        lines[changelog_start:changelog_end] = table_lines

    with open(FRAMEWORK_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True


def append_tips_to_markdown(tips_md):
    """將新技巧 markdown 插入 AUTO-APPEND ZONE"""
    if not os.path.exists(FRAMEWORK_PATH):
        logger.error(f"❌ 找不到 {FRAMEWORK_PATH}")
        return False

    with open(FRAMEWORK_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    if APPEND_MARKER not in content:
        logger.error(f"❌ 找不到插入標記: {APPEND_MARKER}")
        return False

    content = content.replace(
        APPEND_MARKER,
        APPEND_MARKER + "\n" + tips_md
    )

    with open(FRAMEWORK_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    return True


def update_framework(tips, dry_run=False):
    """主更新流程：更新 YAML 元資料 + 插入技巧至 markdown"""
    meta = load_meta()
    old_version = str(meta.get("version", "1.0"))
    new_version = bump_version(old_version)
    week_label = get_current_week()
    today = datetime.now().strftime("%Y-%m-%d")

    # 格式化新技巧
    new_tips_md = format_tips_as_markdown(tips, week_label)

    if dry_run:
        logger.info(f"\n[DRY RUN] 預覽變更 (v{old_version} → v{new_version}):\n")
        logger.info(new_tips_md)
        return True

    # 1. 更新 YAML 元資料
    meta["version"] = new_version
    meta["last_updated"] = today
    meta["learned_sources_count"] = meta.get("learned_sources_count", 0) + len(tips)

    new_changelog_entry = {
        "date": today,
        "version": new_version,
        "tips_added": len(tips),
        "source": "X/Reddit 自動採集",
    }
    meta.setdefault("changelog", []).insert(0, new_changelog_entry)
    save_meta(meta)
    logger.info(f"✅ framework_meta.yaml 已更新至 v{new_version}")

    # 2. 插入技巧至 markdown
    if not append_tips_to_markdown(new_tips_md):
        return False

    # 3. 同步元資料至 markdown header + changelog
    if not sync_meta_to_markdown(meta):
        return False

    logger.info(f"✅ geo_framework.md 已更新至 v{new_version}")
    logger.info(f"   新增 {len(tips)} 條技巧，累計學習來源：{meta['learned_sources_count']} 篇")
    return True


def git_commit_and_push():
    """自動 commit 並 push 變更"""
    try:
        week = get_current_week()
        subprocess.run(
            ["git", "add", "geo_framework.md", "framework_meta.yaml",
             "analyzed_tips.json", "raw_trends.json"],
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
    parser = argparse.ArgumentParser(description="GEO 規範更新器 (YAML 版)")
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

    # 驗證 tips 結構
    required_keys = {"tip"}
    for i, tip in enumerate(tips):
        if not isinstance(tip, dict):
            logger.error(f"❌ tips[{i}] 格式錯誤：預期 dict，得到 {type(tip)}")
            return
        missing = required_keys - set(tip.keys())
        if missing:
            logger.error(f"❌ tips[{i}] 缺少必要欄位: {missing}")
            return

    logger.info(f"📝 準備更新 {len(tips)} 條新技巧至 geo_framework.md")

    success = update_framework(tips, dry_run=args.dry_run)

    if success and not args.dry_run and not args.no_git:
        git_commit_and_push()


if __name__ == "__main__":
    main()
