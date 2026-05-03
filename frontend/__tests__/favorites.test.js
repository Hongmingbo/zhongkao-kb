const { buildFavoritesView } = require('../favorites_view')

describe('favorites_view', () => {
  test('groups favorites by category and marks missing files', () => {
    const favs = new Set(['数学::a.pdf', '物理::b.pdf'])
    const stats = { 数学: [{ name: 'a.pdf' }], 物理: [] }
    const view = buildFavoritesView(favs, stats)
    expect(Array.isArray(view.groups)).toBe(true)
    expect(view.groups.length).toBe(2)
    const phy = view.groups.find(g => g.category === '物理')
    expect(phy.items[0].missing).toBe(true)
    const math = view.groups.find(g => g.category === '数学')
    expect(math.items[0].missing).toBe(false)
  })
})

