# 认证与会话改造：Supabase Postgres（DATABASE_URL）

## 背景

当前认证/会话存储使用本地 SQLite（`app.db`），在 Hugging Face Spaces 的多实例/多副本场景中会出现：

- 不同 `x-proxied-replica` 读到不同的数据库文件
- 同一个账号在某些请求里“消失”，表现为用户数忽高忽低、登录失败

为保证多实例一致性，需要将认证与会话存储迁移到外部共享数据库。

## 目标

- 使用 Supabase Postgres 作为唯一事实源
- 通过环境变量 `DATABASE_URL` 配置连接串（HF Space Secret）
- 现有 API 保持不变（注册/登录/退出/me、昵称、头像、改密码、管理员接口）
- 不迁移现有 SQLite 数据（切换后重新注册）

## 非目标

- 知识库文件存储迁移（仍在 HF 本地目录）
- 使用 Supabase Auth/RLS（继续使用自研账号体系）

## 接入方案

优先方案：`psycopg2-binary` + 原生 SQL（同步）

- 适配当前同步实现（不引入 async/ORM 的大改动）
- 配合 Supabase Transaction pooler，适用于短连接/无状态请求

## 开关逻辑

- 当 `DATABASE_URL` 存在且非空：认证/会话走 Postgres
- 否则：继续走 SQLite（方便本地运行与单元测试）

## 数据表设计（Postgres）

### users

- `id BIGSERIAL PRIMARY KEY`
- `username TEXT UNIQUE NOT NULL`
- `password_salt TEXT NOT NULL`
- `password_hash TEXT NOT NULL`
- `nickname TEXT`
- `avatar_filename TEXT`
- `created_at BIGINT NOT NULL`

### sessions

- `token TEXT PRIMARY KEY`
- `user_id BIGINT NOT NULL REFERENCES users(id)`
- `created_at BIGINT NOT NULL`
- `expires_at BIGINT NOT NULL`

索引：

- `sessions(user_id)`

## 运行行为

- 启动时执行 `init_db()`：确保表存在
- 不记录 `DATABASE_URL` 明文，不在日志中输出任何密码/连接串
- 若 Postgres 可用：所有副本共享数据，用户不会“消失”

