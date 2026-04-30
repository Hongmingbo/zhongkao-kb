# Hugging Face Spaces 部署（Docker）

本项目支持一键部署到 Hugging Face Docker Space，并推荐使用 Supabase Postgres 作为认证数据库（解决多实例导致的用户数据不一致）。

## 1. 创建 Space

1. 新建 Space：SDK 选择 Docker，模板选 Blank
2. Hardware：CPU Basic（Free）
3. Visibility：按需选择 Public/Private

## 2. 推送代码

从你的本地仓库推送到 HF Space：

```bash
git push -f hf main
```

Space 会自动构建并启动（容器端口为 7860）。

## 3. 必需环境变量（推荐配置）

在 Space Settings → Variables and secrets 中配置：

- `INVITE_CODE`（Variable）：注册邀请码
- `ADMIN_TOKEN`（Secret）：管理员 token（用于统计用户数、重置密码）
- `DATABASE_URL`（Secret）：Supabase Postgres Transaction pooler 的 URI

说明：

- `DATABASE_URL` 必须使用 Secret，禁止放在 public variable
- `DATABASE_URL` 里要把 `[YOUR-PASSWORD]` 替换为数据库密码

## 4. 启动日志自检

Space Logs 中应看到：

- `[startup] AUTH_DB_BACKEND=postgres`
- `[startup] DATABASE_URL=set`
- `[startup] DB_INIT_OK`

若出现 `password authentication failed`：
- 检查连接串中是否仍含 `[YOUR-PASSWORD]`
- 或重置 Supabase 数据库密码后重新复制 Transaction pooler URI

