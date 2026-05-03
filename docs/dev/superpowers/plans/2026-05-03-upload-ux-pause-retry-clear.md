# Upload UX: Pause/Resume + Clear Failed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 上传队列新增“暂停/继续（只暂停新任务）”与“一键清空失败”，并保持现有重试逻辑可用。

**Architecture:** 复用现有 `pumpQueue()` 拉起上传的模式，引入 `uploadPaused` 开关；当暂停时 `pumpQueue()` 直接 return，不再开始新的上传。新增 `clearFailedUploads(queue)` 纯函数（只移除 error）。UI 上在队列控制栏新增两个按钮并接入事件。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/upload_queue.js](file:///workspace/zhongkao-kb/frontend/upload_queue.js)
- Create: `frontend/__tests__/upload-ux.test.js`
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: 纯函数（clearFailedUploads + paused gate）TDD

**Files:**
- Create: `frontend/__tests__/upload-ux.test.js`
- Modify: [upload_queue.js](file:///workspace/zhongkao-kb/frontend/upload_queue.js)

- [ ] **Step 1: 写 failing tests（RED）**

```js
const { clearFailedUploads } = require('../upload_queue')

test('clearFailedUploads removes only error items', () => {
  const q = [
    { id: '1', status: 'queued' },
    { id: '2', status: 'error' },
    { id: '3', status: 'success' },
    { id: '4', status: 'uploading' },
  ]
  const out = clearFailedUploads(q)
  expect(out.map(x => x.id)).toEqual(['1', '3', '4'])
})
```

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现最小 clearFailedUploads（GREEN）**

```js
function clearFailedUploads(queue) {
  const items = Array.isArray(queue) ? queue : []
  return items.filter(it => String(it && it.status) !== 'error')
}
```

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/upload_queue.js frontend/__tests__/upload-ux.test.js
git commit -m "feat: add clear failed uploads helper"
```

---

### Task 2: UI 增强（暂停/继续 + 清空失败）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 新增 uploadPaused 状态**
- 默认 `false`

- [ ] **Step 2: pumpQueue 增加暂停 gate**
- 若 `uploadPaused===true`，直接 return

- [ ] **Step 3: renderUploadQueue 控制栏新增按钮**
- 暂停按钮：`data-action="upload-toggle-pause"` 文案随状态切换（暂停/继续）
- 清空失败按钮：`data-action="upload-clear-failed"`

- [ ] **Step 4: 事件处理**
- toggle-pause：切换状态，提示状态栏，若继续则 `pumpQueue()`
- clear-failed：`uploadQueue = clearFailedUploads(uploadQueue)`，并 `renderUploadQueue()`

- [ ] **Step 5: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add upload pause resume and clear failed"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 暂停后：正在上传继续；不再开始新的 queued
- 继续后：queued 继续开始上传
- 清空失败：error 项被移除，其它状态保留

- [ ] **Step 3: Push**

```bash
git push origin main
```

