(function (global) {
  function safeString(v) {
    return String(v == null ? '' : v)
  }

  function keyOf(category, filename) {
    return safeString(category) + '::' + safeString(filename)
  }

  function exportFavoritesJson(favs, exportedAt) {
    const items = []
    if (favs && typeof favs.forEach === 'function') {
      favs.forEach(k => {
        const raw = safeString(k)
        const idx = raw.indexOf('::')
        if (idx === -1) return
        const category = raw.slice(0, idx).trim()
        const filename = raw.slice(idx + 2).trim()
        if (!category || !filename) return
        items.push({ category, filename })
      })
    }
    items.sort((a, b) => (a.category + '::' + a.filename).localeCompare(b.category + '::' + b.filename, 'zh-Hans-CN'))
    const payload = {
      version: 1,
      exported_at: exportedAt ? safeString(exportedAt) : new Date().toISOString(),
      items,
    }
    return JSON.stringify(payload, null, 2)
  }

  function parseFavoritesJson(raw) {
    let data
    try { data = JSON.parse(safeString(raw)) } catch (e) { return { ok: false, reason: 'JSON 解析失败', items: [] } }
    if (!data || typeof data !== 'object') return { ok: false, reason: 'JSON 格式不合法', items: [] }
    if (Number(data.version) !== 1) return { ok: false, reason: '不支持的版本', items: [] }
    if (!Array.isArray(data.items)) return { ok: false, reason: 'items 必须是数组', items: [] }
    const items = []
    data.items.forEach(it => {
      const category = safeString(it && it.category).trim()
      const filename = safeString(it && it.filename).trim()
      if (!category || !filename) return
      if (category.includes('::') || filename.includes('::')) return
      items.push({ category, filename })
    })
    if (!items.length) return { ok: false, reason: '未找到有效收藏项', items: [] }
    return { ok: true, items }
  }

  function mergeFavoriteItems(baseSet, importedItems) {
    const merged = new Set()
    if (baseSet && typeof baseSet.forEach === 'function') {
      baseSet.forEach(k => merged.add(safeString(k)))
    }
    let added = 0
    ;(Array.isArray(importedItems) ? importedItems : []).forEach(it => {
      const category = safeString(it && it.category).trim()
      const filename = safeString(it && it.filename).trim()
      if (!category || !filename) return
      const k = keyOf(category, filename)
      if (merged.has(k)) return
      merged.add(k)
      added += 1
    })
    return { merged, added }
  }

  function applyFavoritesFilters(items, opts) {
    const list = Array.isArray(items) ? items : []
    const query = safeString(opts && opts.query).trim().toLowerCase()
    const category = safeString(opts && opts.category).trim()
    const hideMissing = !!(opts && opts.hideMissing)
    return list.filter(it => {
      if (!it) return false
      if (category && safeString(it.category) !== category) return false
      if (hideMissing && !!it.missing) return false
      if (query) {
        const name = safeString(it.filename).toLowerCase()
        if (!name.includes(query)) return false
      }
      return true
    })
  }

  function applyPinnedCategoryOrder(groups, pinnedCategories) {
    const list = Array.isArray(groups) ? groups.slice() : []
    const pinned = Array.isArray(pinnedCategories) ? pinnedCategories.map(x => safeString(x)) : []
    const pinnedIndex = new Map()
    pinned.forEach((c, i) => pinnedIndex.set(c, i))
    list.sort((a, b) => {
      const ca = safeString(a && a.category)
      const cb = safeString(b && b.category)
      const ia = pinnedIndex.has(ca) ? pinnedIndex.get(ca) : null
      const ib = pinnedIndex.has(cb) ? pinnedIndex.get(cb) : null
      if (ia != null && ib != null) return ia - ib
      if (ia != null) return -1
      if (ib != null) return 1
      return ca.localeCompare(cb, 'zh-Hans-CN')
    })
    return list
  }

  function togglePinnedCategory(pinnedCategories, category) {
    const list = Array.isArray(pinnedCategories) ? pinnedCategories.map(x => safeString(x)) : []
    const c = safeString(category)
    if (!c) return list
    const idx = list.indexOf(c)
    if (idx !== -1) {
      return list.filter(x => x !== c)
    }
    return list.concat([c])
  }

  global.exportFavoritesJson = exportFavoritesJson
  global.parseFavoritesJson = parseFavoritesJson
  global.mergeFavoriteItems = mergeFavoriteItems
  global.applyFavoritesFilters = applyFavoritesFilters
  global.applyPinnedCategoryOrder = applyPinnedCategoryOrder
  global.togglePinnedCategory = togglePinnedCategory

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      exportFavoritesJson,
      parseFavoritesJson,
      mergeFavoriteItems,
      applyFavoritesFilters,
      applyPinnedCategoryOrder,
      togglePinnedCategory,
    }
  }
})(typeof window !== 'undefined' ? window : globalThis)

