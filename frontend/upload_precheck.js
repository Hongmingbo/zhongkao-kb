(function (global) {
  const DEFAULT_ALLOWED_EXTS = new Set(['txt', 'md', 'pdf', 'docx', 'jpg', 'jpeg', 'png', 'webp', 'zip'])

  function safeString(v) {
    return String(v == null ? '' : v)
  }

  function getExt(name) {
    const n = safeString(name).trim()
    const idx = n.lastIndexOf('.')
    if (idx === -1) return ''
    return n.slice(idx + 1).toLowerCase()
  }

  function inc(summary, k) {
    summary[k] = (summary[k] || 0) + 1
  }

  function precheckFiles(files, opts) {
    const list = Array.isArray(files) ? files : []
    const o = opts || {}
    const maxFileMb = Number(o.maxFileMb || 50)
    const maxBytes = maxFileMb > 0 ? maxFileMb * 1024 * 1024 : 0
    const allowedExts = o.allowedExts instanceof Set ? o.allowedExts : DEFAULT_ALLOWED_EXTS

    const accepted = []
    const rejected = []
    const summary = { empty: 0, too_large: 0, unsupported: 0, duplicate_name: 0 }
    const seen = new Set()
    const existingNames = o.existingNames instanceof Set ? o.existingNames : null
    if (existingNames) {
      existingNames.forEach(n => {
        const k = safeString(n).trim().toLowerCase()
        if (k) seen.add(k)
      })
    }

    list.forEach(f => {
      const name = safeString(f && f.name).trim()
      const size = Number(f && f.size || 0)
      if (!name) return
      const key = name.toLowerCase()
      if (seen.has(key)) {
        rejected.push({ name, size, reason: 'duplicate_name' })
        inc(summary, 'duplicate_name')
        return
      }
      seen.add(key)
      if (!size) {
        rejected.push({ name, size, reason: 'empty' })
        inc(summary, 'empty')
        return
      }
      if (maxBytes && size > maxBytes) {
        rejected.push({ name, size, reason: 'too_large' })
        inc(summary, 'too_large')
        return
      }
      const ext = getExt(name)
      if (!allowedExts.has(ext)) {
        rejected.push({ name, size, reason: 'unsupported' })
        inc(summary, 'unsupported')
        return
      }
      accepted.push(f)
    })

    return { accepted, rejected, summary }
  }

  global.precheckFiles = precheckFiles

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { precheckFiles }
  }
})(typeof window !== 'undefined' ? window : globalThis)
