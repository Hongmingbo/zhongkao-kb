# Favorites Tab + Bulk Unfavorite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增独立 Tab「收藏」，展示收藏文件并支持预览/复制文件名/单个与批量取消收藏；对已不存在文件给出提示并允许移除收藏。

**Architecture:** 不改后端，仅复用现有 `favorites`（localStorage）、`loadStats`（获取全量文件映射）、`previewFile` 与 `copyWithToast`。新增 `favoritesTab` UI 与 `renderFavorites()`，并复用现有事件委托风格（data-action）。

**Tech Stack:** Tailwind CDN, 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)
- Create: `frontend/__tests__/favorites.test.js`

---

### Task 1: favorites 渲染纯函数（TDD）

**Files:**
- Create: `frontend/__tests__/favorites.test.js`
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 写 failing test（RED）**

为纯函数 `buildFavoritesView(favs, stats)` 写 jsdom-free 测试（返回结构数据，不返回 HTML）：

```js
const { buildFavoritesView } = require('../favorites_view')

test('groups favorites by category and marks missing files', () => {
  const favs = new Set(['数学::a.pdf', '物理::b.pdf'])
  const stats = { 数学: [{ name: 'a.pdf' }], 物理: [] }
  const view = buildFavoritesView(favs, stats)
  expect(view.groups.length).toBe(2)
  const phy = view.groups.find(g => g.category === '物理')
  expect(phy.items[0].missing).toBe(true)
})
```

该 test 预期失败（模块不存在）。

- [ ] **Step 2: 实现 buildFavoritesView（GREEN）**

新增 `frontend/favorites_view.js`：
- 输入：`favs:Set<string>`（`category::filename`）与 `stats`（来自 `/api/stats` 的对象）
- 输出：`{ groups: [{ category, items: [{ filename, missing }] }] }`

- [ ] **Step 3: 跑 jest 通过**

```bash
npm run test:js
```

- [ ] **Step 4: 提交**

```bash
git add frontend/favorites_view.js frontend/__tests__/favorites.test.js
git commit -m "feat: add favorites view builder"
```

---

### Task 2: 新增 Tab「收藏」与基本布局

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: Tab 导航新增“收藏”按钮**
- `data-tab="favorites"`，与现有 tab 一致

- [ ] **Step 2: 新增页面容器**

新增 section：
- `#favorites-page`
- 顶部工具栏：全选/取消全选、批量取消收藏按钮
- 列表容器：`#favorites-list`

- [ ] **Step 3: setActiveTab 支持 favorites**

切换到 favorites 时调用 `renderFavorites()`。

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "feat: add favorites tab skeleton"
```

---

### Task 3: renderFavorites：渲染 + 事件绑定 + 批量取消收藏

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 渲染**

流程：
- 读取 `favorites` set
- 调用 `loadStats()` 或复用其结果（若已有缓存则直接用）
- 使用 `buildFavoritesView` 生成分组数据
- 渲染为与知识库类似的“学科分组 + 文件行”
- 对 missing 项标记 chip“已不存在”，并禁用预览按钮

- [ ] **Step 2: 单项操作（data-action）**
- `preview`（非 missing 才允许）
- `copy-name`
- `unfavorite`（取消收藏）
- `remove-missing`（仅 missing 可见）

- [ ] **Step 3: 批量**
- checkbox：`data-fav-select="1"` + `data-key="category::filename"`
- 全选/取消全选（仅选中非 missing 或全部？默认：全部都可选）
- 批量取消收藏：对选中 key 执行 `favorites.delete(key)` 并保存

- [ ] **Step 4: 同步其他页面星标**

取消收藏后：
- 若当前 tab 是 library/search：刷新对应列表（或更新局部 DOM 星标）
- 若在 favorites：重新 renderFavorites

- [ ] **Step 5: 提交**

```bash
git add frontend/index.html
git commit -m "feat: render favorites and support bulk unfavorite"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 收藏 Tab 能进入，列表分组正确
- 单个取消收藏即时更新
- 批量取消收藏有效
- missing 文件有提示，预览不可点，可移除收藏

- [ ] **Step 3: Push**

```bash
git push origin main
```

