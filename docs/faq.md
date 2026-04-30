# FAQ

## 1) 为什么用户数据会“忽多忽少”？

在 Hugging Face 多实例环境中，如果认证使用本地 SQLite，会出现不同副本读到不同数据库文件的问题。解决方案：配置 `DATABASE_URL` 使用 Supabase Postgres（Transaction pooler）。

## 2) Hugging Face Logs 报 `password authentication failed`

通常是 `DATABASE_URL` 里仍包含 `[YOUR-PASSWORD]`，或密码填错。建议在 Supabase 重置数据库密码（用纯字母数字），再重新复制 Transaction pooler URI。

## 3) 上传头像后为什么不显示在知识库结构里？

系统目录 `_profile` 会被隐藏：后端 stats/filter/options 会跳过以下划线开头的目录，避免头像等系统文件干扰知识库目录展示。

## 4) 为什么改密码后需要重新登录？

改密码/管理员重置密码会清除该用户所有会话（sessions），这是为了安全（避免旧 token 继续有效）。

