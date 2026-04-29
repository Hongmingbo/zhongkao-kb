# 每日名言/古诗词 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在首页标题下方展示“每日名言/古诗词”，格式为“内容---作者或出处”，可折叠展开查看“思想哲理概括”，并按北京时间每日轮换。

**Architecture:** 后端提供 `GET /api/daily_quote` 返回当日固定内容（从内置列表按日期取模选取）；前端页面加载时请求该接口并渲染 `<details>` 折叠组件，同时做当日 localStorage 缓存与失败兜底。

**Tech Stack:** FastAPI（后端）, 纯前端 JS（fetch）.

---

## File Structure

**Modify**
- `main.py`：新增 `/api/daily_quote`
- `frontend/index.html`：替换标题下方文案为“每日一句”组件并拉取接口
- `tests/test_search.py`：新增接口字段测试

---

### Task 1: 后端新增 `/api/daily_quote`

**Files:**
- Modify: `main.py`
- Test: `tests/test_search.py`

- [ ] **Step 1: 写一个会失败的测试**

在 `tests/test_search.py` 追加：

```python
def test_api_daily_quote_has_required_fields():
    from fastapi.testclient import TestClient
    import main

    client = TestClient(main.app)
    r = client.get("/api/daily_quote")
    assert r.status_code == 200
    data = r.json()
    assert set(["date", "text", "source", "summary"]).issubset(set(data.keys()))
    assert isinstance(data["text"], str) and data["text"]
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q`

- [ ] **Step 3: 实现接口**

在 `main.py` 中新增：

- 北京时间 `ZoneInfo("Asia/Shanghai")` 计算今日日期
- 内置 quotes 列表（`text/source/summary`）
- 以日期稳定取值并返回

- [ ] **Step 4: 运行测试确认通过**

Run: `pytest -q`

- [ ] **Step 5: 提交**

```bash
git add main.py tests/test_search.py
git commit -m "feat: add /api/daily_quote"
```

---

### Task 2: 前端替换标题下方文案（可折叠 + 每日刷新）

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 将标题下方固定文案替换为占位容器**

新增：

```html
<div id="daily-quote" class="mt-2 text-gray-500 text-sm"></div>
```

- [ ] **Step 2: 前端加载时请求 `/api/daily_quote` 并渲染**

实现：
- localStorage 缓存 key：`ZKKB_DAILY_QUOTE`
- 若缓存 date==今日则直接使用
- 否则 fetch 后端接口并缓存
- 渲染为：

```html
<details class="inline-block">
  <summary class="cursor-pointer">内容---出处</summary>
  <div class="mt-1">思想哲理概括</div>
</details>
```

- [ ] **Step 3: 失败兜底**

若请求失败，展示内置兜底语句（仍符合格式）。

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: show daily quote on homepage"
```

---

### Task 3: 推送与部署验证

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

- 后端：`https://hmingbo-zhongkao-kb-api.hf.space/api/daily_quote`
- 前端：`https://zhongkao-kb.pages.dev`（Ctrl+F5）查看标题下方是否每日一句可折叠

