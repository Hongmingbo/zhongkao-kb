# Brand Accent Bar + Unified Empty States (A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为主要卡片容器加克制的 2px 蓝→青渐变 Accent Bar，并将多个空状态统一为同一套 SVG 图标 + 文案 + 引导动作，提高品牌一致性与质感。

**Architecture:** 不引入图片与外部依赖。仅在 `frontend/index.html` 内增加语义化 class（`accent-card`、`empty-state` 等）与少量渲染辅助函数，复用现有主题变量 `--primary/--accent` 与 `btn` 体系。

**Tech Stack:** Tailwind CDN, 原生 JS, pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: Accent Bar（卡片顶部 2px 品牌线）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 CSS**

在 `<style>` 中添加：

```css
.accent-card { position: relative; overflow: hidden; }
.accent-card::before {
  content: "";
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, rgba(37,99,235,0.70), rgba(6,182,212,0.70));
}
html[data-theme="dark"] .accent-card::before {
  background: linear-gradient(90deg, rgba(96,165,250,0.55), rgba(34,211,238,0.55));
}
```

- [ ] **Step 2: 作用到主要容器**

为以下容器加 `accent-card`：
- 四个主 section（upload/library/search/trash）
- 右侧预览面板容器（sticky card）
- 回收站/设置卡片（如果是单独的 card 容器）

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: add accent bar to main cards"
```

---

### Task 2: 统一 Empty States（不引入图片）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 Empty State 组件样式**

```css
.empty-state { text-align: center; padding: 2.5rem 1rem; }
.empty-icon { width: 44px; height: 44px; margin: 0 auto; color: var(--accent); }
.empty-title { margin-top: .75rem; font-weight: 600; color: var(--text); }
.empty-desc { margin-top: .25rem; font-size: 14px; color: var(--muted); }
```

- [ ] **Step 2: 添加渲染函数**

在脚本中加入：
- `function emptyIcon(name) -> svg string`（至少提供 `upload/search/trash/star` 四种）
- `function renderEmptyState({icon, title, desc, primaryActionText, primaryActionHandler}) -> html`

并在渲染后绑定按钮点击事件（使用 `data-empty-action`）。

- [ ] **Step 3: 替换当前空状态文本**

覆盖以下场景：
- 知识库为空（引导：去上传 tab）
- 搜索无结果（引导：清除搜索 + 聚焦输入）
- 回收站为空（无操作或“返回知识库”）
- 只看收藏为空（引导：去知识库/取消勾选“只看收藏”）

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "style: unify empty states"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
pytest -q
```

- [ ] **Step 2: 手工回归**
- 浅色/深色：accent bar 亮度合适，不刺眼
- 空状态：文案一致、按钮可点、跳转正确

- [ ] **Step 3: Push**

```bash
git push origin main
```

