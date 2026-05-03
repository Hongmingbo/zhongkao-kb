const { shouldUseCache, makeSearchCacheKey } = require('../cache_tools')

describe('cache_tools', () => {
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
})

