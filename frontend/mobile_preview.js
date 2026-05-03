(function (global) {
  const state = {
    open: false,
    size: 'half',
    boundKeydown: false,
  }

  function el(id) {
    return global.document && global.document.getElementById(id)
  }

  function getEls() {
    return {
      overlay: el('mobile-preview-overlay'),
      sheet: el('mobile-preview-sheet'),
      title: el('mobile-preview-title'),
      badge: el('mobile-preview-badge'),
      toggle: el('mobile-preview-toggle'),
      close: el('mobile-preview-close'),
      body: el('mobile-preview-body'),
    }
  }

  function applySize(sheet) {
    if (!sheet) return
    sheet.classList.toggle('sheet-half', state.size === 'half')
    sheet.classList.toggle('sheet-full', state.size === 'full')
  }

  function syncToggleText(toggle) {
    if (!toggle) return
    toggle.textContent = state.size === 'half' ? '展开' : '收起'
  }

  function closeMobilePreviewSheet() {
    const { overlay, sheet } = getEls()
    if (overlay) overlay.classList.add('hidden')
    if (sheet) sheet.classList.add('hidden')
    state.open = false
    state.size = 'half'
    if (sheet) applySize(sheet)
    const { toggle } = getEls()
    syncToggleText(toggle)
  }

  function ensureBound() {
    const { overlay, toggle, close } = getEls()
    if (overlay && overlay.dataset && overlay.dataset.bound !== '1') {
      overlay.dataset.bound = '1'
      overlay.addEventListener('click', () => closeMobilePreviewSheet())
    }
    if (toggle && toggle.dataset && toggle.dataset.bound !== '1') {
      toggle.dataset.bound = '1'
      toggle.addEventListener('click', () => toggleMobilePreviewSheetSize())
    }
    if (close && close.dataset && close.dataset.bound !== '1') {
      close.dataset.bound = '1'
      close.addEventListener('click', () => closeMobilePreviewSheet())
    }
    if (global.document && !state.boundKeydown) {
      state.boundKeydown = true
      global.document.addEventListener('keydown', (e) => {
        if (!state.open) return
        if (!e || e.key !== 'Escape') return
        const confirmModal = global.document.getElementById('confirm-modal')
        if (confirmModal && !confirmModal.classList.contains('hidden')) return
        const previewModal = global.document.getElementById('preview-modal')
        if (previewModal && !previewModal.classList.contains('hidden')) return
        closeMobilePreviewSheet()
      })
    }
  }

  function openMobilePreviewSheet(opts) {
    ensureBound()
    const { overlay, sheet, title, badge, toggle, body } = getEls()
    if (!overlay || !sheet || !body) return
    state.open = true
    state.size = 'half'
    applySize(sheet)
    syncToggleText(toggle)
    if (title) title.textContent = (opts && opts.title) ? String(opts.title) : ''
    if (badge) {
      const text = (opts && opts.badgeText) ? String(opts.badgeText) : ''
      const cls = (opts && opts.badgeCls) ? String(opts.badgeCls) : 'chip'
      badge.className = cls
      badge.textContent = text
    }
    body.innerHTML = (opts && opts.html) ? String(opts.html) : ''
    overlay.classList.remove('hidden')
    sheet.classList.remove('hidden')
  }

  function toggleMobilePreviewSheetSize() {
    const { sheet, toggle } = getEls()
    if (!sheet) return
    state.size = state.size === 'half' ? 'full' : 'half'
    applySize(sheet)
    syncToggleText(toggle)
  }

  global.openMobilePreviewSheet = openMobilePreviewSheet
  global.closeMobilePreviewSheet = closeMobilePreviewSheet
  global.toggleMobilePreviewSheetSize = toggleMobilePreviewSheetSize

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      openMobilePreviewSheet,
      closeMobilePreviewSheet,
      toggleMobilePreviewSheetSize,
      _internals: { getState: () => ({ ...state }), getEls },
    }
  }
})(typeof window !== 'undefined' ? window : globalThis)
