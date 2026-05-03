(function (global) {
  function safeString(v) {
    return String(v == null ? '' : v)
  }

  function shouldUseCache(opts) {
    const o = opts || {}
    const ts = Number(o.ts || 0)
    const ttlMs = Number(o.ttlMs || 0)
    const now = Number.isFinite(o.now) ? Number(o.now) : Date.now()
    if (!ts || !ttlMs) return false
    return (now - ts) <= ttlMs
  }

  function makeSearchCacheKey(opts) {
    const o = opts || {}
    const q = safeString(o.q).trim()
    const category = safeString(o.category).trim()
    const onlyFav = o.onlyFav ? '1' : '0'
    const limit = Number(o.limit || 0)
    const context = Number(o.context || 0)
    return [q, category, onlyFav, limit, context].join('||')
  }

  global.shouldUseCache = shouldUseCache
  global.makeSearchCacheKey = makeSearchCacheKey

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { shouldUseCache, makeSearchCacheKey }
  }
})(typeof window !== 'undefined' ? window : globalThis)

