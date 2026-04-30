# 头像与昵称 v1（多用户）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增加用户个人资料：支持设置昵称与上传头像；前端右上角展示头像与昵称，并提供设置入口。

**Architecture:** 后端扩展 SQLite `users` 表增加 `nickname/avatar_filename`，新增 profile API（设置昵称、上传头像、获取头像）；前端新增“设置”弹窗与头像展示，并在 `me` 接口中读取昵称与头像状态。

**Tech Stack:** FastAPI, sqlite3, 纯前端 JS（fetch）, 本地文件存储到 `knowledge_base/u_<user_id>/_profile/`.

---

## File Structure

**Modify**
- `auth.py`：扩展用户查询返回 nickname/has_avatar
- `main.py`：新增 profile API + DB 迁移（ALTER TABLE）
- `frontend/index.html`：用户栏显示头像与昵称 + 设置弹窗（昵称/头像上传）
- `tests/test_auth.py`：新增昵称/头像接口测试

---

### Task 1: 后端 DB 迁移与 `me` 扩展

**Files:**
- Modify: `auth.py`
- Modify: `main.py`
- Test: `tests/test_auth.py`

- [ ] **Step 1: 写会失败的测试（me 返回 nickname/has_avatar）**

在 `tests/test_auth.py` 追加：

```python
def test_me_contains_profile_fields(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import main

    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "alice", "password": "pw"}).json()["token"]

    r = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    data = r.json()
    assert "nickname" in data
    assert "has_avatar" in data
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pytest -q tests/test_auth.py::test_me_contains_profile_fields -q`

- [ ] **Step 3: DB 迁移**

在 `main.py` 启动时调用迁移函数：
- 若 users 表缺少 `nickname`：执行 `ALTER TABLE users ADD COLUMN nickname TEXT`
- 若 users 表缺少 `avatar_filename`：执行 `ALTER TABLE users ADD COLUMN avatar_filename TEXT`

- [ ] **Step 4: 扩展 `me` 返回**

通过 DB 查询当前用户的 `nickname/avatar_filename`，返回：
- `nickname`（空字符串或 null 均可，前端按空处理）
- `has_avatar`（avatar_filename 非空即 true）

- [ ] **Step 5: 运行测试确认通过**

Run: `pytest -q tests/test_auth.py::test_me_contains_profile_fields -q`

- [ ] **Step 6: Commit**

```bash
git add auth.py main.py tests/test_auth.py
git commit -m "feat: add profile fields to me"
```

---

### Task 2: 后端昵称设置接口

**Files:**
- Modify: `main.py`
- Test: `tests/test_auth.py`

- [ ] **Step 1: 写会失败的测试**

在 `tests/test_auth.py` 追加：

```python
def test_set_nickname(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    import main

    monkeypatch.setenv("APP_DB_PATH", str(tmp_path / "app.db"))
    monkeypatch.setenv("INVITE_CODE", "abc123")
    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw"})
    token = client.post("/api/auth/login", json={"username": "alice", "password": "pw"}).json()["token"]

    r = client.post("/api/profile/nickname", json={"nickname": "小明"}, headers={"Authorization": "Bearer " + token})
    assert r.status_code == 200
    assert r.json()["nickname"] == "小明"
```

- [ ] **Step 2: 实现 `POST /api/profile/nickname`**

校验：
- 去除首尾空格
- 允许空（清空昵称）
- 非空长度 1–20

- [ ] **Step 3: 运行测试**

Run: `pytest -q tests/test_auth.py::test_set_nickname -q`

- [ ] **Step 4: Commit**

```bash
git add main.py tests/test_auth.py
git commit -m "feat: add nickname endpoint"
```

---

### Task 3: 后端头像上传与获取（含默认头像）

**Files:**
- Modify: `main.py`
- Test: `tests/test_auth.py`

- [ ] **Step 1: 默认头像实现**

在 `main.py` 内置一个固定 SVG 或固定 PNG bytes（作为默认头像），`GET /api/profile/avatar` 未上传时直接返回默认图。

- [ ] **Step 2: 实现 `POST /api/profile/avatar`**

规则：
- `multipart/form-data` 字段名 `file`
- 仅允许 `image/png` / `image/jpeg` / `image/webp`
- 最大 2MB
- 写入 `knowledge_base/u_<user_id>/_profile/avatar.<ext>`
- 更新 users.avatar_filename

- [ ] **Step 3: 实现 `GET /api/profile/avatar`**

若 avatar_filename 存在且文件存在：返回文件内容与 content-type；否则返回默认头像。

- [ ] **Step 4: 写测试（上传后能取到且 content-type 正确）**

在 `tests/test_auth.py` 追加（用小 PNG bytes 或 webp bytes）并验证：
- 上传成功返回 200
- GET 返回 200 且响应 body 非空

- [ ] **Step 5: Commit**

```bash
git add main.py tests/test_auth.py
git commit -m "feat: add avatar upload and default avatar"
```

---

### Task 4: 前端展示头像/昵称 + 设置弹窗

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 用户栏显示头像 + 昵称**

用户栏新增 `<img>`：
- src 指向 `/api/profile/avatar`（通过 `apiFetch` 取得 blob 并用 objectURL，或直接 `<img src>` 但需带 Authorization，因此推荐 blob 方式）
- 昵称显示：优先 `nickname`，否则 `username`

- [ ] **Step 2: 新增“设置”弹窗**

内容：
- 昵称输入框 + 保存（调用 `/api/profile/nickname`）
- 头像上传按钮（调用 `/api/profile/avatar`，成功后刷新头像）

- [ ] **Step 3: 登录后初始化资料**

在 `me` 成功后：
- 保存 `nickname/has_avatar`
- 加载头像显示

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add profile UI (nickname and avatar)"
```

---

### Task 5: 推送与部署

- [ ] 推送到 GitHub：`git push origin main`
- [ ] 同步 HF：`git push -f hf main`
- [ ] 验证：注册登录后可设置昵称/头像，刷新仍保持

