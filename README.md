# 中考知识库 (Zhongkao Knowledge Base)

这是一个轻量级的中考知识库仓库，专为 Hermes 等 AI 智能助手或 RAG (检索增强生成) 系统设计。

## 核心功能

- **Web 界面上传**：整洁无 Bug 的拖拽式上传页面。
- **自动分类引擎**：根据文件名和文本内容，自动将文件分类至对应的学科目录（如：语文、数学、物理等）。
- **极简结构**：文件直接以明文/原文件格式存储在 `knowledge_base` 目录下，方便 Hermes 等模型直接挂载或读取。

## 快速启动

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

3. **访问网页**
   打开浏览器访问 `http://localhost:8000` 即可使用。

## 推送至你的 GitHub

```bash
git remote add origin <你的Github仓库URL>
git branch -M main
git push -u origin main
```
