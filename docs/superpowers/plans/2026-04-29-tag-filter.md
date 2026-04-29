# 标签筛选 v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增“标签筛选”能力：后端提供筛选选项与筛选结果接口，前端新增独立筛选面板卡片，按学科分组展示筛选结果并保留预览/删除。

**Architecture:** 后端扫描 `knowledge_base/`（目录、文件后缀、`.meta.json`）生成筛选选项，并在 `/api/filter` 中基于 query 参数做过滤后返回与 `/api/stats` 相同结构；前端新增筛选面板，调用 `/api/filters/options` 填充下拉，调用 `/api/filter` 渲染目录区域，提供“应用/清除”。

**Tech Stack:** FastAPI（后端）, 纯前端 JS（fetch）, Hugging Face Spaces + Cloudflare Pages.

---

## File Structure

**Modify**
- `main.py`：新增 `/api/filters/options` 与 `/api/filter`
- `frontend/index.html`：新增筛选面板 UI + 调用接口并渲染
- `tests/test_search.py`：新增接口单测（字段与过滤逻辑）

---

### Task 1: 后端新增 `/api/filters/options`

**Files:**
- Modify: `main.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: 写会失败的测试**

在 `tests/test_search.py` 追加：

```python
def test_filters_options(tmp_path):
    import main
    from fastapi.testclient import TestClient

    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "a.md").write_text("x", encoding="utf-8")
    (kb / "语文" / "a.md.meta.json").write_text('{"year":"2023","region":"北京","type":"中考真题"}', encoding="utf-8")
    (kb / "数学").mkdir(parents=True)
    (kb / "数学" / "b.txt").write_text("y", encoding="utf-8")

    main.KNOWLEDGE_BASE_DIR = kb
    client = TestClient(main.app)
    r = client.get("/api/filters/options")
    assert r.status_code == 200
    data = r.json()
    assert "语文" in data["categories"]
    assert "数学" in data["categories"]
    assert "2023" in data["years"]
    assert "北京" in data["regions"]
    assert "中考真题" in data["types"]
    assert "md" in data["exts"]
    assert "txt" in data["exts"]
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```bash
pytest -q
```

Expected: FAIL（路由不存在）

- [ ] **Step 3: 实现路由**

在 `main.py` 增加：

- 扫描 `KNOWLEDGE_BASE_DIR` 下所有学科目录
- 遍历文件（排除 `.meta.json`），收集后缀（无点、lower）
- 扫描 `*.meta.json`，收集 year/region/type
- 返回去重排序后的列表

- [ ] **Step 4: 运行测试确认通过**

Run: `pytest -q`

- [ ] **Step 5: 提交**

```bash
git add main.py tests/test_search.py
git commit -m "feat: add /api/filters/options"
```

---

### Task 2: 后端新增 `/api/filter`（组合筛选 + 按学科分组）

**Files:**
- Modify: `main.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: 写会失败的测试**

在 `tests/test_search.py` 追加：

```python
def test_filter_by_meta_and_ext(tmp_path):
    import main
    from fastapi.testclient import TestClient

    kb = tmp_path / "knowledge_base"
    (kb / "语文").mkdir(parents=True)
    (kb / "语文" / "a.md").write_text("x", encoding="utf-8")
    (kb / "语文" / "a.md.meta.json").write_text('{"year":"2023","region":"北京","type":"中考真题"}', encoding="utf-8")
    (kb / "语文" / "b.md").write_text("y", encoding="utf-8")
    (kb / "数学").mkdir(parents=True)
    (kb / "数学" / "c.txt").write_text("z", encoding="utf-8")

    main.KNOWLEDGE_BASE_DIR = kb
    client = TestClient(main.app)
    r = client.get("/api/filter", params={"year": "2023", "ext": "md"})
    assert r.status_code == 200
    data = r.json()
    assert "语文" in data
    assert [x["name"] for x in data["语文"]] == ["a.md"]
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q`

- [ ] **Step 3: 实现路由与过滤逻辑**

在 `main.py` 增加：

- 参数：`category/year/region/type/ext`（均可选）
- `ext` 标准化（去点、lower）
- 遍历目标目录与文件（排除 `.meta.json`）
- 读取 meta（若筛选条件包含 year/region/type，但无 meta 则不匹配）
- 命中后按学科收集为 `{"name": f.name, "has_meta": bool(meta_path.exists())}`
- 返回与 `/api/stats` 一样的结构（只包含命中学科）

- [ ] **Step 4: 运行测试确认通过**

Run: `pytest -q`

- [ ] **Step 5: 提交**

```bash
git add main.py tests/test_search.py
git commit -m "feat: add /api/filter"
```

---

### Task 3: 前端新增“筛选面板”卡片（应用/清除 + 渲染结果）

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 添加筛选面板 UI**

在“知识库结构”卡片内（搜索区块下方）新增：
- 学科/年份/地区/类型/后缀下拉
- 按钮：应用筛选 / 清除筛选

- [ ] **Step 2: 加载筛选候选项**

新增 `loadFilterOptions()`，请求 `/api/filters/options` 并填充下拉。

- [ ] **Step 3: 应用筛选**

新增 `applyFilters()`：
- 读取下拉值，拼接 query
- `fetch('/api/filter?...')`
- 使用现有渲染逻辑（复用生成 html 的部分）更新 `kb-stats`

- [ ] **Step 4: 清除筛选**

新增 `clearFilters()`：
- 重置下拉
- 调用 `loadStats()` 恢复原目录

- [ ] **Step 5: 手工验证**

打开页面：
- 选择 year/region/type/ext 任意组合
- 点击“应用筛选”
- 预期：列表变为命中结果（仍可预览/删除）
- 点击“清除筛选”
- 预期：恢复全量目录

- [ ] **Step 6: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add filter panel UI"
```

---

### Task 4: 推送与部署验证

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

- 后端：`/docs` 中出现 `/api/filters/options` 与 `/api/filter`
- 前端：筛选面板可用、筛选后仍按学科分组显示、预览/删除正常

---

## Self-Review（计划自检）

- 覆盖 spec：options 接口、filter 接口、category/year/region/type/ext 组合筛选、按学科分组、前端独立筛选面板、应用/清除、无 meta 文件在 year/region/type 条件下不命中。
- 无占位步骤：包含测试用例、命令与路径。

