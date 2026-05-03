const {
  calcUploadProgress,
  retryOne,
  retryFailed,
  clearQueue,
} = require('../upload_queue')

describe('upload_queue', () => {
  test('calcUploadProgress counts done/success/fail', () => {
    const queue = [
      { id: '1', status: 'queued' },
      { id: '2', status: 'uploading' },
      { id: '3', status: 'success' },
      { id: '4', status: 'error' },
    ]
    expect(calcUploadProgress(queue)).toEqual({
      total: 4,
      done: 2,
      success: 1,
      fail: 1,
      queued: 1,
      uploading: 1,
    })
  })

  test('retryOne resets error item back to queued', () => {
    const queue = [
      { id: '1', status: 'success', message: 'x', category: 'a' },
      { id: '2', status: 'error', message: 'err', category: 'b' },
    ]
    const next = retryOne(queue, '2')
    expect(next[1]).toEqual({ id: '2', status: 'queued', message: '', category: '' })
    expect(next[0]).toEqual(queue[0])
  })

  test('retryFailed resets all error items to queued', () => {
    const queue = [
      { id: '1', status: 'error', message: 'e1', category: 'c1' },
      { id: '2', status: 'success', message: 'ok', category: 'c2' },
      { id: '3', status: 'error', message: 'e3', category: 'c3' },
    ]
    const next = retryFailed(queue)
    expect(next.map(x => x.status)).toEqual(['queued', 'success', 'queued'])
  })

  test('clearQueue removes queued and error by default', () => {
    const queue = [
      { id: '1', status: 'queued' },
      { id: '2', status: 'error' },
      { id: '3', status: 'uploading' },
      { id: '4', status: 'success' },
    ]
    const next = clearQueue(queue)
    expect(next.map(x => x.id)).toEqual(['3', '4'])
  })
})

