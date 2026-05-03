const {
  openMobilePreviewSheet,
  closeMobilePreviewSheet,
  toggleMobilePreviewSheetSize,
  _internals,
} = require('../mobile_preview')

describe('mobile preview sheet', () => {
  beforeEach(() => {
    document.body.innerHTML = `
      <div id="mobile-preview-overlay" class="hidden"></div>
      <div id="mobile-preview-sheet" class="hidden sheet-half"></div>
      <div id="mobile-preview-title"></div>
      <div id="mobile-preview-badge"></div>
      <button id="mobile-preview-toggle"></button>
      <button id="mobile-preview-close"></button>
      <div id="mobile-preview-body"></div>
    `
  })

  test('open shows overlay and sheet as half by default', () => {
    openMobilePreviewSheet({ title: 't', badgeText: 'PDF', badgeCls: 'chip', html: '<div>c</div>' })
    const overlay = document.getElementById('mobile-preview-overlay')
    const sheet = document.getElementById('mobile-preview-sheet')
    expect(overlay.classList.contains('hidden')).toBe(false)
    expect(sheet.classList.contains('hidden')).toBe(false)
    expect(sheet.classList.contains('sheet-half')).toBe(true)
    expect(sheet.classList.contains('sheet-full')).toBe(false)
  })

  test('toggle switches between half and full', () => {
    openMobilePreviewSheet({ title: 't', badgeText: 'PDF', badgeCls: 'chip', html: '<div>c</div>' })
    toggleMobilePreviewSheetSize()
    let sheet = document.getElementById('mobile-preview-sheet')
    expect(sheet.classList.contains('sheet-full')).toBe(true)
    toggleMobilePreviewSheetSize()
    sheet = document.getElementById('mobile-preview-sheet')
    expect(sheet.classList.contains('sheet-half')).toBe(true)
  })

  test('close hides overlay and sheet', () => {
    openMobilePreviewSheet({ title: 't', badgeText: 'PDF', badgeCls: 'chip', html: '<div>c</div>' })
    closeMobilePreviewSheet()
    const overlay = document.getElementById('mobile-preview-overlay')
    const sheet = document.getElementById('mobile-preview-sheet')
    expect(overlay.classList.contains('hidden')).toBe(true)
    expect(sheet.classList.contains('hidden')).toBe(true)
  })

  test('overlay click closes', () => {
    openMobilePreviewSheet({ title: 't', badgeText: 'PDF', badgeCls: 'chip', html: '<div>c</div>' })
    const overlay = document.getElementById('mobile-preview-overlay')
    overlay.click()
    expect(overlay.classList.contains('hidden')).toBe(true)
  })

  test('escape closes when open', () => {
    openMobilePreviewSheet({ title: 't', badgeText: 'PDF', badgeCls: 'chip', html: '<div>c</div>' })
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(document.getElementById('mobile-preview-overlay').classList.contains('hidden')).toBe(true)
  })

  test('internals exposes getState', () => {
    const st = _internals.getState()
    expect(st).toBeTruthy()
  })
})

