# 题目拆分 v1（文本 → JSON）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 从知识库内 `.md/.txt/.csv` 文件拆题并生成 `*.questions.json`，前端提供“拆题”按钮并预览拆题结果。

**Architecture:** 后端新增拆题纯函数（可单测）+ `POST /api/split` 写入 JSON 文件 + `GET /api/questions/...` 读取返回；前端文件列表新增“拆题”按钮，调用接口并在弹窗展示题目列表及下载链接。

**Tech Stack:** FastAPI（后端）, 纯前端 JS（fetch）, JSON 落盘到 `knowledge_base/`.

---

## File Structure

**Modify**
- `main.py`：新增拆题函数与两个 API 路由
- `frontend/index.html`：新增“拆题”按钮与预览渲染
- `tests/test_search.py`：新增拆题 API 的单测

---

### Task 1: 后端拆题纯函数（TDD）

**Files:**
- Modify: `main.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: 写会失败的单测（题号 + 选项识别）**

在 `tests/test_search.py` 追加：

```python
def test_split_questions_basic():
    from main import split_questions_from_text

    text = \"\"\"一、选择题
1. 下列说法正确的是（ ）
A. 选项A
B. 选项B
C. 选项C
D. 选项D

2、这是一道没有选项的题
\"\"\"

    items = split_questions_from_text(text)
    assert len(items) == 2
    assert items[0]["id"] == "1"
    assert "下列说法正确的是" in items[0]["stem"]
    assert items[0]["options"][0].startswith("A")
    assert items[1]["id"] == "2"
    assert items[1]["options"] == []
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q`

- [ ] **Step 3: 在 `main.py` 实现 `split_questions_from_text(text)`**

要求：

- 识别题号：`1.` / `1、` / `1)` / `（1）`
- 题块划分：遇到下一个题号开始新题
- 选项识别：A/B/C/D 行，抽取为 `options`
- 输出 item：`{"id": "...", "stem": "...", "options": [...], "answer":"", "analysis":"", "tags":[]}`

- [ ] **Step 4: 运行测试确认通过**

Run: `pytest -q`

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_search.py
git commit -m "feat: add question splitting core"
```

---

### Task 2: 后端 API（/api/split + /api/questions）

**Files:**
- Modify: `main.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: 写会失败的 API 单测**

在 `tests/test_search.py` 追加：

```python
def test_api_split_creates_questions_file(tmp_path):
    import main
    from fastapi.testclient import TestClient

    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "试卷.md").write_text(\"\"\"1. 题目
A. a
B. b
C. c
D. d
\"\"\", encoding="utf-8")

    main.KNOWLEDGE_BASE_DIR = kb
    client = TestClient(main.app)
    r = client.post("/api/split", json={"category": "语文", "filename": "试卷.md"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["count"] == 1

    out = kb / "语文" / "试卷.questions.json"
    assert out.exists()
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q`

- [ ] **Step 3: 实现 `POST /api/split`**

行为：

- 校验文件存在于 `knowledge_base/{category}/{filename}`
- 限制后缀：仅 `.md/.txt/.csv`
- 调用 `split_questions_from_text` 得到 items
- 写入 `*.questions.json`（同目录，basename 加 `.questions.json`）
- 返回 `count` 与 output 路径

- [ ] **Step 4: 实现 `GET /api/questions/{category}/{filename}`**

行为：
- 读取 JSON 并返回
- 找不到则 404

- [ ] **Step 5: 运行测试确认通过**

Run: `pytest -q`

- [ ] **Step 6: Commit**

```bash
git add main.py tests/test_search.py
git commit -m "feat: add split questions endpoints"
```

---

### Task 3: 前端新增“拆题”按钮与预览

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 在文件 hover 操作区增加“拆题”按钮**

在当前每个文件行的按钮组中新增：

```html
<button class="text-indigo-500 hover:text-indigo-700 text-xs" data-action="split" ...>拆题</button>
```

- [ ] **Step 2: 处理 split 点击**

在 `kbStats` click handler 中新增 action：

- 调用 `POST /api/split`
- 成功后调用 `GET /api/questions/{category}/{basename}.questions.json`
- 在弹窗中渲染前 10 题（题号、题干、选项列表）
- 提供下载链接：`/api/file/{category}/{questions_filename}`（复用已有 file 获取接口；若它不支持 json，新增一个 download endpoint）

- [ ] **Step 3: 手工验证**

- 上传一个包含题号/选项的 `.md`
- 点击“拆题”
- 预期：弹窗展示拆题结果，并可下载 json

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add split button and preview"
```

---

### Task 4: 推送与部署

- [ ] **Step 1: 推送到 GitHub**

```bash
git push origin main
```

- [ ] **Step 2: Hugging Face 同步**

在你的电脑执行：

```powershell
cd C:\Users\Administrator\zhongkao-kb
git pull origin main
git push -f hf main
```

- [ ] **Step 3: 验证**

- 后端：`/docs` 出现 `/api/split` 与 `/api/questions/...`
- 前端：文件列表出现“拆题”，点击可生成并预览 JSON

