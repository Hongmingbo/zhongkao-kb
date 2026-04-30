# 多用户账号登录（邀请码注册）设计

## 背景与目标

当前系统默认单一知识库空间，所有人共用同一套数据。需要新增账号体系，实现多用户隔离，确保不同用户的数据与操作互不影响，并通过邀请码控制注册入口。

目标：

- 支持注册/登录/退出/查询当前用户
- 注册必须提供邀请码（来源于环境变量）
- 每个用户拥有独立的知识库目录（隔离上传、检索、筛选、拆题、删除、清空等所有数据操作）
- 前端提供登录/注册 UI，登录后自动携带 token 访问后端

非目标（v1 不做）：

- 邮箱/短信验证
- 第三方登录（微信/QQ/Google）
- 复杂权限系统（角色、资源级 ACL）
- 后台管理面板

## 约束与部署考虑

- 后端部署于 Hugging Face Spaces，需使用持久化存储（Spaces 默认持久化工作目录一般可用，但重启可能影响内存态）
- 不引入外部托管数据库（v1 使用本地 SQLite）
- 不在代码中硬编码邀请码（使用环境变量）

## 数据与隔离模型

### 用户与会话

存储：SQLite（例如 `app.db`，位于项目根目录运行时生成）。

表：

- `users`
  - `id`（整数主键）
  - `username`（唯一）
  - `password_salt`（随机）
  - `password_hash`（PBKDF2-HMAC）
  - `created_at`
- `sessions`
  - `token`（随机字符串，主键）
  - `user_id`
  - `created_at`
  - `expires_at`

### 知识库目录隔离

每个用户独立根目录：

- `knowledge_base/u_<user_id>/语文/...`
- `knowledge_base/u_<user_id>/数学/...`

所有涉及文件读写/目录扫描的逻辑必须从“当前用户根目录”开始，而不是使用全局 `knowledge_base/`。

## 鉴权方案（推荐：服务端 Session Token）

- 登录成功：后端生成随机 `token`，写入 `sessions`，返回给前端
- 前端保存 token（localStorage）
- 后续请求：携带 `Authorization: Bearer <token>`
- 后端中间层/依赖解析 token，得到 `current_user`
- token 过期：返回 401，前端提示重新登录

选择原因：

- 不需要引入 JWT 库与签名密钥管理
- token 可随时失效（logout/过期清理）

## 注册策略（邀请码注册）

- 环境变量：`INVITE_CODE`
- `POST /api/auth/register` 必须提交 `invite_code`，与环境变量一致才允许注册
- 若 `INVITE_CODE` 未配置：注册接口返回 503/500 并提示管理员配置（避免误开放）

## API 设计

### `POST /api/auth/register`

请求：

```json
{ "invite_code": "xxxx", "username": "alice", "password": "secret" }
```

返回：

```json
{ "status": "success", "user": { "id": 1, "username": "alice" } }
```

错误：

- 400：字段缺失/格式错误
- 403：邀请码错误
- 409：用户名已存在

### `POST /api/auth/login`

请求：

```json
{ "username": "alice", "password": "secret" }
```

返回：

```json
{ "status": "success", "token": "xxx", "user": { "id": 1, "username": "alice" } }
```

错误：

- 401：用户名或密码错误

### `POST /api/auth/logout`

- 需要鉴权
- 失效当前 token

### `GET /api/auth/me`

- 需要鉴权
- 返回当前用户信息

## 需要鉴权的现有接口范围

下列接口全部需要鉴权，并且将根目录切换为当前用户目录：

- `POST /upload`
- `GET /api/stats`
- `GET /api/search`
- `GET /api/filters/options`
- `GET /api/filter`
- `GET /api/file/{category}/{filename}`
- `DELETE /api/file/{category}/{filename}`
- `DELETE /api/clear`
- `POST /api/split`
- `GET /api/questions/{category}/{filename}`

无需鉴权（保持公开）：

- `GET /api/daily_quote`
- `GET /docs`（FastAPI 文档）
- `GET /`（跳转 Cloudflare Pages）

## 前端交互设计（Cloudflare Pages）

- 首次访问：
  - 若 localStorage 无 token：显示登录/注册弹窗（注册需要邀请码）
- 已有 token：
  - 调用 `/api/auth/me` 验证 token
  - 失败则清除 token 并重新弹出登录
- 登录成功后：
  - 页面右上角显示当前用户名 + 退出按钮
  - 所有 fetch 自动附加 `Authorization` 头

## 安全与边界

- 密码使用 PBKDF2-HMAC（盐 + 多轮迭代），不明文存储
- 不在日志中输出 password/token/invite_code
- token 随机、足够长度，并设置过期时间（例如 7 天）
- 避免目录穿越：category/filename 必须严格作为路径段处理（仍建议后端额外校验 filename 不包含 `..`）

