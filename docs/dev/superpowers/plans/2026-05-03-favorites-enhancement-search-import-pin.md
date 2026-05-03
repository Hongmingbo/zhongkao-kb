# Favorites Enhancements: Search + JSON Import/Export + Pin Categories Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 收藏页支持搜索/过滤；支持 JSON 导入/导出（合并去重）；支持学科置顶（本地存储）。

**Architecture:** 纯前端实现，不改后端接口。新增 `favorites_tools.js`（纯函数：过滤、导入/导出、置顶排序），并在收藏页新增工具栏（搜索框/学科筛选/仅存在/导入导出/置顶）。导入时通过现有 `/api/favorites/toggle` 逐项补齐缺失收藏。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Create: [frontend/favorites_tools.js](file:///workspace/zhongkao-kb/frontend/favorites_tools.js)
- Create: `frontend/__tests__/favorites-tools.test.js`
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: favorites_tools（过滤 + 导入导出 + 置顶排序）TDD

**Files:**
- Create: [favorites_tools.js](file:///workspace/zhongkao-kb/frontend/favorites_tools.js)
- Create: `frontend/__tests__/favorites-tools.test.js`

- [ ] **Step 1: 写 failing tests（RED）**

```js
const {
  exportFavoritesJson,
  parseFavoritesJson,
  mergeFavoriteItems,
  applyFavoritesFilters,
  applyPinnedCategoryOrder,
  togglePinnedCategory,
} = require('../favorites_tools')

test('exportFavoritesJson exports versioned json', () => {
  const set = new Set(['数学::a.pdf'])
  const json = exportFavoritesJson(set, '2026-05-03T00:00:00Z')
  const data = JSON.parse(json)
  expect(data.version).toBe(1)
  expect(data.items.length).toBe(1)
})

test('parseFavoritesJson validates structure', () => {
  const r = parseFavoritesJson('{"version":1,"items":[{"category":"数学","filename":"a.pdf"}]}')
  expect(r.ok).toBe(true)
  expect(r.items[0]).toEqual({ category: '数学', filename: 'a.pdf' })
})

test('mergeFavoriteItems merges and dedupes', () => {
  const base = new Set(['数学::a.pdf'])
  const { merged, added } = mergeFavoriteItems(base, [{ category: '数学', filename: 'a.pdf' }, { category: '物理', filename: 'b.pdf' }])
  expect(added).toBe(1)
  expect(merged.has('物理::b.pdf')).toBe(true)
})

test('applyFavoritesFilters filters by query and category', () => {
  const items = [
    { key: '数学::a.pdf', category: '数学', filename: 'a.pdf', missing: false },
    { key: '物理::b.pdf', category: '物理', filename: 'b.pdf', missing: true },
  ]
  const out = applyFavoritesFilters(items, { query: 'a', category: '数学', hideMissing: false })
  expect(out.length).toBe(1)
})

test('applyPinnedCategoryOrder puts pinned categories first', () => {
  const groups = [{ category: '物理' }, { category: '数学' }]
  const out = applyPinnedCategoryOrder(groups, ['数学'])
  expect(out[0].category).toBe('数学')
})

test('togglePinnedCategory toggles membership', () => {
  expect(togglePinnedCategory(['数学'], '数学')).toEqual([])
  expect(togglePinnedCategory([], '数学')).toEqual(['数学'])
})
```

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现最小 favorites_tools.js（GREEN）**
- JSON 格式：`{version:1, exported_at, items:[{category, filename}]}`
- parse：支持字符串输入，验证 version=1、items 为数组、元素字段合法
- merge：合并去重（以 `category::filename` 为 key）
- filters：按 query（filename 包含）+ category（完全匹配）+ hideMissing
- pinned：固定排序（pinned 顺序优先，未置顶按中文排序）

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/favorites_tools.js frontend/__tests__/favorites-tools.test.js
git commit -m "feat: add favorites tools for import export filter and pin"
```

---

### Task 2: 收藏页 UI 增强（搜索/筛选/仅存在/导入导出/置顶）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 收藏页工具栏新增控件**
- 搜索框 `#favoritesQuery`
- 学科下拉 `#favoritesCategory`
- checkbox `#favoritesHideMissing`
- 导出按钮 `#favoritesExportBtn`
- 导入按钮 `#favoritesImportBtn` + 隐藏 file input `#favoritesImportFile`

- [ ] **Step 2: 学科置顶**
- 每个学科标题右侧：`置顶/取消置顶`（data-action="pin-category"）
- 本地存储 key：`ZKKB_FAVORITES_PINNED_CATEGORIES`（JSON 数组）

- [ ] **Step 3: renderFavorites 接入 filters 与 pinned order**
- 渲染前：用 `applyFavoritesFilters` 与 `applyPinnedCategoryOrder`
- `favoritesLastViewKeys` 应基于过滤后结果

- [ ] **Step 4: 导出**
- `await loadFavorites()` 后 `exportFavoritesJson(favorites)` 下载

- [ ] **Step 5: 导入（合并）**
- 读取 file → `parseFavoritesJson`
- 与现有 favorites 合并，找出需新增项
- 对新增项逐个调用 `toggleFavorite(category, filename)`（仅当当前未收藏）
- 完成后 toast：导入条数/新增条数

- [ ] **Step 6: 提交**

```bash
git add frontend/index.html
git commit -m "feat: enhance favorites tab with search import export and pin"
```

---

### Task 3: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 搜索/筛选立即生效
- 导出 json 可用；导入合并去重有效
- 置顶学科排序有效且刷新后仍生效

- [ ] **Step 3: Push**

```bash
git push origin main
```

