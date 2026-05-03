# Upload Polish: Highlight New Files + Collapsible Queue + History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 批量上传完成后自动跳转知识库并高亮新文件；上传队列支持折叠摘要；保留最近一次上传历史并支持失败重试。

**Architecture:** 前端纯实现：在上传流程记录本次成功文件 `{category, filename}` 列表；上传结束时自动切到 library 并在 `loadStats/renderGroupedFiles` 渲染后滚动定位与短暂高亮；队列折叠状态与历史存储在 localStorage；失败重试复用现有 `retryFailedUploads/retryOneUpload` 机制。

**Tech Stack:** Tailwind CDN, 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Modify: [frontend/upload_queue.js](file:///workspace/zhongkao-kb/frontend/upload_queue.js)
- Create: `frontend/__tests__/upload-polish.test.js`

---

### Task 1: 记录“本次上传成功文件列表”

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Test: `frontend/__tests__/upload-polish.test.js`

- [ ] **Step 1: 写 failing test（RED）**

为纯函数 `mergeLastUploadSuccess(prev, item)` 写测试：
- 仅当 `item.status === 'success' && item.category && item.name` 时记录
- 去重（同 category+filename 只保留一次）
- 返回 `[{ category, filename }]` 结构

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现最小代码（GREEN）**

在 `upload_queue.js` 新增并导出：

```js
function mergeLastUploadSuccess(prev, item) {}
```

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/upload_queue.js frontend/__tests__/upload-polish.test.js
git commit -m "feat: track last upload success list"
```

---

### Task 2: 上传完成后自动跳转知识库并高亮新文件

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Test: `frontend/__tests__/upload-polish.test.js`

- [ ] **Step 1: 写 failing test（RED）**

为纯函数 `makeHighlightKey(category, filename)` 与 `shouldAutoClearFilters(filterActive)` 写测试：
- key 规则固定（避免之后改动导致定位失败）
- 发生“上传后高亮”时若 `filterActive`，返回 true（并触发 UI toast）

- [ ] **Step 2: 实现（GREEN）**

实现策略：
- `uploadOne` 成功时把 `{category, filename}` 写入 `lastUploadSuccess`（内存）并同步到 localStorage（例如 `ZKKB_LAST_UPLOAD_SUCCESS`）
- 上传队列结束（无 queued 且无 uploading）时：
  - 若 `filterActive`：执行 `clearFilters(false)` 并 toastInfo 提示“已清除筛选以展示新上传文件”
  - 设置 `location.hash = '#/library'` 并 `await loadStats()`
  - `loadStats/renderGroupedFiles` 渲染完成后，寻找匹配条目的 DOM 节点（通过 `data-key` 或新增 `data-file-key`），scrollIntoView，添加高亮 class，2.5s 后移除

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: auto jump and highlight uploaded files"
```

---

### Task 3: 队列折叠摘要

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 新增折叠状态**

localStorage：
- `ZKKB_UPLOAD_QUEUE_COLLAPSED` = `1|0`

- [ ] **Step 2: renderUploadQueue 支持折叠**

折叠时仅渲染：
- 队列头部（进度条 + 成功/失败/上传中/等待计数）
- 明细区隐藏

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add collapsible upload queue"
```

---

### Task 4: 保留最近一次上传历史（含失败重试）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Test: `frontend/__tests__/upload-polish.test.js`

- [ ] **Step 1: 写 failing test（RED）**

为纯函数 `snapshotUploadHistory(queue)` 写测试：
- 输出只包含必要字段（id/name/status/category/message）
- 不存 File 对象

- [ ] **Step 2: 实现（GREEN）**

策略：
- 上传结束时 `lastUploadHistory = snapshotUploadHistory(uploadQueue)` 并存 localStorage（如 `ZKKB_LAST_UPLOAD_HISTORY`）
- “清空队列”只清理当前队列的 queued/error（现有规则），历史独立存在
- 在队列折叠区提供“查看上次历史 / 清空历史”按钮
- 历史中的失败项点“重试”会重新加入当前队列（复用 `enqueueFiles` 思路：用 name 做展示，用 message 说明，实际重试仍需要原 File，因此历史重试仅对“当前队列失败项”提供；历史面板只做查看 + 一键把失败项提示用户重新选择文件）

> 说明：纯前端无法在刷新后重传原 File，因此“历史重试”仅对未刷新会话内有效；刷新后展示历史但不可直接重传，UI 提示“请重新选择原文件上传”。

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html frontend/__tests__/upload-polish.test.js frontend/upload_queue.js
git commit -m "feat: add last upload history panel"
```

---

### Task 5: 全量回归与推送

- [ ] **Step 1: 全量测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 上传完成自动跳转知识库，高亮并滚动定位
- 开启筛选后上传：自动清筛选并提示
- 队列折叠/展开正常
- 历史可查看/可清空；刷新后历史仍在但提示无法直接重传

- [ ] **Step 3: Push**

```bash
git push origin main
```

