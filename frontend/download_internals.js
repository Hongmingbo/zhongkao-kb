(function (global) {
  async function downloadFile(opts) {
    const o = opts || {}
    const category = String(o.category || '')
    const filename = String(o.filename || '')
    if (!category || !filename) return false

    const apiFetch = o.apiFetch || global.apiFetch
    const toastSuccess = o.toastSuccess || global.toastSuccess
    const toastError = o.toastError || global.toastError
    const withDisabled = o.withDisabled || global.withDisabled
    const btn = o.btn

    if (typeof apiFetch !== 'function') throw new Error('apiFetch not available')

    const task = async () => {
      try {
        const url = '/api/file/raw/' + encodeURIComponent(category) + '/' + encodeURIComponent(filename)
        const r = await apiFetch(url)
        if (!r || !r.ok) {
          let msg = ''
          try {
            const data = await r.json()
            msg = (data && (data.detail || data.message)) ? String(data.detail || data.message) : ''
          } catch (e) {}
          if (toastError) toastError('下载失败', msg || String(r && r.status ? r.status : ''))
          return false
        }
        const blob = await r.blob()
        const href = URL.createObjectURL(blob)
        const a = (global.document || {}).createElement ? global.document.createElement('a') : null
        if (!a) return false
        a.href = href
        a.download = filename
        ;(global.document.body || global.document.documentElement).appendChild(a)
        a.click()
        a.remove()
        setTimeout(() => URL.revokeObjectURL(href), 500)
        if (toastSuccess) toastSuccess('开始下载', filename)
        return true
      } catch (e) {
        if (toastError) toastError('下载失败', e && e.message ? e.message : '')
        return false
      }
    }

    if (typeof withDisabled === 'function' && btn) {
      return await withDisabled(btn, task)
    }
    return await task()
  }

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { downloadFile }
  }
  global._downloadInternals = { downloadFile }
})(typeof window !== 'undefined' ? window : globalThis)

