const {
  mergeLastUploadSuccess,
  snapshotUploadHistory,
  makeHighlightKey,
  shouldAutoClearFilters,
} = require('../upload_queue')

describe('upload polish helpers', () => {
  test('mergeLastUploadSuccess records only success items and de-duplicates', () => {
    const prev = [{ category: '数学', filename: 'a.pdf' }]
    const next1 = mergeLastUploadSuccess(prev, { status: 'error', category: '数学', name: 'b.pdf' })
    expect(next1).toEqual(prev)

    const next2 = mergeLastUploadSuccess(prev, { status: 'success', category: '数学', name: 'a.pdf' })
    expect(next2).toEqual(prev)

    const next3 = mergeLastUploadSuccess(prev, { status: 'success', category: '物理', name: 'c.pdf' })
    expect(next3).toEqual([{ category: '数学', filename: 'a.pdf' }, { category: '物理', filename: 'c.pdf' }])
  })

  test('snapshotUploadHistory strips File and keeps minimal fields', () => {
    const queue = [
      { id: '1', file: { any: true }, name: 'a.pdf', status: 'success', category: '数学', message: '' },
      { id: '2', file: { any: true }, name: 'b.pdf', status: 'error', category: '', message: 'bad' },
    ]
    expect(snapshotUploadHistory(queue)).toEqual([
      { id: '1', name: 'a.pdf', status: 'success', category: '数学', message: '' },
      { id: '2', name: 'b.pdf', status: 'error', category: '', message: 'bad' },
    ])
  })

  test('makeHighlightKey is stable', () => {
    expect(makeHighlightKey('数学', 'a.pdf')).toBe('数学::a.pdf')
    expect(makeHighlightKey('', 'a.pdf')).toBe('::a.pdf')
  })

  test('shouldAutoClearFilters follows filterActive', () => {
    expect(shouldAutoClearFilters(true)).toBe(true)
    expect(shouldAutoClearFilters(false)).toBe(false)
  })
})

