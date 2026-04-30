# 认证与会话改造：Supabase Postgres（DATABASE_URL）Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将认证与会话存储从本地 SQLite 切换到 Supabase Postgres，解决 HF 多实例导致的用户数据不一致。

**Architecture:** `auth.py` 根据 `DATABASE_URL` 选择 Postgres/SQLite 后端；Postgres 使用 `psycopg2-binary` 原生 SQL 创建表与读写；启动时执行 `init_db()`，日志仅输出“使用哪个后端”，不输出连接串明文。

**Tech Stack:** FastAPI, psycopg2-binary, sqlite3（fallback）, Supabase Postgres Transaction Pooler.

---

## Files

- Modify: `requirements.txt`
- Modify: `auth.py`
- Modify: `main.py`
- Test: `tests/test_auth.py`（无需改动，确保 sqlite fallback 仍通过）

---

### Task 1: 增加 psycopg2 依赖

**Files:**
- Modify: `requirements.txt`

- [ ] 添加 `psycopg2-binary`
- [ ] Run: `python -m pip install -q -r requirements.txt`
- [ ] Commit: `chore: add psycopg2-binary`

---

### Task 2: auth.py 增加 Postgres 后端并保持 SQLite 作为默认

**Files:**
- Modify: `auth.py`
- Test: `tests/test_auth.py`

- [ ] 新增 `db_backend()`：返回 `postgres` 或 `sqlite`
- [ ] Postgres 连接：
  - 读取 `DATABASE_URL`
  - 未包含 `sslmode=` 时强制 `sslmode=require`
  - 使用 `psycopg2.pool.SimpleConnectionPool` 做进程内连接池
- [ ] `init_db()`：
  - Postgres：`CREATE TABLE IF NOT EXISTS ...`
  - SQLite：保持现状
- [ ] 将 users/sessions 的 CRUD 按后端分支实现（注册、登录、会话、profile、改密码、管理员统计）
- [ ] Run: `pytest -q`
- [ ] Commit: `feat: add postgres auth backend`

---

### Task 3: 启动日志显示当前后端（不泄露连接串）

**Files:**
- Modify: `main.py`

- [ ] 启动日志输出：`DB_BACKEND=postgres|sqlite`
- [ ] 当 postgres 时，不再输出 `APP_DB_PATH`（避免误导），仅输出 `DATABASE_URL=set`
- [ ] Run: `pytest -q`
- [ ] Commit: `chore: log auth db backend`

---

### Task 4: 推送与部署

- [ ] `git push origin main`
- [ ] 你本机同步到 HF：`git push -f hf main`
- [ ] HF Space Secret 已配置：`DATABASE_URL`
- [ ] 验证：
  - 反复请求 `/api/admin/users_count`，不同 `x-proxied-replica` 返回一致
  - 注册后重启/多次请求用户数不再回到 0

