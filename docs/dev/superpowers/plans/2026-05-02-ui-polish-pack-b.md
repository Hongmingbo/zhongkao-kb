# UI Polish Pack (B) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有蓝+青主题与深色模式基础上，统一全站视觉组件并加入轻量微交互（hover/active/卡片层级/滚动提示），提升整体质感与一致性。

**Architecture:** 继续保持 `frontend/index.html` 单文件。通过 CSS 变量 + 少量语义化 class（btn/chip/card/input）统一样式；微交互只涉及 `transform/opacity/box-shadow`，并尊重 `prefers-reduced-motion`。

**Tech Stack:** Tailwind CDN, 原生 JS, pytest。

---

## 文件改动清单

- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: 主题组件补全（按钮/输入/徽标/卡片）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 扩展 CSS 语义组件**

在 `<style>` 中补充以下 class（不要引入新依赖）：

```css
@media (prefers-reduced-motion: reduce) {
  .motion-safe { transition: none !important; }
}

.motion-safe { transition: transform .16s ease, box-shadow .16s ease, background-color .16s ease, border-color .16s ease, color .16s ease; }
.btn { border-radius: .75rem; padding: .5rem .75rem; }
.btn-accent { background: var(--accent); color: #001018; }
.btn-accent:hover { filter: brightness(0.95); }
.btn:active { transform: translateY(1px); }

.input { border: 1px solid var(--border); background: var(--card); color: var(--text); border-radius: .75rem; padding: .5rem .75rem; }
.input:focus { outline: none; box-shadow: 0 0 0 4px var(--ring); }

.chip { display: inline-flex; align-items: center; gap: .25rem; padding: .125rem .5rem; border-radius: 999px; font-size: 10px; border: 1px solid var(--border); color: var(--muted); background: rgba(148,163,184,0.10); }
.chip-accent { border-color: rgba(6,182,212,0.35); color: var(--accent); background: rgba(6,182,212,0.10); }
.chip-warning { border-color: rgba(245,158,11,0.35); color: #f59e0b; background: rgba(245,158,11,0.10); }
.chip-danger { border-color: rgba(239,68,68,0.35); color: #ef4444; background: rgba(239,68,68,0.10); }

.card-hover:hover { transform: translateY(-1px); box-shadow: 0 12px 30px rgba(2,8,23,0.10); }
html[data-theme="dark"] .card-hover:hover { box-shadow: 0 12px 30px rgba(0,0,0,0.35); }
```

- [ ] **Step 2: 全局替换旧按钮样式**

在以下模块把残留的 `bg-blue-600/bg-gray-100/bg-white border-gray-*` 等替换为：
- 主：`btn-primary btn motion-safe`
- 次：`btn-soft btn motion-safe`
- 危险：`btn-danger btn motion-safe`
- 青强调（推荐用于“批量改标签”等非破坏但强调动作）：`btn-accent btn motion-safe`

覆盖范围（至少）：
- 回收站弹窗
- 批量改标签/重命名/批量重命名弹窗
- 登录/注册弹窗 tab、按钮
- profile-modal（如果仍可打开）

- [ ] **Step 3: 全局替换旧输入样式**

把残留的 `border rounded-lg` 输入统一成 `input motion-safe`（保留原 layout class，如 `w-full`、`flex-1` 等）。

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "style: ui polish pack base components"
```

---

### Task 2: 预览面板信息密度与层级

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 预览头部加类型徽标**

实现一个小工具函数：
- 输入 `filename` → 输出 `ext` 与展示标签（如 `PDF / IMG / TXT / DOCX / OTHER`）

在右侧预览面板 title 区域右侧加入一个 `chip`：
- `PDF` 用 `chip-accent`
- `IMG` 用 `chip-warning`
- 其他用 `chip`

- [ ] **Step 2: 预览内容容器统一底色与滚动提示**

为预览 body 容器增加：
- `max-height` 已有时保留
- 滚动区域顶部阴影提示（仅视觉，CSS `box-shadow` 或 `mask-image`，不做 JS 监听）

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: polish preview panel"
```

---

### Task 3: 列表 hover/active 细节（不改行为）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 卡片与列表行增加轻量 hover**
- 搜索结果卡片、回收站条目、知识库文件行：增加 `motion-safe` + `card-hover`（只用 transform/阴影）

- [ ] **Step 2: 收藏星标交互**
- 星标按钮 hover 更明显（颜色/轻微缩放），active 有按下反馈（复用 `.btn:active` 或局部 class）

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: add subtle micro-interactions"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
pytest -q
```

- [ ] **Step 2: 手工回归清单**
- 深色/浅色切换后：弹窗、输入、按钮颜色不突兀
- hover/active：不抖动、不影响布局
- prefers-reduced-motion：动画被抑制（可简单通过浏览器模拟验证）

- [ ] **Step 3: Push**

```bash
git push origin main
```

