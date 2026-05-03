(function (global) {
  function normStatus(s) {
    const v = String(s || '')
    if (v === 'queued' || v === 'uploading' || v === 'success' || v === 'error') return v
    return 'queued'
  }

  function calcUploadProgress(queue) {
    const items = Array.isArray(queue) ? queue : []
    let queued = 0
    let uploading = 0
    let success = 0
    let fail = 0
    for (const it of items) {
      const st = normStatus(it && it.status)
      if (st === 'queued') queued += 1
      else if (st === 'uploading') uploading += 1
      else if (st === 'success') success += 1
      else if (st === 'error') fail += 1
    }
    const total = items.length
    const done = success + fail
    return { total, done, success, fail, queued, uploading }
  }

  function retryOne(queue, id) {
    const items = Array.isArray(queue) ? queue : []
    return items.map(it => {
      if (!it || String(it.id || '') !== String(id || '')) return it
      const st = normStatus(it.status)
      if (st !== 'error') return it
      return { ...it, status: 'queued', message: '', category: '' }
    })
  }

  function retryFailed(queue) {
    const items = Array.isArray(queue) ? queue : []
    return items.map(it => {
      if (!it) return it
      const st = normStatus(it.status)
      if (st !== 'error') return it
      return { ...it, status: 'queued', message: '', category: '' }
    })
  }

  function clearQueue(queue) {
    const items = Array.isArray(queue) ? queue : []
    return items.filter(it => {
      const st = normStatus(it && it.status)
      return st !== 'queued' && st !== 'error'
    })
  }

  global.calcUploadProgress = calcUploadProgress
  global.retryOneUpload = retryOne
  global.retryFailedUploads = retryFailed
  global.clearUploadQueue = clearQueue

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { calcUploadProgress, retryOne, retryFailed, clearQueue }
  }
})(typeof window !== 'undefined' ? window : globalThis)

