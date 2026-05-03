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

  function clearFailedUploads(queue) {
    const items = Array.isArray(queue) ? queue : []
    return items.filter(it => normStatus(it && it.status) !== 'error')
  }

  function makeHighlightKey(category, filename) {
    return String(category || '') + '::' + String(filename || '')
  }

  function mergeLastUploadSuccess(prev, item) {
    const arr = Array.isArray(prev) ? prev.slice() : []
    if (!item || normStatus(item.status) !== 'success') return arr
    const category = String(item.category || '').trim()
    const filename = String(item.name || '').trim()
    if (!category || !filename) return arr
    const k = makeHighlightKey(category, filename)
    if (arr.some(x => x && makeHighlightKey(x.category, x.filename) === k)) return arr
    arr.push({ category, filename })
    return arr
  }

  function snapshotUploadHistory(queue) {
    const items = Array.isArray(queue) ? queue : []
    return items.map(it => ({
      id: String((it && it.id) || ''),
      name: String((it && it.name) || ''),
      status: normStatus(it && it.status),
      category: String((it && it.category) || ''),
      message: String((it && it.message) || ''),
    }))
  }

  function shouldAutoClearFilters(filterActive) {
    return !!filterActive
  }

  global.calcUploadProgress = calcUploadProgress
  global.retryOneUpload = retryOne
  global.retryFailedUploads = retryFailed
  global.clearUploadQueue = clearQueue
  global.clearFailedUploads = clearFailedUploads
  global.makeHighlightKey = makeHighlightKey
  global.mergeLastUploadSuccess = mergeLastUploadSuccess
  global.snapshotUploadHistory = snapshotUploadHistory
  global.shouldAutoClearFilters = shouldAutoClearFilters

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      calcUploadProgress,
      retryOne,
      retryFailed,
      clearQueue,
    clearFailedUploads,
      makeHighlightKey,
      mergeLastUploadSuccess,
      snapshotUploadHistory,
      shouldAutoClearFilters,
    }
  }
})(typeof window !== 'undefined' ? window : globalThis)
