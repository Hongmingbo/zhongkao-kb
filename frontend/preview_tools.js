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
      try { node.src = url } catch (e) {}
      return true
    } catch (e) {
      if (toastError) toastError('预览失败', e && e.message ? e.message : '')
      return false
    }
  }

  global.hydrateRawPreview = hydrateRawPreview

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { hydrateRawPreview }
  }
})(typeof window !== 'undefined' ? window : globalThis)

