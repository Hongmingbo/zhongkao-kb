# 多用户账号登录（邀请码注册）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为中考知识库增加“多用户账号登录”，支持邀请码注册、登录会话 token，并将所有知识库相关操作按用户隔离到独立目录。

**Architecture:** 后端使用 SQLite 存储用户与 session token，通过 `Authorization: Bearer <token>` 鉴权并注入 `current_user`，把所有知识库目录从 `knowledge_base/<学科>` 迁移为 `knowledge_base/u_<user_id>/<学科>`；前端增加登录/注册弹窗和顶部用户栏，所有请求自动携带 token。

**Tech Stack:** FastAPI（后端）, sqlite3（标准库）, hashlib.pbkdf2_hmac（标准库）, 纯前端 JS（fetch + localStorage）.

---

## File Structure

**Create**
- `auth.py`：SQLite 初始化、密码哈希、session 创建/校验、FastAPI 依赖 `get_current_user`

**Modify**
- `main.py`：引入 `auth.py`、新增 auth 路由、把知识库根目录计算改为“按用户”，为现有业务接口增加鉴权
- `frontend/index.html`：新增登录/注册 UI，所有 fetch 自动带 Authorization，增加退出
- `tests/test_auth.py`：认证/授权与隔离逻辑单测

---

### Task 1: 建立认证基础设施（SQLite + PBKDF2 + session token）

**Files:**
- Create: `auth.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: 写会失败的单测（注册/登录/鉴权）**

创建 `tests/test_auth.py`：

```python
import os
from pathlib import Path

from fastapi.testclient import TestClient

import main


def test_register_login_me(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")

    client = TestClient(main.app)

    r = client.post("/api/auth/register", json={"invite_code": "abc123", "username": "alice", "password": "pw"})
    assert r.status_code == 200
    assert r.json()["status"] == "success"

    r2 = client.post("/api/auth/login", json={"username": "alice", "password": "pw"})
    assert r2.status_code == 200
    token = r2.json()["token"]
    assert token

    r3 = client.get("/api/auth/me", headers={"Authorization": "Bearer " + token})
    assert r3.status_code == 200
    data = r3.json()
    assert data["username"] == "alice"
```

- [ ] **Step 2: 运行测试确认失败**

Run:

```bash
pytest -q tests/test_auth.py -q
```

Expected: FAIL（路由/模块不存在）

- [ ] **Step 3: 创建 `auth.py`（DB 初始化 + 密码哈希 + session）**

创建 `auth.py`：

```python
import os
import secrets
import sqlite3
import time
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fastapi import HTTPException, Header


@dataclass(frozen=True)
class User:
    id: int
    username: str


def db_path() -> Path:
    p = os.getenv("APP_DB_PATH", "").strip()
    return Path(p) if p else Path(__file__).parent / "app.db"


def get_conn():
    conn = sqlite3.connect(str(db_path()))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    try:
        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              username TEXT NOT NULL UNIQUE,
              password_salt TEXT NOT NULL,
              password_hash TEXT NOT NULL,
              created_at INTEGER NOT NULL
            )
            \"\"\"
        )
        conn.execute(
            \"\"\"
            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL,
              created_at INTEGER NOT NULL,
              expires_at INTEGER NOT NULL,
              FOREIGN KEY(user_id) REFERENCES users(id)
            )
            \"\"\"
        )
        conn.commit()
    finally:
        conn.close()


def _pbkdf2(password: str, salt: str, rounds: int = 200_000) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), rounds)
    return dk.hex()


def create_user(username: str, password: str) -> User:
    init_db()
    salt = secrets.token_hex(16)
    pw_hash = _pbkdf2(password, salt)
    now = int(time.time())
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO users(username,password_salt,password_hash,created_at) VALUES (?,?,?,?)",
            (username, salt, pw_hash, now),
        )
        conn.commit()
        return User(id=int(cur.lastrowid), username=username)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="用户名已存在")
    finally:
        conn.close()


def verify_user(username: str, password: str) -> Optional[User]:
    init_db()
    conn = get_conn()
    try:
        row = conn.execute("SELECT id, username, password_salt, password_hash FROM users WHERE username=?", (username,)).fetchone()
        if not row:
            return None
        expected = row["password_hash"]
        got = _pbkdf2(password, row["password_salt"])
        if secrets.compare_digest(expected, got):
            return User(id=int(row["id"]), username=row["username"])
        return None
    finally:
        conn.close()


def create_session(user_id: int, ttl_seconds: int = 7 * 24 * 3600) -> str:
    init_db()
    token = secrets.token_urlsafe(32)
    now = int(time.time())
    exp = now + ttl_seconds
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO sessions(token,user_id,created_at,expires_at) VALUES (?,?,?,?)",
            (token, user_id, now, exp),
        )
        conn.commit()
        return token
    finally:
        conn.close()


def delete_session(token: str):
    init_db()
    conn = get_conn()
    try:
        conn.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
    finally:
        conn.close()


def get_user_by_token(token: str) -> Optional[User]:
    init_db()
    now = int(time.time())
    conn = get_conn()
    try:
        row = conn.execute(
            \"\"\"
            SELECT u.id as id, u.username as username, s.expires_at as expires_at
            FROM sessions s JOIN users u ON s.user_id = u.id
            WHERE s.token=?
            \"\"\",
            (token,),
        ).fetchone()
        if not row:
            return None
        if int(row["expires_at"]) < now:
            conn.execute("DELETE FROM sessions WHERE token=?", (token,))
            conn.commit()
            return None
        return User(id=int(row["id"]), username=row["username"])
    finally:
        conn.close()


def parse_bearer(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    parts = authorization.split(" ", 1)
    if len(parts) != 2:
        return None
    if parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def get_current_user(authorization: Optional[str] = Header(None)) -> User:
    token = parse_bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="未登录")
    user = get_user_by_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="登录已过期")
    return user
```

- [ ] **Step 4: 运行测试确认仍失败（因为路由未接入）**

Run: `pytest -q tests/test_auth.py -q`

- [ ] **Step 5: Commit**

```bash
git add auth.py tests/test_auth.py
git commit -m "feat: add auth foundation (sqlite + sessions)"
```

---

### Task 2: 在后端接入注册/登录/退出/me 路由

**Files:**
- Modify: `main.py`
- Modify: `tests/test_auth.py`

- [ ] **Step 1: 在 `main.py` 引入并初始化 DB**

在 `main.py` 顶部引入：

```python
import auth
```

并在模块加载后调用：

```python
auth.init_db()
```

- [ ] **Step 2: 添加 auth 路由**

在 `main.py` 添加：

```python
@app.post("/api/auth/register")
async def register(payload: dict = Body(...)):
    invite = (payload.get("invite_code") or "").strip()
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    code = (os.getenv("INVITE_CODE") or "").strip()
    if not code:
        raise HTTPException(status_code=503, detail="未配置 INVITE_CODE")
    if not invite or invite != code:
        raise HTTPException(status_code=403, detail="邀请码错误")
    if not username or not password:
        raise HTTPException(status_code=400, detail="缺少用户名或密码")
    user = auth.create_user(username=username, password=password)
    return {"status": "success", "user": {"id": user.id, "username": user.username}}


@app.post("/api/auth/login")
async def login(payload: dict = Body(...)):
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    user = auth.verify_user(username=username, password=password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    token = auth.create_session(user_id=user.id)
    return {"status": "success", "token": token, "user": {"id": user.id, "username": user.username}}


@app.post("/api/auth/logout")
async def logout(current_user: auth.User = Depends(auth.get_current_user), authorization: str | None = Header(None)):
    token = auth.parse_bearer(authorization)
    if token:
        auth.delete_session(token)
    return {"status": "success"}


@app.get("/api/auth/me")
async def me(current_user: auth.User = Depends(auth.get_current_user)):
    return {"id": current_user.id, "username": current_user.username}
```

并补齐 import：

```python
from fastapi import Depends, Header
```

- [ ] **Step 3: 运行 `tests/test_auth.py`**

Run:

```bash
pytest -q tests/test_auth.py -q
```

Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: add auth routes"
```

---

### Task 3: 用户隔离目录与接口鉴权（后端）

**Files:**
- Modify: `main.py`
- Modify: `tests/test_auth.py`

- [ ] **Step 1: 写隔离测试（两用户互不可见）**

在 `tests/test_auth.py` 追加：

```python
def test_kb_isolated_by_user(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "app.db"
    monkeypatch.setenv("APP_DB_PATH", str(db_path))
    monkeypatch.setenv("INVITE_CODE", "abc123")

    client = TestClient(main.app)
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u1", "password": "pw"})
    client.post("/api/auth/register", json={"invite_code": "abc123", "username": "u2", "password": "pw"})
    t1 = client.post("/api/auth/login", json={"username": "u1", "password": "pw"}).json()["token"]
    t2 = client.post("/api/auth/login", json={"username": "u2", "password": "pw"}).json()["token"]

    kb_root = tmp_path / "knowledge_base"
    monkeypatch.setattr(main, "KNOWLEDGE_BASE_DIR", kb_root)

    (kb_root / "u_1" / "语文").mkdir(parents=True)
    (kb_root / "u_1" / "语文" / "a.md").write_text("x", encoding="utf-8")

    r1 = client.get("/api/stats", headers={"Authorization": "Bearer " + t1})
    r2 = client.get("/api/stats", headers={"Authorization": "Bearer " + t2})
    assert r1.status_code == 200 and "语文" in r1.json()
    assert r2.status_code == 200 and r2.json() == {}
```

- [ ] **Step 2: 修改后端统一获取用户根目录**

在 `main.py` 新增：

```python
def user_kb_dir(user_id: int) -> Path:
    d = KNOWLEDGE_BASE_DIR / f"u_{user_id}"
    d.mkdir(parents=True, exist_ok=True)
    return d
```

并将原先直接使用 `KNOWLEDGE_BASE_DIR` 的逻辑改为使用 `user_kb_dir(current_user.id)`：

- `upload`：保存到用户目录
- `stats/search/filters/filter/file/clear/split/questions/delete`：全部以用户目录为根

实现方式：给这些路由加 `current_user: auth.User = Depends(auth.get_current_user)` 参数，并把路径根替换。

- [ ] **Step 3: 运行隔离测试**

Run:

```bash
pytest -q tests/test_auth.py::test_kb_isolated_by_user -q
```

- [ ] **Step 4: Commit**

```bash
git add main.py tests/test_auth.py
git commit -m "feat: isolate knowledge base by user"
```

---

### Task 4: 前端登录/注册弹窗 + 全局 fetch 携带 token

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 添加登录/注册弹窗 UI**

新增一个 modal：
- tab：登录/注册
- 注册字段：邀请码/用户名/密码
- 登录字段：用户名/密码
- 顶部右侧：显示用户名 + 退出

- [ ] **Step 2: 增加 token 管理与统一请求封装**

在 script 中加入：

```js
const TOKEN_KEY = 'ZKKB_TOKEN'

function getToken() { return localStorage.getItem(TOKEN_KEY) || '' }
function setToken(t) { localStorage.setItem(TOKEN_KEY, t) }
function clearToken() { localStorage.removeItem(TOKEN_KEY) }

async function apiFetch(path, opts) {
  const base = getApiBase()
  const headers = Object.assign({}, (opts && opts.headers) || {})
  const token = getToken()
  if (token) headers['Authorization'] = 'Bearer ' + token
  const res = await fetch(base + path, Object.assign({}, opts || {}, { headers }))
  if (res.status === 401) {
    clearToken()
    showAuthModal()
  }
  return res
}
```

然后把现有 `fetch(base + ...)` 替换为 `apiFetch('/api/...')` 或 `apiFetch('/upload', ...)`。

- [ ] **Step 3: 登录流程**

- `login()` 调用 `/api/auth/login` 成功后保存 token，关闭弹窗，刷新目录
- `register()` 调用 `/api/auth/register` 成功后切换到登录或直接登录（v1 可直接登录）
- `me()` 在页面加载时调用 `/api/auth/me` 校验 token

- [ ] **Step 4: 手工验证步骤**

- 无 token：页面弹出登录/注册
- 注册（邀请码正确）→ 登录 → 可上传/目录可见
- 退出后：操作接口返回 401 并重新弹出登录

- [ ] **Step 5: Commit**

```bash
git add frontend/index.html
git commit -m "feat: add frontend auth modal and token fetch"
```

---

### Task 5: 推送与部署（GitHub + Hugging Face 环境变量）

- [ ] **Step 1: 推送到 GitHub**

```bash
git push origin main
```

- [ ] **Step 2: Hugging Face 设置环境变量**

在 Space Settings → Variables：
- `INVITE_CODE`: 你设定的邀请码（例如 `abc123`）

- [ ] **Step 3: 同步到 Hugging Face**

在你的电脑执行：

```powershell
cd C:\Users\Administrator\zhongkao-kb
git pull origin main
git push -f hf main
```

- [ ] **Step 4: 线上验证**

- 注册：填写邀请码、用户名、密码能成功
- 登录后：上传一个文件，只在该用户可见
- 换另一个用户登录：目录应为空或只显示其自身上传

---

## Self-Review（计划自检）

- 覆盖 spec：邀请码注册、登录会话、鉴权范围、用户目录隔离、前端登录注册 UI、token 注入。
- 安全：PBKDF2 + 盐、session 过期、401 处理。

