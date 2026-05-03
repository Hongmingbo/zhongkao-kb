# Upload Queue Progress + Retry (A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为批量上传队列增加整体进度条（已完成/总数），并提供失败单条重试、清空队列等操作，提升上传体验与可控性。

**Architecture:** 仍使用现有 `uploadQueue + pumpQueue + uploadOne` 并发模型；新增纯前端 UI 计算（完成数、失败数、总数）；重试逻辑只重置指定队列项状态并重新入队；所有提示/确认复用 Toast/Confirm。

**Tech Stack:** Tailwind CDN, 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- (Optional) Modify: [frontend/__tests__/feedback.test.js](file:///workspace/zhongkao-kb/frontend/__tests__/feedback.test.js)
- Create: `frontend/__tests__/upload-queue.test.js`

---

### Task 1: 进度条与队列操作区 UI

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 队列渲染加入“进度条头部”**

在 `renderUploadQueue()` 的 HTML 顶部加入：
- 文案：`已完成 X / N`（完成 = success+error）
- 进度条：`width = Math.round((done/total)*100)%`
- 失败提示：存在失败时显示 `失败 Y`（chip-danger）

- [ ] **Step 2: 队列操作按钮**

在队列头部右侧加：
- “重试失败”（仅当存在失败项时显示）
- “清空队列”（清空 queued+error；保留 uploading/success 或全部清空由下一步决定）

按钮触发 confirmDialog：
- 清空队列：`title=清空上传队列？ message=将移除等待/失败项…`
- 重试失败：`title=重试失败项？ message=将重新上传失败的 Y 个文件…`

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: add upload queue progress header"
```

---

### Task 2: 失败单条重试与批量重试

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 单条重试按钮**

在每个队列条目：
- status=error 时显示 “重试” 按钮（btn-soft）
- 点击后将该 item 重置为 `queued`，清空 `message/category`，并触发 `pumpQueue()`

- [ ] **Step 2: 批量重试失败**

点击“重试失败”：
- 批量把 `status=error` 的 item 重置为 `queued`
- toastInfo：`已重新加入队列：Y`
- 触发 `pumpQueue()`

- [ ] **Step 3: 清空队列规则**

默认策略（推荐）：
- 仅清除 `queued + error`；保留 `uploading + success`
原因：避免误清进行中的上传，且保留成功结果便于用户确认。

- [ ] **Step 4: 结束 toast**

当队列没有 queued/uploading 时：
- toastInfo：`上传完成：成功 X，失败 Y`

- [ ] **Step 5: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add upload retry and clear queue"
```

---

### Task 3: JS 单测（Jest + jsdom）

**Files:**
- Create: [upload-queue.test.js](file:///workspace/zhongkao-kb/frontend/__tests__/upload-queue.test.js)

- [ ] **Step 1: 红灯测试（先写失败）**

用 jsdom 构造一个最小 DOM（含 `upload-queue` 容器），注入 `renderUploadQueue()` 相关函数（建议把逻辑提取为纯函数 `calcUploadProgress(queue)`，避免强耦合 DOM）。

测试：
- `calcUploadProgress` 的 `done/total/fail` 计算
- 单条 retry 会把 item.status 从 error 置回 queued
- 清空队列只移除 queued+error（默认策略）

- [ ] **Step 2: 跑测试确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现最小代码让测试通过**

- [ ] **Step 4: 再跑测试确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/__tests__/upload-queue.test.js frontend/index.html
git commit -m "test: add upload queue progress tests"
```

---

### Task 4: 全量回归与推送

- [ ] **Step 1: 全量测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 选择 2-3 个文件，观察进度条随完成数变化
- 断网或填错后端地址触发失败，出现“重试”与“重试失败”
- 清空队列不会影响正在上传的条目

- [ ] **Step 3: Push**

```bash
git push origin main
```

