# Toast + Confirm Modal (A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 使用右上角 Toast 替代 `alert()`，使用统一 Confirm Modal 替代 `confirm()`，提升产品感与反馈一致性，并在全站破坏性操作中落地。

**Architecture:** 在 `frontend/index.html` 单文件内实现：新增 Toast 容器与 Confirm Modal HTML；新增 `toast*` 与 `confirmDialog` 两类 API；逐步替换现有 `alert/confirm` 调用点。

**Tech Stack:** Tailwind CDN, 原生 JS, pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: Toast 组件（右上角）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 Toast 容器 HTML**

在 `<body>` 内靠近末尾（modal 附近）增加：

```html
<div id="toast-stack" class="fixed top-4 right-4 z-[60] space-y-2 w-[340px] max-w-[calc(100vw-2rem)] pointer-events-none"></div>
```

- [ ] **Step 2: 添加 CSS class**

```css
.toast { pointer-events: auto; border: 1px solid var(--border); background: var(--card); border-radius: .75rem; padding: .75rem .75rem .75rem .75rem; box-shadow: 0 14px 40px rgba(2,8,23,0.10); }
html[data-theme="dark"] .toast { box-shadow: 0 18px 48px rgba(0,0,0,0.40); }
.toast-bar { width: 3px; border-radius: 999px; }
.toast-title { font-weight: 600; color: var(--text); font-size: 14px; }
.toast-desc { margin-top: 2px; color: var(--muted); font-size: 13px; }
```

- [ ] **Step 3: 添加 JS API**

实现：
- `toast({ type, title, desc, timeoutMs })`
- `toastSuccess(title, desc?) / toastError(...) / toastInfo(...)`
- 堆叠上限 3 条；超出移除最旧
- 默认 `timeoutMs=3000`；提供关闭按钮
- 容器 `aria-live="polite"`

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add toast notifications"
```

---

### Task 2: Confirm Modal（替代 confirm）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 Confirm Modal HTML**

```html
<div id="confirm-modal" class="fixed inset-0 z-[70] hidden bg-gray-900 bg-opacity-50 flex items-center justify-center p-4">
  <div class="bg-card rounded-xl shadow-lg w-full max-w-md card-border">
    <div class="p-4 card-border border-b flex items-center justify-between">
      <div id="confirm-title" class="text-lg font-semibold" style="color: var(--text);"></div>
      <button id="confirm-close" class="text-gray-400 hover:text-gray-600 focus:outline-none">×</button>
    </div>
    <div class="p-4 space-y-4">
      <div id="confirm-message" class="text-sm muted"></div>
      <div class="flex justify-end gap-2">
        <button id="confirm-cancel" class="px-4 py-2 rounded-lg text-sm btn btn-soft motion-safe">取消</button>
        <button id="confirm-ok" class="px-4 py-2 rounded-lg text-sm btn btn-danger motion-safe">确认</button>
      </div>
    </div>
  </div>
</div>
```

- [ ] **Step 2: 添加 JS API**

实现 Promise API：

```js
function confirmDialog({ title, message, confirmText, tone }) { /* returns Promise<boolean> */ }
```

支持：
- ESC 关闭 = false
- 点击遮罩/关闭按钮 = false
- `tone` 控制确认按钮 class（`btn-danger`/`btn-primary`）
- 默认聚焦取消按钮

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add confirm dialog"
```

---

### Task 3: 替换 alert/confirm 调用点

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 替换 alert**
- `toggleFavorite` 失败提示 → `toastError`
- 回收站恢复/删除失败等 → `toastError`
- profile / settings 保存成功/失败 → `toastSuccess/toastError`

- [ ] **Step 2: 替换 confirm**
- `deleteTrash` / `clearTrashAll` / 清空知识库 / 删除文件等破坏性操作 → `await confirmDialog(...)`

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "refactor: replace alert/confirm with toast dialogs"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
pytest -q
```

- [ ] **Step 2: 手工回归**
- 右上角 toast 堆叠、自动消失、可关闭
- 破坏性操作弹 confirm modal，按钮与 ESC 行为正确

- [ ] **Step 3: Push**

```bash
git push origin main
```

