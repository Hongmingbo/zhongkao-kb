(function (global) {
  async function hydrateRawPreview(opts) {
    const o = opts || {}
    const container = o.container
    const rawPath = String(o.rawPath || '')
    const apiFetch = o.apiFetch || global.apiFetch
    const toastError = o.toastError || global.toastError
    if (!container || !rawPath || typeof apiFetch !== 'function') return false

    try {
      const prev = container.dataset ? (container.dataset.rawObjUrl || '') : ''
      if (prev) {
        try { URL.revokeObjectURL(prev) } catch (e) {}
        try { delete container.dataset.rawObjUrl } catch (e) {}
      }

      const node = container.querySelector ? container.querySelector('[data-preview-raw="1"]') : null
      if (!node) return false

      const r = await apiFetch(rawPath)
      if (!r || !r.ok) {
        if (toastError) toastError('预览失败', String(r && r.status ? r.status : ''))
        return false
      }
      const blob = await r.blob()
      const url = URL.createObjectURL(blob)
      if (container.dataset) container.dataset.rawObjUrl = url
      if (container.querySelectorAll) container.querySelectorAll('[data-preview-loading="1"]').forEach(n => n.remove())
      try {
        if (node && node.tagName && node.tagName.toUpperCase() === 'IFRAME') node.setAttribute('src', url)
        else node.src = url
      } catch (e) {}
      return true
    } catch (e) {
      if (toastError) toastError('预览失败', e && e.message ? e.message : '')
      return false
    }
  }

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
    module.exports = { downloadFile, hydrateRawPreview }
  }
  global._downloadInternals = { downloadFile, hydrateRawPreview }
})(typeof window !== 'undefined' ? window : globalThis)
