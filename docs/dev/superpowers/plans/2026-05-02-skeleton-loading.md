# Skeleton Loading (A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为知识库列表、搜索结果、回收站列表加入统一骨架屏（浅色/深色适配，尊重 `prefers-reduced-motion`），替换“加载中...”的廉价感。

**Architecture:** 在 `frontend/index.html` 内实现：CSS 提供 `skeleton-*` 组件与可选 shimmer；JS 提供 `renderSkeleton*` 辅助函数与少量加载状态控制，不改 API 协议。

**Tech Stack:** Tailwind CDN, 原生 JS, pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: Skeleton 样式与渲染函数

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 CSS（含 prefers-reduced-motion）**

```css
.skeleton { background: rgba(148,163,184,0.16); border-radius: .75rem; }
html[data-theme="dark"] .skeleton { background: rgba(148,163,184,0.10); }
.skeleton-line { height: 12px; }
.skeleton-chip { height: 18px; width: 52px; border-radius: 999px; }
.skeleton-card { border: 1px solid var(--border); background: var(--card); border-radius: .75rem; overflow: hidden; }
.skeleton-body { padding: .75rem; display: grid; gap: .5rem; }
.shimmer { position: relative; overflow: hidden; }
.shimmer::after { content:""; position:absolute; inset:0; transform: translateX(-100%); background: linear-gradient(90deg, transparent, rgba(255,255,255,0.35), transparent); animation: shimmer 1.1s infinite; }
html[data-theme="dark"] .shimmer::after { background: linear-gradient(90deg, transparent, rgba(255,255,255,0.18), transparent); }
@keyframes shimmer { 100% { transform: translateX(100%); } }
@media (prefers-reduced-motion: reduce) { .shimmer::after { animation: none; } }
```

- [ ] **Step 2: 添加渲染函数**

实现：
- `renderSkeletonList(count, variant)`：`variant in ['kb','search','trash']`
- 默认 `count=6`，返回一段 HTML

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: add skeleton components"
```

---

### Task 2: 绑定到知识库/搜索/回收站加载流程

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 知识库**
- 初始与刷新时：`kbStats.innerHTML = renderSkeletonList(6,'kb')`
- 请求结束后再渲染真实列表/空状态

- [ ] **Step 2: 搜索**
- 发起搜索后立即显示 `renderSkeletonList(4,'search')`
- 请求结束后渲染真实结果/空状态

- [ ] **Step 3: 回收站**
- 打开/刷新回收站时：`trashList.innerHTML = renderSkeletonList(4,'trash')`（同理 trashListPage）
- 请求结束后渲染真实列表/空状态

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "style: apply skeleton loading"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
pytest -q
```

- [ ] **Step 2: 手工回归**
- 三处加载都出现 skeleton，并在数据返回后替换
- 深色模式 skeleton 不发白
- reduced-motion 下 shimmer 停止

- [ ] **Step 3: Push**

```bash
git push origin main
```

