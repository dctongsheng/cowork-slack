# 灵感数据库 (CSV)

用一个 Git 仓库把随时冒出来的想法/灵感集中记录下来。数据以 CSV 存储，配套两个 Python 脚本：一个用于**快速记录**，一个用于**检索与统计**。

> ⚠️ **隐私提醒**：如果灵感包含私人内容，建议把本仓库设为 **私有**（GitHub → Settings → General → Danger Zone → Change repository visibility）。

## 目录结构

```text
.
├── README.md
├── ideas.csv            # 主数据库：所有灵感集中一张表
└── scripts/
    ├── add.py           # 快速记一条（自动生成 id/时间戳，安全转义）
    └── search.py        # 按关键词/标签/分类/状态检索与统计
```

## 字段说明

| 字段 | 含义 | 示例 |
| --- | --- | --- |
| `id` | 唯一编号（日期 + 当天序号） | `20260705-0001` |
| `created_at` | 记录时间 | `2026-07-05 14:30` |
| `title` | 一句话标题 | `用Git仓库当灵感库` |
| `content` | 详细描述 | `想法来得快去得也快...` |
| `tags` | 标签，用 `;` 分隔（避免和逗号冲突） | `产品;工具` |
| `category` | 大分类 | `产品` / `技术` / `写作` / `生活` |
| `status` | 状态 | `inbox` / `processing` / `done` / `archived` |
| `source` | 灵感来源 | `洗澡时` / `某篇文章` |
| `next_action` | 下一步行动 | `做个原型` |

## 如何记一条灵感

推荐用脚本写入（会自动处理逗号、引号、换行的转义，**不要手动编辑 CSV 记录**以免破坏格式）：

```bash
python scripts/add.py -t "标题" -c "详细内容"

# 完整参数
python scripts/add.py \
  -t "用Git仓库当灵感库" \
  -c "想法来得快，用 CSV 记录再配脚本检索" \
  --tags "产品;工具" \
  --category 产品 \
  --status inbox \
  --source "洗澡时" \
  --next "做个原型"
```

| 参数 | 说明 |
| --- | --- |
| `-t, --title` | 标题（必填） |
| `-c, --content` | 详细描述 |
| `--tags` | 标签，用 `;` 分隔 |
| `--category` | 分类 |
| `--status` | 状态，默认 `inbox`（可选 inbox/processing/done/archived） |
| `--source` | 来源 |
| `--next` | 下一步行动 |

## 如何检索

```bash
python scripts/search.py                 # 列出全部
python scripts/search.py -k 灵感库        # 按标题/内容关键词
python scripts/search.py --tag 产品       # 按标签
python scripts/search.py --category 技术  # 按分类
python scripts/search.py --status inbox   # 看还没整理的
python scripts/search.py --stats          # 按状态/分类/标签统计
```

## 工作流建议

1. **随手记**：想到什么先用 `add.py` 无脑扔进去，状态默认 `inbox`。
2. **定期整理**：用 `search.py --status inbox` 找出待整理项，补充 `category`/`tags`/`next_action`，处理后改状态。
3. **提交**：`git add -A && git commit -m "add idea" && git push`。

> 💡 本仓库还接入了 Slack Cloud Agent：你也可以直接在频道里发一句"记一条想法：xxx"，让 agent 帮你规范化后写入 `ideas.csv` 并自动提交。

## 环境要求

- Python 3（标准库即可，无需额外依赖）
