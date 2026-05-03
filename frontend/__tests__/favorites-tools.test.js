const {
  exportFavoritesJson,
  parseFavoritesJson,
  mergeFavoriteItems,
  applyFavoritesFilters,
  applyPinnedCategoryOrder,
  togglePinnedCategory,
} = require('../favorites_tools')

describe('favorites_tools', () => {
  test('exportFavoritesJson exports versioned json', () => {
    const set = new Set(['数学::a.pdf'])
    const json = exportFavoritesJson(set, '2026-05-03T00:00:00Z')
    const data = JSON.parse(json)
    expect(data.version).toBe(1)
    expect(data.items.length).toBe(1)
    expect(data.items[0]).toEqual({ category: '数学', filename: 'a.pdf' })
  })

  test('parseFavoritesJson validates structure', () => {
    const r = parseFavoritesJson('{"version":1,"items":[{"category":"数学","filename":"a.pdf"}]}')
    expect(r.ok).toBe(true)
    expect(r.items[0]).toEqual({ category: '数学', filename: 'a.pdf' })
  })

  test('mergeFavoriteItems merges and dedupes', () => {
    const base = new Set(['数学::a.pdf'])
    const { merged, added } = mergeFavoriteItems(base, [
      { category: '数学', filename: 'a.pdf' },
      { category: '物理', filename: 'b.pdf' },
    ])
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
    expect(out[0].key).toBe('数学::a.pdf')
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
})

