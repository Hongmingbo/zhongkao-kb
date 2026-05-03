# Visual Polish: Sizing + States Unification Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不改变现有配色的前提下，统一全站按钮/Chip/列表行的尺寸、对齐与交互状态（hover/active/disabled），减少页面间不一致与跳动。

**Architecture:** 仅改前端静态页（[frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)）的 CSS tokens 与少量结构 class；不改业务逻辑，不改 API；以“新增统一类 + 渐进替换”为主，保留旧类以避免回归风险。

**Tech Stack:** Tailwind CDN, 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- (Optional) Create: `frontend/__tests__/visual-polish.test.js`（仅做存在性断言，不做视觉快照）

---

### Task 1: 定义统一尺寸类（btn/chip/row）与 disabled 状态

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 新增 CSS tokens（不动颜色）**

在 `<style>` 中新增（示例）：
- `.btn-sm` / `.btn-md`（font-size/line-height/padding）
- `.chip-sm`（更紧凑）
- `.row-item`（列表行 padding/gap/align）
- `.btn[disabled], .btn.is-disabled` 的统一禁用态（opacity + pointer-events）

- [ ] **Step 2: 提交**

```bash
git add frontend/index.html
git commit -m "style: add sizing tokens for buttons and chips"
```

---

### Task 2: 批量替换关键区域按钮尺寸（上传/知识库/搜索/回收站/预览）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 上传队列**
- “重试/清空/折叠/上次记录”等统一为 `btn btn-soft btn-sm`
- 主按钮仍保持 `btn-primary`，但补齐 `btn-sm` 或 `btn-md`

- [ ] **Step 2: 知识库列表 & 搜索结果**
- hover 操作区所有 action 统一 `btn-sm`（保持链接色不变：仅加 padding/line-height）
- 避免 hover 时宽度跳动：对操作区容器固定高度/对齐

- [ ] **Step 3: 回收站**
- 恢复/复制/彻底删除按钮统一 `btn-sm`

- [ ] **Step 4: 预览区**
- “复制链接/查看提取文本”等统一 `btn-sm`

- [ ] **Step 5: 提交**

```bash
git add frontend/index.html
git commit -m "style: unify button sizing across lists and preview"
```

---

### Task 3: 列表行对齐与信息密度（不改结构）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: row-item 应用**
- 知识库/搜索/回收站/上传队列的行容器加 `row-item`
- 统一 `items-center`、`gap`、`border` 表现

- [ ] **Step 2: chip-sm 应用（移动端优先）**
- 对移动端抽屉 header、紧凑区域使用 chip-sm

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: unify row alignment and density"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归检查点**
- 上传队列按钮尺寸一致、折叠/历史区不抖动
- 知识库/搜索 hover 操作区对齐一致、无“跳动”
- 移动端抽屉 header 按钮/Chip 紧凑但可点击

- [ ] **Step 3: Push**

```bash
git push origin main
```

