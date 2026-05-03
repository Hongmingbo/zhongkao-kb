const { precheckFiles } = require('../upload_precheck')

function fileLike(name, size, type) {
  return { name, size, type }
}

describe('upload_precheck', () => {
  test('rejects empty file', () => {
    const r = precheckFiles([fileLike('a.txt', 0, 'text/plain')], { maxFileMb: 50 })
    expect(r.accepted.length).toBe(0)
    expect(r.rejected.length).toBe(1)
    expect(r.rejected[0].reason).toBe('empty')
  })

  test('rejects oversize', () => {
    const r = precheckFiles([fileLike('a.pdf', 51 * 1024 * 1024, 'application/pdf')], { maxFileMb: 50 })
    expect(r.rejected[0].reason).toBe('too_large')
  })

  test('rejects unsupported ext', () => {
    const r = precheckFiles([fileLike('a.exe', 10, 'application/octet-stream')], { maxFileMb: 50 })
    expect(r.rejected[0].reason).toBe('unsupported')
  })

  test('dedupes duplicate names in same batch', () => {
    const r = precheckFiles([fileLike('a.txt', 10, 'text/plain'), fileLike('a.txt', 12, 'text/plain')], { maxFileMb: 50 })
    expect(r.accepted.length).toBe(1)
    expect(r.rejected.length).toBe(1)
    expect(r.rejected[0].reason).toBe('duplicate_name')
  })

  test('summary counts by reason', () => {
    const r = precheckFiles([fileLike('a.txt', 0, 'text/plain'), fileLike('b.exe', 10, '')], { maxFileMb: 50 })
    expect(r.summary.empty).toBe(1)
    expect(r.summary.unsupported).toBe(1)
  })

  test('rejects duplicates against existing queue names', () => {
    const existingNames = new Set(['a.txt'])
    const r = precheckFiles([fileLike('a.txt', 10, 'text/plain'), fileLike('b.txt', 10, 'text/plain')], { maxFileMb: 50, existingNames })
    expect(r.accepted.map(x => x.name)).toEqual(['b.txt'])
    expect(r.rejected.map(x => x.reason)).toEqual(['duplicate_name'])
  })
})
