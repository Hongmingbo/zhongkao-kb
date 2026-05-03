# Upload Enhancement: Pre-upload Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 文件进入上传队列前进行前置校验：空文件/超限/不支持类型/批次内同名重复等，减少无效上传与失败噪音。

**Architecture:** 新增 `frontend/upload_precheck.js`（纯函数：筛选与原因汇总），`enqueueFiles()` 调用该函数后仅把通过的文件入队，并用 `showStatus()` 输出汇总提示。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Create: `frontend/upload_precheck.js`
- Create: `frontend/__tests__/upload-precheck.test.js`
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: upload_precheck（TDD）

**Files:**
- Create: `frontend/upload_precheck.js`
- Create: `frontend/__tests__/upload-precheck.test.js`

- [ ] **Step 1: 写 failing tests（RED）**

```js
const { precheckFiles } = require('../upload_precheck')

function fileLike(name, size, type) {
  return { name, size, type }
}

test('rejects empty file', () => {
  const r = precheckFiles([fileLike('a.txt', 0, 'text/plain')], { maxFileMb: 50 })
  expect(r.accepted.length).toBe(0)
  expect(r.rejected.length).toBe(1)
  expect(r.rejected[0].reason).toBe('empty')
})

test('rejects oversize', () => {
  const r = precheckFiles([fileLike('a.pdf', 51 * 1024 * 1024, 'application/pdf')], { maxFileMb: 50 })
  expect(r.rejected[0].reason).toBe('too_large')
})

test('rejects unsupported ext', () => {
  const r = precheckFiles([fileLike('a.exe', 10, 'application/octet-stream')], { maxFileMb: 50 })
  expect(r.rejected[0].reason).toBe('unsupported')
})

test('dedupes duplicate names in same batch', () => {
  const r = precheckFiles([fileLike('a.txt', 10, 'text/plain'), fileLike('a.txt', 12, 'text/plain')], { maxFileMb: 50 })
  expect(r.accepted.length).toBe(1)
  expect(r.rejected.length).toBe(1)
  expect(r.rejected[0].reason).toBe('duplicate_name')
})

test('summary counts by reason', () => {
  const r = precheckFiles([fileLike('a.txt', 0, 'text/plain'), fileLike('b.exe', 10, '')], { maxFileMb: 50 })
  expect(r.summary.empty).toBe(1)
  expect(r.summary.unsupported).toBe(1)
})
```

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现 upload_precheck.js（GREEN）**
- 支持后缀白名单：`txt, md, pdf, docx, jpg, jpeg, png, webp, zip`
- 规则：
  - `size===0` → empty
  - `size > maxFileMb*1024*1024` → too_large
  - 后缀不在白名单 → unsupported
  - 批次内同名重复 → duplicate_name（保留第一个）
- 输出结构：
  - `accepted: File[]`
  - `rejected: [{ name, reason, size }]`
  - `summary: { empty, too_large, unsupported, duplicate_name }`

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/upload_precheck.js frontend/__tests__/upload-precheck.test.js
git commit -m "feat: add upload precheck"
```

---

### Task 2: 接入 enqueueFiles + 汇总提示

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 引入脚本**
- 在 index.html `<script>` 列表加入 `upload_precheck.js`

- [ ] **Step 2: enqueueFiles 使用 precheckFiles**
- 传入 `maxFileMb: 50`
- 对 rejected：调用 `showStatus()` 输出汇总，例如：
  - `已跳过 3 个文件：空文件 1 / 超限 1 / 不支持 1`
- 对 accepted：沿用原逻辑入队 + pumpQueue

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: validate files before enqueuing upload"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 拖入空文件/超大文件/不支持后缀：不会进入队列，提示原因
- 合法文件正常入队并上传

- [ ] **Step 3: Push**

```bash
git push origin main
```

