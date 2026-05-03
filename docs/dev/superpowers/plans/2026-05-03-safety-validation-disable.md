# Safety Polish: Confirm Copy + Input Validation + Disable During Requests Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 统一危险操作确认文案、表单输入校验与请求中按钮禁用，减少误操作与重复提交。

**Architecture:** 新增 `frontend/safety.js`（工具层）：输入校验（用户名/密码/重命名）+ `withDisabled(btn, fn)` 包装器；`index.html` 接入并统一 toast/confirm 文案。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Create: [frontend/safety.js](file:///workspace/zhongkao-kb/frontend/safety.js)
- Create: `frontend/__tests__/safety.test.js`
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: safety.js（校验 + withDisabled）TDD

**Files:**
- Create: [safety.js](file:///workspace/zhongkao-kb/frontend/safety.js)
- Create: `frontend/__tests__/safety.test.js`

- [ ] **Step 1: 写 failing tests（RED）**

```js
const { validateUsername, validatePassword, validateRename, withDisabled } = require('../safety')

test('validateUsername allows cn/en/digits/_/- and enforces 3-32', () => {
  expect(validateUsername('张三')).toEqual({ ok: true, value: '张三' })
  expect(validateUsername('ab')).toEqual({ ok: false })
  expect(validateUsername('a'.repeat(33)).toEqual({ ok: false }))
  expect(validateUsername('a/b')).toEqual({ ok: false })
})

test('validatePassword enforces >= 6', () => {
  expect(validatePassword('12345')).toEqual({ ok: false })
  expect(validatePassword('123456')).toEqual({ ok: true, value: '123456' })
})

test('validateRename rejects empty and slashes', () => {
  expect(validateRename('')).toEqual({ ok: false })
  expect(validateRename('a/b')).toEqual({ ok: false })
  expect(validateRename('a.pdf')).toEqual({ ok: true, value: 'a.pdf' })
})

test('withDisabled disables button during async fn', async () => {
  const btn = document.createElement('button')
  btn.disabled = false
  let inside = false
  await withDisabled(btn, async () => { inside = btn.disabled; return 1 })
  expect(inside).toBe(true)
  expect(btn.disabled).toBe(false)
})
```

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现最小 safety.js（GREEN）**

要求：
- `validateUsername`：trim 后 3-32，允许中文/英文/数字/_/-，禁止 `/` `\\`
- `validatePassword`：trim 后 >=6
- `validateRename`：trim 后非空，禁止 `/` `\\`
- `withDisabled(btn, fn)`：try/finally 恢复 disabled + class `is-disabled`

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/safety.js frontend/__tests__/safety.test.js
git commit -m "feat: add safety helpers for validation and disable"
```

---

### Task 2: index.html 接入 safety.js

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 引入脚本**

在 `usability.js` 之后加入：
`<script src="./safety.js"></script>`

- [ ] **Step 2: 登录/注册**
- 使用 `validateUsername/validatePassword`
- 请求按钮使用 `withDisabled` 防止重复提交
- 校验失败用 toastError（或现有 msg 区域）但文案统一

- [ ] **Step 3: 改密码**
- 校验新密码 >=6 & 两次一致
- 请求中禁用按钮

- [ ] **Step 4: 重命名**
- `validateRename`
- 请求中禁用按钮

- [ ] **Step 5: 其他会发请求的危险按钮**
- 清空知识库/清空回收站/彻底删除/批量操作：统一 confirm 文案
- 请求中禁用（点击后直到请求结束）

- [ ] **Step 6: 提交**

```bash
git add frontend/index.html
git commit -m "feat: apply safety validation and disable to actions"
```

---

### Task 3: 全量回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 登录/注册：非法输入立即提示；请求中按钮不可重复点
- 改密码：长度与一致性提示正确
- 重命名：禁止斜杠；请求中禁用
- 删除/清空：confirm 文案明确且危险按钮风格一致

- [ ] **Step 3: Push**

```bash
git push origin main
```

