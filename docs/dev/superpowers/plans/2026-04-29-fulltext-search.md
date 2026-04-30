# 全文搜索 v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为“中考知识库”新增全文搜索能力：支持按关键词（包含匹配、大小写不敏感）在文件名与文本内容中检索，并在前端展示结果并可一键预览命中文件。

**Architecture:** 后端新增 `GET /api/search` 在 `knowledge_base/` 中扫描匹配（文件名匹配 + 文本内容匹配），返回命中片段；前端新增搜索 UI，通过 `API_BASE` 调用后端接口并渲染结果列表，点击结果复用现有预览弹窗。

**Tech Stack:** FastAPI（后端）, Cloudflare Pages（静态前端）, Hugging Face Spaces（后端托管）, 纯前端 JS（fetch）.

---

## File Structure

**Modify**
- `main.py`：新增搜索纯函数 + 新增 `GET /api/search` 路由
- `frontend/index.html`：新增搜索输入/筛选/结果列表 UI 与 fetch 调用

**Create**
- `tests/test_search.py`：后端搜索逻辑单测（需要引入测试依赖）

**Modify (deps)**
- `requirements.txt`：加入 `pytest` 与 `httpx`（用于 FastAPI TestClient）或使用 `unittest` + `httpx`

---

### Task 1: 添加后端搜索纯函数（可测试）

**Files:**
- Modify: `main.py`
- Create: `tests/test_search.py`
- Modify: `requirements.txt`

- [ ] **Step 1: 添加测试依赖**

在 `requirements.txt` 追加：

```txt
pytest
httpx
```

- [ ] **Step 2: 写一个会失败的单测（filename/content 都能命中）**

创建 `tests/test_search.py`：

```python
from pathlib import Path

from main import search_knowledge_base


def test_search_matches_filename_and_content(tmp_path: Path):
    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "语文.md").write_text("这是文言文复习资料", encoding="utf-8")
    (kb / "语文" / "古诗.txt").write_text("古诗文言文", encoding="utf-8")
    (kb / "语文" / "古诗.txt.meta.json").write_text("{}", encoding="utf-8")

    res = search_knowledge_base(
        base_dir=kb,
        q="文言文",
        category=None,
        limit=20,
        context=6,
    )

    assert res["query"] == "文言文"
    assert len(res["results"]) == 2
    filenames = {r["filename"] for r in res["results"]}
    assert "语文.md" in filenames
    assert "古诗.txt" in filenames
```

- [ ] **Step 3: 运行测试，确认失败**

Run:

```bash
pytest -q
```

Expected: FAIL（因为 `search_knowledge_base` 尚未实现或未导出）

- [ ] **Step 4: 在后端实现 `search_knowledge_base`（纯函数）**

在 `main.py` 中新增函数（放在 helper functions 区域）：

```python
from typing import Optional


def _iter_target_files(base_dir: Path, category: Optional[str]):
    if category:
        dirs = [base_dir / category]
    else:
        dirs = [p for p in base_dir.iterdir() if p.is_dir()]
    for d in dirs:
        if not d.exists() or not d.is_dir():
            continue
        for f in d.iterdir():
            if not f.is_file():
                continue
            if f.name.endswith(".meta.json"):
                continue
            yield d.name, f


def _find_all(haystack: str, needle: str, max_hits: int):
    hits = []
    start = 0
    while start < len(haystack) and len(hits) < max_hits:
        idx = haystack.find(needle, start)
        if idx < 0:
            break
        hits.append(idx)
        start = idx + max(1, len(needle))
    return hits


def _make_snippet(text: str, pos: int, needle_len: int, context: int) -> str:
    left = max(0, pos - context)
    right = min(len(text), pos + needle_len + context)
    prefix = "…" if left > 0 else ""
    suffix = "…" if right < len(text) else ""
    return prefix + text[left:right].replace("\n", " ") + suffix


def search_knowledge_base(
    base_dir: Path,
    q: str,
    category: Optional[str],
    limit: int,
    context: int,
):
    q_norm = q.strip()
    q_lower = q_norm.lower()

    results = []
    for cat, f in _iter_target_files(base_dir, category):
        filename_lower = f.name.lower()
        matches = []

        if q_lower in filename_lower:
            matches.append({"where": "filename", "snippet": f.name, "pos": filename_lower.find(q_lower)})

        ext = f.suffix.lower()
        if ext in [".md", ".txt", ".csv"]:
            try:
                content = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                content = ""
            content_lower = content.lower()
            if q_lower in content_lower:
                for pos in _find_all(content_lower, q_lower, max_hits=3):
                    matches.append(
                        {
                            "where": "content",
                            "snippet": _make_snippet(content, pos, len(q_norm), context),
                            "pos": pos,
                        }
                    )

        if matches:
            results.append(
                {
                    "category": cat,
                    "filename": f.name,
                    "path": f"knowledge_base/{cat}/{f.name}",
                    "count": len(matches),
                    "matches": matches,
                }
            )

    results.sort(key=lambda r: (-r["count"], r["filename"]))
    return {
        "query": q_norm,
        "category": category,
        "limit": limit,
        "context": context,
        "results": results[:limit],
    }
```

- [ ] **Step 5: 运行测试，确认通过**

Run:

```bash
pytest -q
```

Expected: PASS

- [ ] **Step 6: 提交**

```bash
git add requirements.txt main.py tests/test_search.py
git commit -m "feat: add backend fulltext search core"
```

---

### Task 2: 新增 `GET /api/search` 路由（参数校验 + 返回结构）

**Files:**
- Modify: `main.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: 写一个会失败的 API 单测**

在 `tests/test_search.py` 追加：

```python
from fastapi.testclient import TestClient

import main


def test_api_search_returns_results(tmp_path):
    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "语文.md").write_text("这是文言文复习资料", encoding="utf-8")

    main.KNOWLEDGE_BASE_DIR = kb
    client = TestClient(main.app)

    r = client.get("/api/search", params={"q": "文言文"})
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "文言文"
    assert data["results"][0]["filename"] == "语文.md"
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
pytest -q
```

Expected: FAIL（路由不存在）

- [ ] **Step 3: 实现路由与参数校验**

在 `main.py` 增加路由：

```python
from fastapi import Query


@app.get("/api/search")
async def api_search(
    q: str = Query(..., min_length=1, max_length=60),
    category: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50),
    context: int = Query(60, ge=10, le=200),
):
    return search_knowledge_base(
        base_dir=KNOWLEDGE_BASE_DIR,
        q=q,
        category=category,
        limit=limit,
        context=context,
    )
```

- [ ] **Step 4: 运行测试，确认通过**

Run:

```bash
pytest -q
```

Expected: PASS

- [ ] **Step 5: 提交**

```bash
git add main.py tests/test_search.py
git commit -m "feat: add /api/search endpoint"
```

---

### Task 3: 前端新增搜索 UI + 结果列表 + 预览联动

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 添加搜索区块（输入框 + 学科筛选 + 按钮）**

在页面顶部（后端地址卡片下方或同卡片内）加入：

- 输入框：关键词
- 下拉框：学科（默认“全部”）
- 按钮：搜索

- [ ] **Step 2: 添加搜索结果列表容器**

新增一个 `div#search-results`，用于渲染结果条目：学科 / 文件名 / snippet（支持多片段）。

- [ ] **Step 3: 实现 `search()` 与渲染函数**

新增 JS：

```js
async function runSearch() {
  const base = getApiBase()
  const q = (document.getElementById('searchQuery').value || '').trim()
  if (!q) return
  const category = document.getElementById('searchCategory').value || ''
  const params = new URLSearchParams({ q })
  if (category) params.set('category', category)
  const r = await fetch(base + '/api/search?' + params.toString())
  const data = await r.json()
  renderSearchResults(data)
}
```

渲染结果时为每条结果提供“预览”按钮，点击后调用现有 `previewFile(category, filename)`（或复用当前实现的 preview 逻辑）。

- [ ] **Step 4: 学科筛选下拉的数据来源**

v1：从 `/api/stats` 的 keys 生成（调用 `loadStats()` 后更新下拉）。

- [ ] **Step 5: 手工验证**

Run 后端（本地或已部署）后，在前端输入关键词：
- 预期：搜索结果出现
- 点击“预览”：弹窗打开对应文件内容

- [ ] **Step 6: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add frontend fulltext search UI"
```

---

### Task 4: 联调与部署（GitHub → Cloudflare Pages / Hugging Face）

**Files:**
- No code changes required

- [ ] **Step 1: 推送到 GitHub**

```bash
git push origin main
```

- [ ] **Step 2: 更新 Hugging Face 后端**

在你的电脑执行：

```powershell
cd C:\Users\Administrator\zhongkao-kb
git pull origin main
git push -f hf main
```

- [ ] **Step 3: 等待 Cloudflare Pages 自动部署完成**

打开 Pages 项目部署列表，确认最新 commit 已成功部署；必要时 Redeploy。

- [ ] **Step 4: 验证线上**

- 后端：打开 `https://hmingbo-zhongkao-kb-api.hf.space/docs`，确认出现 `/api/search`
- 前端：打开 `https://zhongkao-kb.pages.dev`，输入关键词，确认能看到结果并预览

---

## Self-Review（计划自检）

- 覆盖 spec：包含匹配/大小写不敏感、文件名匹配 + 文本内容匹配、片段返回、前端结果列表与预览联动、参数限制。
- 无占位：每一步都有明确文件路径/代码/命令。
- 类型一致：`search_knowledge_base` 返回结构与 `/api/search` 一致；前端按 `results[].matches[]` 渲染。

