# Usability Polish: Global Shortcuts + Copy Actions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 增加全局快捷键（`/`、`Esc`、`Ctrl/Cmd+K`）与高频复制能力（复制文件名/复制链接），并用 Toast 做统一反馈，提升效率与“产品感”。

**Architecture:** 只改 `frontend/index.html`：新增 `copyText()` 与全局 `keydown` 监听；在列表 hover 操作区与预览区新增 `data-action` 按钮并复用现有事件委托（`bindSearchResults` 等）。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Create: `frontend/__tests__/usability.test.js`

---

### Task 1: copyText 工具与 Toast 反馈

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Test: `frontend/__tests__/usability.test.js`

- [ ] **Step 1: 写 failing test（RED）**

`copyText`：
- 有 `navigator.clipboard.writeText` 时调用它
- 否则 fallback 到临时 `<textarea>` + `document.execCommand('copy')`

Jest 中通过注入 `navigator.clipboard.writeText = jest.fn()` 验证调用。

- [ ] **Step 2: 实现 copyText（GREEN）**

新增：
- `async function copyText(text) -> boolean`
- 成功：`toastSuccessFn('已复制')`
- 失败：`toastErrorFn('复制失败', reason)`

- [ ] **Step 3: 运行 jest 并提交**

```bash
npm run test:js
git add frontend/index.html frontend/__tests__/usability.test.js
git commit -m "feat: add copyText helper"
```

---

### Task 2: 复制文件名（知识库/搜索/回收站）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 知识库列表操作区新增按钮**

在每个条目的 hover 操作区加：
- `data-action="copy-name"` 并带 `data-filename`

- [ ] **Step 2: 搜索结果卡片新增按钮**

在搜索结果卡片右侧操作区加：
- `复制文件名`
- （可选）`复制路径`（category/filename）

- [ ] **Step 3: 回收站条目新增按钮**

在回收站条目右侧操作区加：
- `复制文件名`

- [ ] **Step 4: 绑定事件**

在对应的事件委托中处理 `copy-name`：
- `await copyText(filename)`

- [ ] **Step 5: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add copy filename actions"
```

---

### Task 3: 复制链接（预览区）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 预览区新增“复制链接”按钮**

在 `renderPreviewTo()` 里生成 `rawUrl` 时：
- 与“下载/打开原文件”同一行新增按钮 `data-action="copy-link"` `data-url="..."`

- [ ] **Step 2: 绑定事件**

在预览容器 click handler 中处理：
- `await copyText(url)`

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add copy preview link action"
```

---

### Task 4: 全局快捷键

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Test: `frontend/__tests__/usability.test.js`

- [ ] **Step 1: 写 failing test（RED）**

验证：
- `Ctrl/Cmd+K` 会把 tab 切到 search 并 focus 搜索框
- `/` 同上（但不在 input/textarea 聚焦时触发）
- `Esc` 关闭预览 modal / confirm modal（若打开）

- [ ] **Step 2: 实现（GREEN）**

新增 `document.addEventListener('keydown', ...)`：
- `/`：`preventDefault`，切到 search，focus
- `Ctrl/Cmd+K`：同上
- `Esc`：优先关闭 confirm，再关闭 preview

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html frontend/__tests__/usability.test.js
git commit -m "feat: add global shortcuts"
```

---

### Task 5: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 任意页面按 `/`、`Ctrl/Cmd+K` 应跳到搜索并聚焦
- `Esc` 能关闭 confirm / 预览弹窗
- “复制文件名/复制链接”在 HTTPS 环境可用（HF）

- [ ] **Step 3: Push**

```bash
git push origin main
```

