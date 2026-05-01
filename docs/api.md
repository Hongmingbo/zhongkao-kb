# API 概览

后端基于 FastAPI，主要接口如下（均以 `/api` 开头）。

## 认证与个人资料

- `POST /api/auth/register`：邀请码注册
- `POST /api/auth/login`：登录获取 token
- `POST /api/auth/logout`：退出
- `GET /api/auth/me`：当前用户信息（含 nickname/has_avatar）

- `POST /api/profile/nickname`：设置昵称
- `POST /api/profile/avatar`：上传头像
- `GET /api/profile/avatar`：获取头像（未上传返回默认头像）
- `POST /api/profile/password`：改密码（旧密码 + 新密码，成功后强制重新登录）

## 管理员

管理员接口通过 `X-Admin-Token` 鉴权：

- `GET /api/admin/users_count`：当前注册用户数
- `POST /api/admin/reset_password`：重置指定用户名密码（成功后清除该用户会话）

## 知识库

- `POST /upload`：上传文件（支持 ZIP）
- `GET /api/stats`：知识库结构
- `GET /api/search`：全文搜索
- `GET /api/filters/options`：筛选项枚举
- `GET /api/filter`：按条件筛选文件
- `DELETE /api/file/{category}/{filename}`：删除文件
- `POST /api/file/batch_move`：批量移动文件到目标学科（同名自动改名）
- `DELETE /api/clear`：清空知识库
- `POST /api/split`：试卷拆题
- `GET /api/questions/{category}/{filename}`：获取拆题结果
