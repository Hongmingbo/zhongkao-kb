---
title: Zhongkao Knowledge Base
emoji: 📚
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
---

# 中考知识库 (Zhongkao Knowledge Base)

一个轻量级的中考知识库全栈项目：

- Web 页面上传资料
- 自动按学科分类（语文/数学/英语/物理/化学/历史/政治/生物/地理/其他）
- ZIP 批量上传与解压
- 文档抽取与转换为 Markdown（PDF/Word/图片等会落为 .md，便于 Hermes 读取）
- 试卷切块（按“一、二、三…”分段）
- 元数据打标（年份/地区/类型）写入 `.meta.json`
- 在线预览/删除

## 本地运行（完整版）

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

浏览器打开 `http://localhost:8000/`

## Hugging Face Spaces（无需绑卡）

本仓库提供了 [Dockerfile](file:///workspace/zhongkao-kb/Dockerfile)，可直接部署到 Hugging Face Docker Space。

1. 在 Hugging Face 创建 Space：SDK 选择 Docker → 模板选 Blank → Hardware 选 CPU Basic（Free）→ Visibility 选 Public
2. 把代码推送到 Space 仓库（会触发自动构建）

Space 的端口固定为 7860，因此 Dockerfile 已配置为监听 7860。
