# Download From Lists Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在知识库/搜索/收藏列表的操作区新增“下载”按钮，点击后用带鉴权的 fetch+blob 直接下载原文件。

**Architecture:** 复用后端现有 `GET /api/file/raw/{category}/{filename}`。前端新增 `downloadFile(category, filename, btn?)`，内部调用 `apiFetch` 获取 blob 并通过 `<a download>` 保存；并复用 `withDisabledFn` 防重复点击。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Create: `frontend/__tests__/download.test.js`

---

### Task 1: downloadFile 工具函数（TDD）

**Files:**
- Create: `frontend/__tests__/download.test.js`
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 写 failing test（RED）**

```js
test('downloadFile requests raw endpoint with auth and triggers a download', async () => {
  const { _downloadInternals } = require('../download_internals')
  expect(typeof _downloadInternals.downloadFile).toBe('function')
})
```

该 test 预期失败（模块不存在）。

- [ ] **Step 2: 实现最小 downloadFile（GREEN）**

实现要点：
- url: `/api/file/raw/${encodeURIComponent(category)}/${encodeURIComponent(filename)}`
- `apiFetch(url)` 获取 `blob()`
- `URL.createObjectURL(blob)` → `<a download>` click → revoke
- 成功 toastSuccess，失败 toastError

- [ ] **Step 3: 跑 jest 通过**

```bash
npm run test:js
```

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html frontend/__tests__/download.test.js
git commit -m "feat: add download helper for raw files"
```

---

### Task 2: 列表操作区新增“下载”按钮 + 事件处理

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 知识库列表**
- 操作区新增 `<button data-action="download">下载</button>`
- 点击时调用 `downloadFile(category, filename, btn)`

- [ ] **Step 2: 搜索结果**
- 操作区新增 “下载”
- bindSearchResults 支持 `download`

- [ ] **Step 3: 收藏页**
- 非 missing 项操作区新增 “下载”
- favoritesList click handler 支持 `download`

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add download action to file lists"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 任意二进制文件（pdf/png/docx）点击“下载”能保存
- txt/md 也能下载（从 raw 接口拿 bytes）
- 未登录时点击下载会弹登录（401 流程）

- [ ] **Step 3: Push**

```bash
git push origin main
```

