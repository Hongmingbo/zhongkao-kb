const { toast, confirmDialog } = require('../feedback')

describe('toast', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
    jest.useFakeTimers()
  })

  afterEach(() => {
    jest.useRealTimers()
  })

  test('adds a toast and auto-removes', () => {
    toast({ type: 'info', title: 't', desc: 'd', timeoutMs: 1000 })
    const stack = document.getElementById('toast-stack')
    expect(stack).toBeTruthy()
    expect(stack.children.length).toBe(1)
    jest.advanceTimersByTime(1000)
    expect(stack.children.length).toBe(0)
  })

  test('keeps at most 3 toasts', () => {
    toast({ title: '1', timeoutMs: 0 })
    toast({ title: '2', timeoutMs: 0 })
    toast({ title: '3', timeoutMs: 0 })
    toast({ title: '4', timeoutMs: 0 })
    const stack = document.getElementById('toast-stack')
    expect(stack.children.length).toBe(3)
    expect(stack.textContent.includes('1')).toBe(false)
  })
})

describe('confirmDialog', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  test('resolves true on confirm click', async () => {
    const p = confirmDialog({ title: 'x', message: 'y', confirmText: 'ok', tone: 'primary' })
    const ok = document.getElementById('confirm-ok')
    ok.click()
    await expect(p).resolves.toBe(true)
  })

  test('resolves false on escape', async () => {
    const p = confirmDialog({ title: 'x', message: 'y' })
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    await expect(p).resolves.toBe(false)
  })
})

