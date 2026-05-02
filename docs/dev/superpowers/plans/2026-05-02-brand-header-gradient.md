# Brand Header Gradient (A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为「中考知识库」标题加入克制的蓝→青渐变字与一条轻量品牌线（浅色/深色一致可读），提升品牌感但不花哨。

**Architecture:** 不引入新依赖，仅在 `frontend/index.html` 里通过 CSS class（`brand-title`/`brand-bar`）实现。颜色取自现有 CSS 变量 `--primary/--accent`，确保主题一致。

**Tech Stack:** Tailwind CDN, 原生 CSS。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: 标题渐变与品牌线

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 CSS class**

在 `<style>` 中添加：

```css
.brand-title {
  background: linear-gradient(90deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}
.brand-bar {
  height: 2px;
  width: 11.5rem;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(37,99,235,0.60), rgba(6,182,212,0.60));
}
html[data-theme="dark"] .brand-bar {
  background: linear-gradient(90deg, rgba(96,165,250,0.45), rgba(34,211,238,0.45));
}
```

- [ ] **Step 2: 替换标题样式**

把标题 `<h1>` 改为使用 `brand-title`（移除 inline `color: var(--primary)`），并在标题下方插入品牌线：

```html
<h1 class="text-3xl sm:text-4xl font-bold tracking-tight brand-title">中考知识库</h1>
<div class="brand-bar mt-2"></div>
```

- [ ] **Step 3: 回归**

人工检查：
- 浅色/深色标题都清晰
- 不影响布局（不会换行/抖动）

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "style: add brand header gradient"
git push origin main
```

