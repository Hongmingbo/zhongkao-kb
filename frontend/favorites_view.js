(function (global) {
  function safeString(v) {
    return String(v == null ? '' : v)
  }

  function parseKey(key) {
    const raw = safeString(key)
    const idx = raw.indexOf('::')
    if (idx === -1) return { category: '', filename: raw }
    return { category: raw.slice(0, idx), filename: raw.slice(idx + 2) }
  }

  function buildStatsIndex(stats) {
    const index = new Map()
    const obj = stats && typeof stats === 'object' ? stats : {}
    for (const [category, files] of Object.entries(obj)) {
      const set = new Set()
      ;(Array.isArray(files) ? files : []).forEach(f => {
        const name = safeString(f && f.name)
        if (name) set.add(name)
      })
      index.set(String(category || ''), set)
    }
    return index
  }

  function buildFavoritesView(favs, stats) {
    const keys = []
    if (favs && typeof favs.forEach === 'function') {
      favs.forEach(k => keys.push(safeString(k)))
    }
    const idx = buildStatsIndex(stats)
    const groupsMap = new Map()
    keys.forEach(k => {
      const { category, filename } = parseKey(k)
      const set = idx.get(category) || new Set()
      const missing = !set.has(filename)
      const g = groupsMap.get(category) || []
      g.push({ key: category + '::' + filename, category, filename, missing })
      groupsMap.set(category, g)
    })
    const groups = Array.from(groupsMap.entries()).map(([category, items]) => ({
      category,
      items: items.slice().sort((a, b) => a.filename.localeCompare(b.filename, 'zh-Hans-CN')),
    })).sort((a, b) => a.category.localeCompare(b.category, 'zh-Hans-CN'))
    return { groups }
  }

  global.buildFavoritesView = buildFavoritesView

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { buildFavoritesView }
  }
})(typeof window !== 'undefined' ? window : globalThis)

