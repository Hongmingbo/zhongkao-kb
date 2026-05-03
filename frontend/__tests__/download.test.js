describe('download helper', () => {
  test('downloadFile is exported for tests', () => {
    const { downloadFile } = require('../download_internals')
    expect(typeof downloadFile).toBe('function')
  })
})

