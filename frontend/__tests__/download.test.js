describe('download helper', () => {
  test('downloadFile is exported for tests', () => {
    const { downloadFile } = require('../download_internals')
    expect(typeof downloadFile).toBe('function')
  })

  test('hydrateRawPreview is exported for tests', () => {
    const { hydrateRawPreview } = require('../download_internals')
    expect(typeof hydrateRawPreview).toBe('function')
  })

  test('hydrateRawPreview fetches blob and sets object url on preview element', async () => {
    const { hydrateRawPreview } = require('../download_internals')
    const apiFetch = jest.fn(async () => ({
      ok: true,
      status: 200,
      blob: async () => new Blob(['x'], { type: 'image/png' }),
    }))
    const prevCreate = URL.createObjectURL
    const prevRevoke = URL.revokeObjectURL
    URL.createObjectURL = jest.fn(() => 'blob:mock')
    URL.revokeObjectURL = jest.fn(() => {})

    const container = document.createElement('div')
    container.innerHTML = `<div data-preview-loading="1">loading</div><img data-preview-raw="1" alt="p" />`
    document.body.appendChild(container)

    const ok = await hydrateRawPreview({ container, rawPath: '/api/file/raw/a/b.png', apiFetch })
    expect(ok).toBe(true)
    expect(apiFetch).toHaveBeenCalledWith('/api/file/raw/a/b.png')
    expect(container.dataset.rawObjUrl).toBe('blob:mock')
    expect(container.querySelector('img').src).toBe('blob:mock')
    expect(container.querySelector('[data-preview-loading="1"]')).toBe(null)

    await hydrateRawPreview({ container, rawPath: '/api/file/raw/a/c.png', apiFetch })
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock')

    URL.createObjectURL = prevCreate
    URL.revokeObjectURL = prevRevoke
  })
})
