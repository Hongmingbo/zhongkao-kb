# 配置（环境变量）

## 后端环境变量

### 必需（生产建议）

- `INVITE_CODE`：注册邀请码（注册接口会校验）
- `DATABASE_URL`：认证与会话数据库（Supabase Postgres Transaction pooler URI，建议作为 Secret）

### 管理员

- `ADMIN_TOKEN`：管理员 token（建议作为 Secret）
  - Header 使用 `X-Admin-Token: <ADMIN_TOKEN>`

### 可选（本地/单实例）

- `APP_DB_PATH`：SQLite 文件路径（未配置 `DATABASE_URL` 时生效）

## 前端配置

前端默认后端地址写在 `frontend/index.html` 的 `API_BASE` 常量中。

