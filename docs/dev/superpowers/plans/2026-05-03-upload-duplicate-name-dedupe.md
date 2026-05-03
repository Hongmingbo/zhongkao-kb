# Upload Enhancement: Duplicate Name Deduping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 文件进入队列前检测“同名重复”（本次选择内 + 队列内已有项），默认跳过重复项并给出汇总提示。

**Architecture:** 在 `upload_precheck.js` 的 precheck 中增加 `existingNames` 输入，用于判定与现有队列重复；`enqueueFiles()` 调用 precheck 时传入当前队列文件名集合，并输出“同名重复”跳过提示（最多展示 3 个文件名）。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/upload_precheck.js](file:///workspace/zhongkao-kb/frontend/upload_precheck.js)
- Modify: [frontend/__tests__/upload-precheck.test.js](file:///workspace/zhongkao-kb/frontend/__tests__/upload-precheck.test.js)
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: precheck 支持 existingNames（TDD）

**Files:**
- Modify: [upload-precheck.test.js](file:///workspace/zhongkao-kb/frontend/__tests__/upload-precheck.test.js)
- Modify: [upload_precheck.js](file:///workspace/zhongkao-kb/frontend/upload_precheck.js)

- [ ] **Step 1: 写 failing test（RED）**

```js
test('rejects duplicates against existing queue names', () => {
  const { precheckFiles } = require('../upload_precheck')
  const fileLike = (name, size, type) => ({ name, size, type })
  const existingNames = new Set(['a.txt'])
  const r = precheckFiles([fileLike('a.txt', 10, 'text/plain'), fileLike('b.txt', 10, 'text/plain')], { maxFileMb: 50, existingNames })
  expect(r.accepted.map(x => x.name)).toEqual(['b.txt'])
  expect(r.rejected.map(x => x.reason)).toEqual(['duplicate_name'])
})
```

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现 existingNames 判定（GREEN）**
- 在 `precheckFiles` 内部 `seen` 初始化时合并 `existingNames`（大小写不敏感）

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/upload_precheck.js frontend/__tests__/upload-precheck.test.js
git commit -m "feat: dedupe upload files by existing queue names"
```

---

### Task 2: enqueueFiles 传入队列文件名 + 提示显示文件名样例

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: enqueueFiles 收集现有队列文件名**
- `existingNames = new Set(uploadQueue.map(it => (it && it.name || '').toLowerCase()).filter(Boolean))`
- 传给 `precheckFiles(picked, { maxFileMb: 50, existingNames })`

- [ ] **Step 2: 状态提示带示例文件名**
- 当 `sum.duplicate_name` > 0：
  - 从 `rejected` 里取最多 3 个 `name`
  - `已跳过 X 个重复文件（同名）：a.pdf、b.pdf…`

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: warn and skip duplicate names when enqueuing"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 先加入 a.pdf 到队列，再选 a.pdf + b.pdf：只加入 b.pdf，并提示跳过 a.pdf

- [ ] **Step 3: Push**

```bash
git push origin main
```

