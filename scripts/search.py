#!/usr/bin/env python3
"""检索 ideas.csv 里的灵感。

用法示例：
    python scripts/search.py                     # 列出全部
    python scripts/search.py --keyword 灵感库      # 标题/内容关键词
    python scripts/search.py --tag 产品            # 按标签过滤
    python scripts/search.py --category 技术       # 按分类过滤
    python scripts/search.py --status inbox        # 按状态过滤
    python scripts/search.py --stats               # 只看统计信息
"""
import argparse
import csv
import os
from collections import Counter

CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ideas.csv")


def read_rows(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def split_tags(value):
    return [t.strip() for t in value.split(";") if t.strip()]


def match(row, args):
    if args.keyword:
        kw = args.keyword.lower()
        if kw not in row.get("title", "").lower() and kw not in row.get("content", "").lower():
            return False
    if args.tag and args.tag not in split_tags(row.get("tags", "")):
        return False
    if args.category and args.category != row.get("category", ""):
        return False
    if args.status and args.status != row.get("status", ""):
        return False
    return True


def print_rows(rows):
    if not rows:
        print("没有匹配的记录。")
        return
    for r in rows:
        tags = " ".join(f"#{t}" for t in split_tags(r.get("tags", "")))
        header = f"[{r.get('id', '')}] {r.get('created_at', '')} · {r.get('category', '')} {tags}".rstrip()
        print(header)
        print(f"  {r.get('title', '')}")
        if r.get("content"):
            print(f"    {r.get('content')}")
        meta = []
        if r.get("status"):
            meta.append(f"状态:{r['status']}")
        if r.get("source"):
            meta.append(f"来源:{r['source']}")
        if r.get("next_action"):
            meta.append(f"下一步:{r['next_action']}")
        if meta:
            print(f"    ({' | '.join(meta)})")
        print()


def print_stats(rows):
    print(f"总条数: {len(rows)}")
    by_status = Counter(r.get("status", "") for r in rows)
    by_category = Counter(r.get("category", "") for r in rows)
    by_tag = Counter(t for r in rows for t in split_tags(r.get("tags", "")))
    print("\n按状态:")
    for k, v in by_status.most_common():
        print(f"  {k or '(空)'}: {v}")
    print("\n按分类:")
    for k, v in by_category.most_common():
        print(f"  {k or '(空)'}: {v}")
    print("\n按标签:")
    for k, v in by_tag.most_common():
        print(f"  #{k}: {v}")


def main():
    parser = argparse.ArgumentParser(description="检索 ideas.csv 里的灵感")
    parser.add_argument("-k", "--keyword", default="", help="标题/内容关键词")
    parser.add_argument("--tag", default="", help="按标签过滤")
    parser.add_argument("--category", default="", help="按分类过滤")
    parser.add_argument("--status", default="", help="按状态过滤")
    parser.add_argument("--stats", action="store_true", help="显示统计信息")
    args = parser.parse_args()

    rows = read_rows(CSV_PATH)

    if args.stats:
        print_stats(rows)
        return

    result = [r for r in rows if match(r, args)]
    print_rows(result)
    print(f"共 {len(result)} 条（总 {len(rows)} 条）")


if __name__ == "__main__":
    main()
