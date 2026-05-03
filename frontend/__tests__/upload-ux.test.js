const { clearFailedUploads } = require('../upload_queue')

describe('upload ux helpers', () => {
  test('clearFailedUploads removes only error items', () => {
    const q = [
      { id: '1', status: 'queued' },
      { id: '2', status: 'error' },
      { id: '3', status: 'success' },
      { id: '4', status: 'uploading' },
    ]
    const out = clearFailedUploads(q)
    expect(out.map(x => x.id)).toEqual(['1', '3', '4'])
  })
})

