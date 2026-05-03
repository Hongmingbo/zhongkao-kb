# Mobile Preview Bottom Sheet (A) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在移动端将“桌面端右侧预览面板”替换为底部抽屉预览（两段高度：半屏/近全屏），并复用现有 `previewFile/renderPreviewTo` 逻辑，提升小屏阅读与操作体验。

**Architecture:** 不改 API。新增一个 `mobile-preview-sheet`（overlay + bottom sheet）。当 `!isDesktopPreview()` 时，`previewFile()` 不再打开旧的 previewModal，而是填充并打开 bottom sheet；提供“展开/收起/关闭”与 `Esc` 关闭。

**Tech Stack:** Tailwind CDN, 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Create: `frontend/__tests__/mobile-preview.test.js`

---

### Task 1: 新增 bottom sheet HTML + CSS

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 添加 HTML 容器**

在 body 底部（toast/confirm 附近）加入：
- overlay：`#mobile-preview-overlay`
- sheet：`#mobile-preview-sheet`
- header：标题 + badge + “展开/收起” + “关闭”
- body：`#mobile-preview-body`（滚动容器）

- [ ] **Step 2: 添加 CSS**

新增类：
- `.sheet-hidden`（display none）
- `.sheet`（固定底部，圆角，阴影）
- `.sheet-half`（高度约 55vh）
- `.sheet-full`（高度约 90vh）

并尊重 `prefers-reduced-motion`：展开收起用 `transform` 过渡，reduce 下关闭动画。

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "style: add mobile preview bottom sheet"
```

---

### Task 2: JS 行为：打开/关闭/展开收起

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Test: `frontend/__tests__/mobile-preview.test.js`

- [ ] **Step 1: 写 failing test（RED）**

测试：
- `openMobilePreviewSheet()` 会显示 overlay/sheet，并默认半屏模式
- 点击“展开”切换到 full，再次点击回 half
- `closeMobilePreviewSheet()` 会隐藏 overlay/sheet

- [ ] **Step 2: 实现最小逻辑（GREEN）**

新增函数：
- `openMobilePreviewSheet({ title, badgeText, badgeCls, html })`
- `toggleMobilePreviewSheetSize()`
- `closeMobilePreviewSheet()`

事件：
- overlay 点击关闭
- 关闭按钮关闭
- Esc 关闭（复用现有全局 shortcuts 的 Esc 逻辑：优先 confirm，其次 preview，再其次 sheet）

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html frontend/__tests__/mobile-preview.test.js
git commit -m "feat: add mobile preview sheet behavior"
```

---

### Task 3: 接入 previewFile（移动端走 sheet）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 调整 previewFile 的分支**

当 `!isDesktopPreview()`：
- 不再打开 `previewModal`
- 使用 `renderPreviewTo(tmpEl, ...)` 生成 HTML（或直接复用 `renderPreviewTo` 往 `#mobile-preview-body` 填充）
- 设置标题与 badge，然后打开 bottom sheet

- [ ] **Step 2: 复制链接/查看提取文本按钮在 sheet 内可点击**

确保 sheet body 的 click handler 支持：
- `data-action="copy-link"`
- `data-action="preview-derived"`

- [ ] **Step 3: 提交**

```bash
git add frontend/index.html
git commit -m "feat: use bottom sheet for mobile preview"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 全量测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 缩小窗口到手机宽度：预览打开为 bottom sheet
- 默认半屏，点击“展开”近全屏
- overlay/关闭按钮/Esc 关闭
- 复制链接与查看提取文本可用

- [ ] **Step 3: Push**

```bash
git push origin main
```

