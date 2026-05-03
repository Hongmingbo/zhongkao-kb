const { copyText, installGlobalShortcuts } = require('../usability')

describe('copyText', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  test('uses navigator.clipboard.writeText when available', async () => {
    const writeText = jest.fn().mockResolvedValue(undefined)
    const ok = await copyText('hello', {
      navigator: { clipboard: { writeText } },
      document,
    })
    expect(ok).toBe(true)
    expect(writeText).toHaveBeenCalledWith('hello')
  })

  test('falls back to execCommand copy', async () => {
    document.execCommand = jest.fn().mockReturnValue(true)
    const ok = await copyText('hi', {
      navigator: {},
      document,
    })
    expect(ok).toBe(true)
    expect(document.execCommand).toHaveBeenCalledWith('copy')
  })
})

describe('global shortcuts', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <input id="searchQuery" />
      <div id="preview-modal"></div>
      <div id="confirm-modal" class="hidden"></div>
      <button id="confirm-cancel">取消</button>
    `
  })

  test('"/" focuses search and calls setActiveTab', () => {
    const setActiveTab = jest.fn()
    const searchQueryInput = document.getElementById('searchQuery')
    installGlobalShortcuts({ setActiveTab, searchQueryInput, previewModal: null, confirmModal: null })

    const ev = new KeyboardEvent('keydown', { key: '/' })
    document.dispatchEvent(ev)
    expect(setActiveTab).toHaveBeenCalledWith('search')
    expect(document.activeElement).toBe(searchQueryInput)
  })

  test('Ctrl+K focuses search and calls setActiveTab', () => {
    const setActiveTab = jest.fn()
    const searchQueryInput = document.getElementById('searchQuery')
    installGlobalShortcuts({ setActiveTab, searchQueryInput, previewModal: null, confirmModal: null })

    const ev = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    document.dispatchEvent(ev)
    expect(setActiveTab).toHaveBeenCalledWith('search')
    expect(document.activeElement).toBe(searchQueryInput)
  })

  test('Escape closes preview modal first when confirm modal hidden', () => {
    const setActiveTab = jest.fn()
    const searchQueryInput = document.getElementById('searchQuery')
    const previewModal = document.getElementById('preview-modal')
    previewModal.classList.remove('hidden')
    const confirmModal = document.getElementById('confirm-modal')
    confirmModal.classList.add('hidden')

    installGlobalShortcuts({ setActiveTab, searchQueryInput, previewModal, confirmModal })
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(previewModal.classList.contains('hidden')).toBe(true)
  })
})

