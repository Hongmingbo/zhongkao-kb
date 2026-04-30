# 头像与昵称 v1（多用户）

## 背景与目标

已实现多用户账号登录（邀请码注册）与用户数据隔离。需要补充“个人资料”能力，使用户可设置昵称与头像，并在前端右上角显示，提升可用性与识别度。

目标：

- 用户可设置昵称（nickname），不影响登录用户名（username）
- 用户可上传头像图片（png/jpg/jpeg/webp，≤2MB）
- 未上传头像时，后端返回统一默认头像图片（B 方案）
- 前端右上角用户栏显示：头像 + 昵称/用户名 + 设置 + 退出

非目标（v1 不做）：

- 修改登录用户名（username）
- 头像裁剪、滤镜、压缩优化
- 多端同步/历史头像
- 后台管理面板

## 数据模型

SQLite `users` 表新增字段：

- `nickname TEXT`：可空；前端显示优先使用 nickname，否则用 username
- `avatar_filename TEXT`：可空；记录用户头像文件名（例如 `avatar.png`）

存储位置（按用户隔离）：

- 用户头像：`knowledge_base/u_<user_id>/_profile/avatar.<ext>`
- 默认头像：由后端内置返回（统一一张）

## API 设计

鉴权：以下接口均需要 `Authorization: Bearer <token>`。

### 1) `POST /api/profile/nickname`

请求：

```json
{ "nickname": "小明" }
```

规则：

- 允许空字符串（表示清空昵称）
- 非空时长度 1–20（去除首尾空格）

返回：

```json
{ "status": "success", "nickname": "小明" }
```

### 2) `POST /api/profile/avatar`

上传：`multipart/form-data`，字段名 `file`

规则：

- 允许类型：`image/png`、`image/jpeg`、`image/webp`
- 最大 2MB
- 上传成功后写入用户目录 `_profile/`，并更新 `users.avatar_filename`

返回：

```json
{ "status": "success" }
```

### 3) `GET /api/profile/avatar`

行为：

- 若用户上传过头像：返回用户头像二进制（带正确 content-type）
- 否则：返回默认头像二进制（统一一张）

### 4) `GET /api/auth/me`（扩展）

在现有返回基础上，新增：

- `nickname`
- `has_avatar`（boolean）

## 前端交互

- 右上角用户栏展示：头像（圆形） + 昵称/用户名 + 设置 + 退出
- “设置”弹窗：
  - 昵称输入框（保存）
  - 头像上传（选择文件后上传并刷新头像展示）
- 页面加载时：
  - `/api/auth/me` 获取用户信息
  - 调用 `/api/profile/avatar` 获取头像（或用 `<img src=...>` 直接请求）

## 安全与边界

- 头像上传不记录/回显原始文件名
- 严格校验 content-type 与大小上限，避免大文件滥用
- 路径固定到用户目录 `_profile/`，避免路径穿越

