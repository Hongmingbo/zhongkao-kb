(function (global) {
  function getDoc(ctx) {
    return (ctx && ctx.document) || global.document
  }

  function getNav(ctx) {
    return (ctx && ctx.navigator) || global.navigator
  }

  async function copyText(text, ctx) {
    const doc = getDoc(ctx)
    const nav = getNav(ctx)
    const value = String(text == null ? '' : text)
    if (!value) return false

    try {
      if (nav && nav.clipboard && typeof nav.clipboard.writeText === 'function') {
        await nav.clipboard.writeText(value)
        return true
      }
    } catch (e) {}

    try {
      if (!doc || !doc.body) return false
      const ta = doc.createElement('textarea')
      ta.value = value
      ta.setAttribute('readonly', 'true')
      ta.style.position = 'fixed'
      ta.style.opacity = '0'
      ta.style.pointerEvents = 'none'
      doc.body.appendChild(ta)
      ta.select()
      const ok = !!doc.execCommand && doc.execCommand('copy')
      doc.body.removeChild(ta)
      return ok
    } catch (e) {
      return false
    }
  }

  function isEditableTarget(target) {
    if (!target) return false
    const el = target
    if (el.isContentEditable) return true
    const tag = String(el.tagName || '').toLowerCase()
    return tag === 'input' || tag === 'textarea' || tag === 'select'
  }

  function installGlobalShortcuts(opts) {
    const setActiveTab = opts && opts.setActiveTab
    const searchQueryInput = opts && opts.searchQueryInput
    const previewModal = opts && opts.previewModal
    const confirmModal = opts && opts.confirmModal

    const onKeyDown = (e) => {
      if (!e) return
      if (e.key === 'Escape') {
        if (confirmModal && !confirmModal.classList.contains('hidden')) {
          const cancel = global.document && global.document.getElementById('confirm-cancel')
          if (cancel && typeof cancel.click === 'function') cancel.click()
          else confirmModal.classList.add('hidden')
          return
        }
        if (previewModal && !previewModal.classList.contains('hidden')) {
          previewModal.classList.add('hidden')
          return
        }
        return
      }

      const target = e.target
      const isEditable = isEditableTarget(target)
      const isSlash = e.key === '/'
      const isK = (e.key === 'k' || e.key === 'K') && (e.ctrlKey || e.metaKey)
      if ((isSlash && !isEditable) || isK) {
        e.preventDefault()
        if (typeof setActiveTab === 'function') setActiveTab('search')
        try { if (searchQueryInput) searchQueryInput.focus() } catch (err) {}
      }
    }

    global.document.addEventListener('keydown', onKeyDown)
    return () => global.document.removeEventListener('keydown', onKeyDown)
  }

  global.copyText = copyText
  global.installGlobalShortcuts = installGlobalShortcuts

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { copyText, installGlobalShortcuts }
  }
})(typeof window !== 'undefined' ? window : globalThis)

