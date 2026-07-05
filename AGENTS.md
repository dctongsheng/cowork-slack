# AGENTS.md

## Cursor Cloud specific instructions

This repo is a minimal CLI product: a CSV-backed idea database (`ideas.csv`) with two
Python scripts in `scripts/` (`add.py` to append, `search.py` to list/filter/stats).

- **No dependencies to install.** Scripts use only the Python 3 standard library
  (`csv`, `argparse`, `datetime`, `collections`). There is no `requirements.txt`,
  `pyproject.toml`, package manager, database, or long-running service.
- **Use `python3`, not `python`.** The README examples say `python`, but this
  environment only provides `python3` (no `python` alias). Run e.g.
  `python3 scripts/add.py -t "标题" -c "内容"`.
- **Run/test commands** (all defined in `README.md`):
  - Add: `python3 scripts/add.py -t "标题" -c "内容" [--tags a;b] [--category X] [--status inbox]`
  - Search: `python3 scripts/search.py [-k 关键词] [--tag X] [--category X] [--status X] [--stats]`
- **There is no build, lint config, or automated test suite** in the repo. "Testing"
  = running the two scripts against `ideas.csv`.
- `ideas.csv` is the tracked data store. Do not hand-edit it; use `add.py` so CSV
  escaping stays correct. If you add rows only for testing, revert with
  `git checkout -- ideas.csv` to keep the working tree clean.
