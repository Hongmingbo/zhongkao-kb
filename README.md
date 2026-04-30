---
title: Zhongkao Knowledge Base
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 中考知识库（Zhongkao Knowledge Base）

把中考复习资料从“文件夹堆积”升级为“可检索的个人资料库”：上传 → 自动归类 → 标签筛选 → 全文搜索 → 拆题复盘。适合日常高频使用（每天上传/整理/查找/复习）。

## 你能做什么

- 多用户登录：邀请码注册 + 用户数据隔离
- 批量上传：支持 `txt/md/pdf/docx/jpg/png/webp/zip`，ZIP 自动解压
- 自动归类：按学科目录管理（语文/数学/英语/物理/化学/历史/政治/生物/地理/其他）
- 元数据打标：年份/地区/类型写入 `.meta.json`，支持筛选面板
- 全文搜索：在整个知识库内进行关键词检索
- 试卷拆题：把试卷切块并输出 questions JSON，便于错题复盘
- OCR/抽取：对 PDF/图片进行文本抽取（依赖环境是否安装 OCR 工具）
- 个人资料：头像、昵称、改密码；管理员支持重置密码与用户数统计

## 在线使用

- 前端：`https://zhongkao-kb.pages.dev/`
- 后端（HF Space 示例）：`https://hmingbo-zhongkao-kb-api.hf.space`

## 文档

- [docs/README.md](file:///workspace/zhongkao-kb/docs/README.md)

## 部署（推荐：Hugging Face Spaces）

完整步骤见：[docs/deployment/huggingface.md](file:///workspace/zhongkao-kb/docs/deployment/huggingface.md)

最少需要配置：

- `INVITE_CODE`（Variable）：注册邀请码
- `DATABASE_URL`（Secret）：Supabase Postgres Transaction pooler URI（强烈推荐，解决 HF 多副本数据不一致）
- `ADMIN_TOKEN`（Secret）：管理员 token

## 本地开发

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

浏览器打开 `http://localhost:8000/`（前端也可直接打开 `frontend/index.html` 进行调试）

## GitHub About 建议（可复制）

**About**

中考资料高频整理与检索工具：上传→自动归类→标签筛选→全文搜索→拆题复盘（多用户/邀请码/可部署）。

**Topics**

`fastapi` `huggingface-spaces` `supabase` `postgresql` `knowledge-base` `ocr` `exam` `education` `full-text-search`
