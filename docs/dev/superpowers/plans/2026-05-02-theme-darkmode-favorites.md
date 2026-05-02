# 蓝+青主题 + 深色模式 + 收藏（星标）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为前端增加蓝+青的统一主题与深色模式开关，并增加文件收藏（星标）功能（可在知识库/搜索中星标与筛选）。

**Architecture:** 前端仍保持单文件 `frontend/index.html`。主题通过 CSS 变量 + Tailwind utility 组合实现：在 `<html>` 上切换 `data-theme="dark"` 并定义 `--bg/--card/--text/--muted/--primary/--accent` 等变量；深色模式开关写入 `localStorage` 并同步 `prefers-color-scheme`。收藏使用后端 per-user 的 `favorites.json` 存储，提供最小 API：list/toggle/check。前端在渲染文件列表与搜索结果时显示星标按钮并支持“只看收藏”过滤。

**Tech Stack:** Tailwind CDN, 原生 JS, FastAPI, 本地文件系统（用户目录）, pytest。

---

## 设计细节

### 主题（蓝+青）
- 视觉目标：减少“灰白单调”，通过渐变背景、卡片描边、按钮层级和少量青色点缀提升质感。
- 使用方式：仅改 CSS/类名，不改变页面结构与业务逻辑。

### 深色模式
- UI：右上角用户栏新增“深色/浅色”切换按钮（图标 + 文案）。
- 逻辑优先级：
  1) 若 localStorage 有用户选择（`ZKKB_THEME=dark|light`）则使用
  2) 否则跟随系统 `prefers-color-scheme`

### 收藏（星标）
- 行为：
  - 知识库文件行与搜索结果卡片提供 ⭐ 切换
  - 知识库页筛选区新增“只看收藏”
  - 搜索页新增“只看收藏”
- 存储：后端保存到 `knowledge_base/u_<id>/_profile/favorites.json`
  - 格式：`{"items":[{"category":"语文","filename":"xxx.pdf","ts":1710000000}]}`
  - `items` 去重，以 `category::filename` 为 key

---

## 文件改动清单

- Modify: [main.py](file:///workspace/zhongkao-kb/main.py)（新增 favorites API）
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)（主题/深色模式/星标 UI 与筛选）
- Create: `tests/test_favorites.py`（后端 API 测试）

---

### Task 1: Favorites API（RED→GREEN）

**Files:**
- Modify: [main.py](file:///workspace/zhongkao-kb/main.py)
- Create: `/workspace/zhongkao-kb/tests/test_favorites.py`

- [ ] **Step 1: 写失败测试：收藏 toggle + list**

```python
import sys
from pathlib import Path
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import main

def _create_user_and_token(client: TestClient, monkeypatch, tmp_path: Path, username: str):
    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": username, "password": "pw"})
    token = client.post("/api/auth/login", json={"username": username, "password": "pw"}).json()["token"]
    return token

def test_favorites_toggle_and_list(tmp_path: Path, monkeypatch):
    client = TestClient(main.app)
    token = _create_user_and_token(client, monkeypatch, tmp_path, "u1")

    kb_root = tmp_path / "kb"
    kb_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    r1 = client.post(
        "/api/favorites/toggle",
        headers={"Authorization": "Bearer " + token},
        json={"category": "语文", "filename": "a.pdf"},
    )
    assert r1.status_code == 200
    assert r1.json()["status"] == "success"
    assert r1.json()["favorited"] is True

    r2 = client.get("/api/favorites", headers={"Authorization": "Bearer " + token})
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert any(it["category"] == "语文" and it["filename"] == "a.pdf" for it in items)

    r3 = client.post(
        "/api/favorites/toggle",
        headers={"Authorization": "Bearer " + token},
        json={"category": "语文", "filename": "a.pdf"},
    )
    assert r3.status_code == 200
    assert r3.json()["favorited"] is False
```

- [ ] **Step 2: 运行测试确认失败（Verify RED）**

Run:
```bash
pytest -q tests/test_favorites.py -q
```
Expected: FAIL（接口不存在）

- [ ] **Step 3: 实现 favorites 存取工具函数**

在 `main.py` 新增（靠近 user_kb_dir/profile 相关函数）：
- `_favorites_path(user_id) -> Path`
- `_read_favorites(user_id) -> dict`
- `_write_favorites(user_id, data) -> None`
- `_toggle_favorite(user_id, category, filename) -> bool`

注意：
- category/filename 使用 `validate_path_segment`
- 限制最大 items（例如 5000）

- [ ] **Step 4: 新增 API**

Endpoints：
- `GET /api/favorites` → `{"items":[...]}`
- `POST /api/favorites/toggle` → `{"status":"success","favorited":true|false}`
- （可选）`GET /api/favorites/check?category=..&filename=..`

- [ ] **Step 5: 跑测试转绿并提交**

```bash
pytest -q tests/test_favorites.py -q
git add main.py tests/test_favorites.py
git commit -m "feat: favorites api"
```

---

### Task 2: 前端收藏 UI（知识库/搜索）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 前端 favorites state**
- `let favorites = new Set()`（key: `${category}::${filename}`）
- 启动时 `GET /api/favorites` 加载

- [ ] **Step 2: 列表/搜索结果渲染星标按钮**
- 知识库文件行：在“预览/拆题/删除”旁新增 ⭐
- 搜索结果卡片右上：新增 ⭐
- 点击：调用 `/api/favorites/toggle`，本地 set 同步更新并刷新当前视图

- [ ] **Step 3: “只看收藏”过滤**
- 知识库页筛选面板新增一个 checkbox：只看收藏
- 搜索页同样新增 checkbox

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: favorites ui"
```

---

### Task 3: 主题与深色模式（蓝+青）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: CSS 变量主题**
- 在 `<style>` 里加入 `:root` 与 `[data-theme="dark"]` 的变量
- `body` 背景使用渐变（浅色轻微、深色更暗）

- [ ] **Step 2: 深色模式开关**
- 右上角用户栏新增按钮（“深色/浅色”）
- JS：读取/写入 localStorage 并设置 `document.documentElement.dataset.theme`

- [ ] **Step 3: 替换关键区域颜色为变量/一致的 Tailwind 方案**
- Tabs 选中态、卡片背景、边框、预览面板、按钮 hover
- 控制修改范围：只改外观，不动结构

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "style: add blue-cyan theme and dark mode"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
pytest -q
```

- [ ] **Step 2: 手工回归清单**
- 星标：知识库/搜索都可点亮与取消
- 筛选：只看收藏生效
- 深色模式：刷新后记住；不登录时不报错

- [ ] **Step 3: Push**

```bash
git push origin main
```

