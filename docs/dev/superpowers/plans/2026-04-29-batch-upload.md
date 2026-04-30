# 批量上传 v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在前端实现批量上传：支持一次选择/拖拽多个文件，按并发 3 的策略逐个向后端 `/upload` 提交，并展示每个文件的状态（等待/上传中/成功/失败），全部完成后刷新目录。

**Architecture:** 仅改前端：将文件输入改为 `multiple`，将 drop 事件处理为多文件；在前端维护一个上传队列（数组），调度器按并发上限启动多个 `fetch('/upload')`，每个任务完成后更新队列并启动下一任务；队列空且无进行中任务时触发 `loadStats()`。

**Tech Stack:** 纯前端 JS（fetch + FormData），Cloudflare Pages 静态托管；后端接口不变（FastAPI `/upload`）。

---

## File Structure

**Modify**
- `frontend/index.html`：上传区块支持多文件、队列 UI、并发调度器

---

### Task 1: 调整上传输入与拖拽，支持一次选择/拖拽多个文件

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 将文件输入改为 multiple**

把：

```html
<input id="file-upload" name="file-upload" type="file" class="absolute inset-0 opacity-0 cursor-pointer">
```

改为：

```html
<input id="file-upload" name="file-upload" type="file" multiple class="absolute inset-0 opacity-0 cursor-pointer">
```

- [ ] **Step 2: 修改 change 事件处理为批量**

将 `change` 回调中从单文件改为遍历 `this.files` 并调用 `enqueueFiles([...])`。

- [ ] **Step 3: 修改 drop 事件处理为批量**

将 drop 回调中从单文件改为 `enqueueFiles([...files])`。

- [ ] **Step 4: 手工验证**

在页面中：
- “选择文件”一次选多个文件
- 拖拽多个文件到虚线框

预期：不会报错，且会进入队列（下一任务会实现队列 UI）。

- [ ] **Step 5: Commit**

```bash
git add frontend/index.html
git commit -m "feat: 支持批量选择与拖拽多个文件"
```

---

### Task 2: 增加队列 UI（状态列表）

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 添加队列容器**

在上传区块内（上传框下方、状态提示上方）新增：

```html
<div id="upload-queue" class="mt-4 hidden"></div>
```

- [ ] **Step 2: 定义队列数据结构**

在 script 中新增：

```js
const MAX_BATCH_FILES = 50
const UPLOAD_CONCURRENCY = 3
let uploadQueue = []
```

每个 item：

```js
{ id, file, name, status: 'queued'|'uploading'|'success'|'error', category, message }
```

- [ ] **Step 3: 实现渲染函数**

新增 `renderUploadQueue()`：把队列渲染为列表，显示文件名与状态。

- [ ] **Step 4: 实现 enqueueFiles**

新增 `enqueueFiles(files)`：
- 超过 50 个只取前 50 个并提示
- 生成队列项（status=queued），push 进 `uploadQueue`
- 调用 `renderUploadQueue()` 和 `pumpQueue()`

- [ ] **Step 5: 手工验证**

选择/拖拽多个文件后：
- 预期：队列区域出现，显示多行“等待/排队中”

- [ ] **Step 6: Commit**

```bash
git add frontend/index.html
git commit -m "feat: 增加批量上传队列 UI"
```

---

### Task 3: 实现并发调度器（并发 3）与状态更新

**Files:**
- Modify: `frontend/index.html`

- [ ] **Step 1: 实现 pumpQueue 调度器**

新增：
- `let activeUploads = 0`
- `pumpQueue()`：当 `activeUploads < UPLOAD_CONCURRENCY` 时，从队列里取下一个 `queued` 项开始上传

- [ ] **Step 2: 复用现有 upload 逻辑改为“单项上传函数”**

把现有 `uploadFile(file)` 拆成：

```js
async function uploadOne(queueItem) { ... }
```

要求：
- 开始时：status=uploading，activeUploads++
- 成功时：status=success，记录 category（从后端返回 results[0].category）
- 失败时：status=error，记录 message
- finally：activeUploads--，renderUploadQueue()，pumpQueue()
- 当队列内无 queued 且 activeUploads==0：调用 `loadStats()`

- [ ] **Step 3: 错误处理**

- 单个文件失败不影响其它文件继续
- 后端响应异常时写入 message（status code 或 data.message）

- [ ] **Step 4: 清空知识库后清空队列**

在现有清空成功逻辑里，追加：

```js
uploadQueue = []
renderUploadQueue()
```

- [ ] **Step 5: 手工验证**

- 同时选择 5 个文件上传
- 预期：同一时间最多 3 个显示“上传中”，其余显示“等待”
- 全部完成后目录自动刷新

- [ ] **Step 6: Commit**

```bash
git add frontend/index.html
git commit -m "feat: 批量上传并发调度与状态更新"
```

---

### Task 4: 发布与验证（GitHub → Cloudflare Pages）

**Files:**
- No code changes required

- [ ] **Step 1: 推送到 GitHub**

```bash
git push origin main
```

- [ ] **Step 2: 等待 Cloudflare Pages 自动部署**

如未自动触发，在 Pages 项目 Deployments 中点击 Redeploy。

- [ ] **Step 3: 线上验证**

打开 `https://zhongkao-kb.pages.dev`：
- 一次选择多个文件并上传
- 观察队列状态变化与并发限制
- 全部完成后目录是否刷新

---

## Self-Review（计划自检）

- 覆盖 spec：多选、拖拽多文件、并发 3、状态列表、完成后刷新目录、上限 50、失败不影响其他、清空后清队列。
- 无占位步骤：每步包含路径/代码/命令或明确验证方式。

