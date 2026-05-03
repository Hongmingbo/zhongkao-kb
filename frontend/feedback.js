(function (global) {
  function ensureToastStack() {
    let el = global.document && global.document.getElementById('toast-stack')
    if (el) return el
    if (!global.document || !global.document.body) return null
    el = global.document.createElement('div')
    el.id = 'toast-stack'
    el.className = 'fixed top-4 right-4 z-[60] space-y-2 w-[340px] max-w-[calc(100vw-2rem)] pointer-events-none'
    el.setAttribute('aria-live', 'polite')
    global.document.body.appendChild(el)
    return el
  }

  function toast(options) {
    const opts = options || {}
    const type = opts.type || 'info'
    const title = opts.title || ''
    const desc = opts.desc || ''
    const timeoutMs = Number.isFinite(opts.timeoutMs) ? Number(opts.timeoutMs) : 3000

    const stack = ensureToastStack()
    if (!stack) return

    while (stack.children.length >= 3) stack.removeChild(stack.firstElementChild)

    const barColor = type === 'error'
      ? '#ef4444'
      : (type === 'success' ? 'var(--accent)' : 'var(--primary)')

    const node = global.document.createElement('div')
    node.className = 'toast motion-safe'
    node.style.display = 'grid'
    node.style.gridTemplateColumns = '3px 1fr auto'
    node.style.gap = '12px'
    node.style.alignItems = 'start'

    const bar = global.document.createElement('div')
    bar.className = 'toast-bar'
    bar.style.background = barColor

    const content = global.document.createElement('div')
    const titleEl = global.document.createElement('div')
    titleEl.className = 'toast-title'
    titleEl.textContent = title
    content.appendChild(titleEl)
    if (desc) {
      const descEl = global.document.createElement('div')
      descEl.className = 'toast-desc'
      descEl.textContent = desc
      content.appendChild(descEl)
    }

    const close = global.document.createElement('button')
    close.type = 'button'
    close.className = 'btn btn-soft motion-safe'
    close.style.padding = '6px 10px'
    close.style.borderRadius = '10px'
    close.style.fontSize = '12px'
    close.textContent = '×'
    close.addEventListener('click', () => {
      if (node.parentElement) node.parentElement.removeChild(node)
    })

    node.appendChild(bar)
    node.appendChild(content)
    node.appendChild(close)
    stack.appendChild(node)

    if (timeoutMs > 0) {
      global.setTimeout(() => {
        if (node.parentElement) node.parentElement.removeChild(node)
      }, timeoutMs)
    }
  }

  function toastSuccess(title, desc) {
    toast({ type: 'success', title, desc })
  }

  function toastInfo(title, desc) {
    toast({ type: 'info', title, desc })
  }

  function toastError(title, desc) {
    toast({ type: 'error', title, desc })
  }

  function ensureConfirmModal() {
    let modal = global.document && global.document.getElementById('confirm-modal')
    if (modal) return modal
    if (!global.document || !global.document.body) return null

    modal = global.document.createElement('div')
    modal.id = 'confirm-modal'
    modal.className = 'fixed inset-0 z-[70] hidden bg-gray-900 bg-opacity-50 flex items-center justify-center p-4'
    modal.innerHTML = `
      <div class="bg-card rounded-xl shadow-lg w-full max-w-md card-border">
        <div class="p-4 card-border border-b flex items-center justify-between">
          <div id="confirm-title" class="text-lg font-semibold" style="color: var(--text);"></div>
          <button id="confirm-close" class="btn btn-soft motion-safe" style="padding: 6px 10px;">×</button>
        </div>
        <div class="p-4 space-y-4">
          <div id="confirm-message" class="text-sm muted"></div>
          <div class="flex justify-end gap-2">
            <button id="confirm-cancel" class="px-4 py-2 rounded-lg text-sm btn btn-soft motion-safe">取消</button>
            <button id="confirm-ok" class="px-4 py-2 rounded-lg text-sm btn btn-danger motion-safe">确认</button>
          </div>
        </div>
      </div>
    `
    global.document.body.appendChild(modal)
    return modal
  }

  let confirmActive = false

  function confirmDialog(options) {
    const opts = options || {}
    const title = opts.title || '请确认'
    const message = opts.message || ''
    const confirmText = opts.confirmText || '确认'
    const tone = opts.tone || 'danger'

    if (confirmActive) return Promise.resolve(false)
    const modal = ensureConfirmModal()
    if (!modal) return Promise.resolve(false)
    confirmActive = true

    const titleEl = modal.querySelector('#confirm-title')
    const msgEl = modal.querySelector('#confirm-message')
    const closeBtn = modal.querySelector('#confirm-close')
    const cancelBtn = modal.querySelector('#confirm-cancel')
    const okBtn = modal.querySelector('#confirm-ok')

    if (titleEl) titleEl.textContent = title
    if (msgEl) msgEl.textContent = message
    if (okBtn) {
      okBtn.textContent = confirmText
      okBtn.className = `px-4 py-2 rounded-lg text-sm btn ${tone === 'primary' ? 'btn-primary' : 'btn-danger'} motion-safe`
    }

    modal.classList.remove('hidden')

    return new Promise((resolve) => {
      const cleanup = (result) => {
        modal.classList.add('hidden')
        confirmActive = false
        global.document.removeEventListener('keydown', onKeyDown)
        if (closeBtn) closeBtn.removeEventListener('click', onCancel)
        if (cancelBtn) cancelBtn.removeEventListener('click', onCancel)
        if (okBtn) okBtn.removeEventListener('click', onOk)
        modal.removeEventListener('click', onOverlay)
        resolve(result)
      }

      const onCancel = () => cleanup(false)
      const onOk = () => cleanup(true)
      const onOverlay = (e) => {
        if (e.target === modal) cleanup(false)
      }
      const onKeyDown = (e) => {
        if (e.key === 'Escape') cleanup(false)
      }

      if (closeBtn) closeBtn.addEventListener('click', onCancel)
      if (cancelBtn) cancelBtn.addEventListener('click', onCancel)
      if (okBtn) okBtn.addEventListener('click', onOk)
      modal.addEventListener('click', onOverlay)
      global.document.addEventListener('keydown', onKeyDown)

      try {
        if (cancelBtn) cancelBtn.focus()
      } catch (e) {}
    })
  }

  global.toast = toast
  global.toastSuccess = toastSuccess
  global.toastInfo = toastInfo
  global.toastError = toastError
  global.confirmDialog = confirmDialog

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
      toast,
      toastSuccess,
      toastInfo,
      toastError,
      confirmDialog,
      _internals: { ensureToastStack, ensureConfirmModal },
    }
  }
})(typeof window !== 'undefined' ? window : globalThis)

