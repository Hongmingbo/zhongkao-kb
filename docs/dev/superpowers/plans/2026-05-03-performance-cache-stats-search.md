# Performance: Cache Stats + Search Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 `/api/stats` 与 `/api/search` 增加前端缓存与 TTL 失效机制，减少重复请求与切换卡顿；并在关键数据变更操作后主动失效缓存。

**Architecture:** 新增 `frontend/cache_tools.js`（纯函数：TTL 缓存与 key 构造），在 `frontend/index.html` 中新增 `statsCache/searchCache` 运行时状态与失效点；`fetchStatsData()` 与 `runSearch()` 接入缓存读取逻辑。

**Tech Stack:** 原生 JS, Jest(jsdom), pytest。

---

## 文件改动清单
- Create: `frontend/cache_tools.js`
- Create: `frontend/__tests__/cache-tools.test.js`
- Modify: [frontend/index.html](file:///workspace/zhongkao-kb/frontend/index.html)

---

### Task 1: cache_tools（TTL 缓存纯函数）TDD

**Files:**
- Create: `frontend/cache_tools.js`
- Create: `frontend/__tests__/cache-tools.test.js`

- [ ] **Step 1: 写 failing test（RED）**

```js
const { shouldUseCache, makeSearchCacheKey } = require('../cache_tools')

test('shouldUseCache respects ttl', () => {
  const now = 1000
  expect(shouldUseCache({ ts: 500, ttlMs: 400, now })).toBe(false)
  expect(shouldUseCache({ ts: 500, ttlMs: 600, now })).toBe(true)
})

test('makeSearchCacheKey is stable', () => {
  const k1 = makeSearchCacheKey({ q: 'a', category: '语文', onlyFav: true, limit: 20, context: 60 })
  const k2 = makeSearchCacheKey({ q: 'a', category: '语文', onlyFav: true, limit: 20, context: 60 })
  expect(k1).toBe(k2)
})
```

- [ ] **Step 2: 跑 jest 确认失败**

```bash
npm run test:js
```

- [ ] **Step 3: 实现最小 cache_tools.js（GREEN）**
- `shouldUseCache({ts, ttlMs, now})`
- `makeSearchCacheKey({q, category, onlyFav, limit, context})`

- [ ] **Step 4: 跑 jest 确认通过**

```bash
npm run test:js
```

- [ ] **Step 5: 提交**

```bash
git add frontend/cache_tools.js frontend/__tests__/cache-tools.test.js
git commit -m "feat: add cache tools for ttl and search key"
```

---

### Task 2: stats 缓存接入（TTL 30s + 失效点）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 新增缓存状态**
- `statsCache = { data, ts }`
- TTL：`STATS_TTL_MS = 30000`

- [ ] **Step 2: fetchStatsData 使用缓存**
- 命中缓存：直接返回缓存 data
- 未命中：请求 `/api/stats` 并写入缓存
- 增加 `invalidateStatsCache()` 工具函数

- [ ] **Step 3: 在数据变更操作后失效**
- 上传完成、删除/恢复、清空、批量移动/标签/重命名等路径：调用 `invalidateStatsCache()`

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "perf: cache stats with ttl and invalidation"
```

---

### Task 3: search 缓存接入（TTL 60s + 失效）

**Files:**
- Modify: [index.html](file:///workspace/zhongkao-kb/frontend/index.html)

- [ ] **Step 1: 新增 searchCache Map**
- 结构：`Map<key, { data, ts }>`
- TTL：`SEARCH_TTL_MS = 60000`

- [ ] **Step 2: runSearch 命中缓存直接 render**
- 缓存 key 使用 `makeSearchCacheKey`
- 未命中再调用 `/api/search`

- [ ] **Step 3: 失效策略**
- 收藏变化（toggle/bulk/unfavorite/import）触发 `searchCache.clear()`
- 若当前在 search tab：执行一次 `runSearch()`

- [ ] **Step 4: 提交**

```bash
git add frontend/index.html
git commit -m "perf: cache search results with ttl"
```

---

### Task 4: 回归与推送

- [ ] **Step 1: 自动化测试**

```bash
npm run test:js
pytest -q
```

- [ ] **Step 2: 手工回归**
- 多次切换“知识库/收藏”不会重复触发 stats 请求（可用浏览器 Network 验证）
- 相同搜索条件短时间内重复搜索命中缓存
- 收藏变更后“只看收藏”的搜索结果能刷新

- [ ] **Step 3: Push**

```bash
git push origin main
```

