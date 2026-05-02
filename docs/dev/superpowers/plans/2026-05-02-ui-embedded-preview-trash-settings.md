# UI 内嵌预览面板 + 回收站与设置双栏 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将文件预览从弹窗升级为右侧内嵌预览面板（1A），并将“回收站与设置”页改为左右双栏内嵌（2B），整体信息架构更专业。

**Architecture:** 继续保持单文件前端（`frontend/index.html`），将“预览弹窗”的渲染逻辑提取为可复用的 `renderPreview()`，并增加一个右侧 `<aside>` 作为预览容器；列表点击即加载 `/api/file/{category}/{filename}` 并渲染 text/image/pdf/download。回收站从弹窗迁移为页面内列表（复用现有加载/批量选择/恢复/删除逻辑），设置面板迁移为页面内表单（复用现有 profile modal 内的 DOM/事件）。

**Tech Stack:** Tailwind CDN, 原生 JS, FastAPI（无需新增后端接口），pytest（回归）。

---

## 文件与模块改动清单

- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- (Optional) Modify: [tests/test_upload.py](file:///workspace/zhongkao-kb/tests/test_upload.py)（保持不变或加轻量 smoke）

---

## 交互规格

### 预览面板（替代弹窗）

1) 位置：知识库页与搜索页右侧固定预览区域（桌面端），移动端降级为“弹窗/全屏预览按钮”。
2) 内容类型：
   - `type=text`：显示 `<pre>`（保留换行），顶部提供“复制内容”按钮
   - `type=binary` + image：`<img>` 预览 + “下载/打开原文件”
   - `type=binary` + pdf：`<iframe>` 预览 + “查看提取文本（*.pdf.md）”按钮
   - `type=binary` + doc/docx：显示下载链接 + “查看提取文本（*.docx.md）”按钮
3) 行为：
   - 点击知识库文件列表的“预览”→ 右侧更新
   - 点击搜索结果“预览”→ 右侧更新
   - 右侧提供“清空预览”按钮

### 回收站与设置（双栏 2B）

1) 左栏：回收站列表（包含“恢复已选 / 删除已选 / 清空回收站 / 取消选择”）
2) 右栏：账号设置（头像上传、昵称、密码修改）直接内嵌显示，不再依赖设置弹窗
3) 保留右上角“设置”按钮：点击自动跳转 `#/trash` 并滚动到设置区域。

---

### Task 1: 搭建可复用预览渲染（不改行为，只拆函数）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 提取 `previewFile(category, filename)` 内的渲染为 `renderPreviewTo(el, base, category, filename, data)`**

目标：让弹窗与右侧面板可以复用同一套渲染 HTML（避免两套逻辑分叉）。

- [ ] **Step 2: 确保现有弹窗预览仍可用**

手工回归：
- 上传 png/pdf/docx
- 点击“预览”依然弹窗能展示（此时仅做重构，不换 UI）

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "refactor: extract preview renderer"
```

---

### Task 2: 知识库页增加右侧预览面板（桌面端双栏）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 在 `data-page=\"library\"` 内引入两栏布局**

结构示例：

```html
<div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
  <div class="lg:col-span-2">（筛选 + 文件列表 + 批量条）</div>
  <aside id="library-preview" class="hidden lg:block lg:col-span-1 ...">（预览）</aside>
</div>
```

- [ ] **Step 2: 列表点击“预览”时，改为渲染到 `#library-preview`**

保留弹窗作为移动端 fallback：
- `window.matchMedia('(min-width: 1024px)')` 为 true → 右侧渲染
- 否则 → 继续弹窗

- [ ] **Step 3: 右侧提供按钮**
- 复制文本（仅 text）
- 清空预览

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: embedded preview panel in library page"
```

---

### Task 3: 搜索页增加右侧预览面板（复用同一渲染）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 在 `data-page=\"search\"` 内做两栏布局（左结果/右预览）**

- [ ] **Step 2: 搜索结果“预览”按钮改为：桌面端右侧预览，移动端弹窗**

- [ ] **Step 3: Commit**

```bash
git add frontend/index.html
git commit -m "feat: embedded preview panel in search page"
```

---

### Task 4: 回收站内嵌到 `#/trash` 左栏（替换弹窗）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 在 `data-page=\"trash\"` 内加入双栏容器**

```html
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
  <section id="trash-panel">（回收站列表 + 批量操作）</section>
  <section id="settings-panel">（账号设置）</section>
</div>
```

- [ ] **Step 2: 把 `trash-modal` 的头部/按钮/列表 DOM 迁移到 `#trash-panel`**

策略：保留原 modal（先不删），但新增一套页面内元素，并让 `loadTrash()` 渲染到页面内的 `#trash-list`（或新增 `#trash-list-page`）。

- [ ] **Step 3: 回收站入口按钮逻辑调整**
- 顶部 Tabs 中 “回收站与设置” 即可进入
- 旧的 `trashBtn`/`trashBtn2` 点击：`location.hash = '#/trash'` + 自动加载回收站

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: embed trash panel in trash page"
```

---

### Task 5: 设置面板内嵌到 `#/trash` 右栏（替换设置弹窗的主要用途）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 将 profile modal 的表单 DOM 复制到 `#settings-panel`**
- 头像上传
- 昵称保存
- 密码修改

- [ ] **Step 2: 复用现有事件处理函数**

把按钮事件绑定目标从 modal 的按钮改为双写（modal 继续保留一段时间）：
- `saveNicknameBtn` 与 `saveNicknameBtnPage`
- `uploadAvatarBtn` 与 `uploadAvatarBtnPage`
- `changePasswordBtn` 与 `changePasswordBtnPage`

- [ ] **Step 3: “设置”按钮行为调整**
- 点击右上角设置：跳转 `#/trash` 并滚动到 `#settings-panel`

- [ ] **Step 4: Commit**

```bash
git add frontend/index.html
git commit -m "feat: embed settings panel in trash page"
```

---

### Task 6: 清理与回归（保持功能完整）

**Files:**
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 手工回归清单**
- 上传：png/pdf/docx/zip
- 知识库：筛选、批量移动/回收站/改标签/批量重命名
- 预览：text/png/pdf/docx（右侧与移动端弹窗）
- 回收站：恢复已选、删除已选、清空回收站
- 设置：头像/昵称/密码

- [ ] **Step 2: pytest**

```bash
pytest -q
```

- [ ] **Step 3: Commit + Push**

```bash
git add frontend/index.html
git commit -m "style: refine embedded panels and interactions"
git push origin main
```

