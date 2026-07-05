#!/usr/bin/env python3
"""快速记录一条灵感到 ideas.csv。

用法示例：
    python scripts/add.py --title "标题" --content "详细内容"
    python scripts/add.py -t "标题" -c "内容" --tags "产品;工具" --category 产品 \
        --status inbox --source "洗澡时" --next "做个原型"

脚本会自动生成 id（日期+当天序号）和时间戳，并用标准 csv 模块安全写入，
无需手动处理逗号、换行、引号等转义问题。
"""
import argparse
import csv
import os
from datetime import datetime

FIELDS = [
    "id",
    "created_at",
    "title",
    "content",
    "tags",
    "category",
    "status",
    "source",
    "next_action",
]

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ideas.csv")


def ensure_csv(path):
    """确保 CSV 存在且带表头。"""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(FIELDS)


def read_rows(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def next_id(rows, today):
    """基于当天已有记录数生成形如 20260705-0003 的自增 id。"""
    prefix = today.strftime("%Y%m%d")
    count = sum(1 for r in rows if r.get("id", "").startswith(prefix))
    return f"{prefix}-{count + 1:04d}"


def main():
    parser = argparse.ArgumentParser(description="记录一条灵感到 ideas.csv")
    parser.add_argument("-t", "--title", required=True, help="一句话标题")
    parser.add_argument("-c", "--content", default="", help="详细描述")
    parser.add_argument("--tags", default="", help="标签，用分号分隔，例如 产品;工具")
    parser.add_argument("--category", default="", help="大分类，例如 产品/技术/写作/生活")
    parser.add_argument(
        "--status",
        default="inbox",
        choices=["inbox", "processing", "done", "archived"],
        help="状态，默认 inbox",
    )
    parser.add_argument("--source", default="", help="灵感来源")
    parser.add_argument("--next", dest="next_action", default="", help="下一步行动")
    args = parser.parse_args()

    ensure_csv(CSV_PATH)
    rows = read_rows(CSV_PATH)

    now = datetime.now()
    record = {
        "id": next_id(rows, now),
        "created_at": now.strftime("%Y-%m-%d %H:%M"),
        "title": args.title,
        "content": args.content,
        "tags": args.tags,
        "category": args.category,
        "status": args.status,
        "source": args.source,
        "next_action": args.next_action,
    }

    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writerow(record)

    print(f"已记录: [{record['id']}] {record['title']}")


if __name__ == "__main__":
    main()
