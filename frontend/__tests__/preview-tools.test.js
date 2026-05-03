const { hydrateRawPreview } = require('../preview_tools')

describe('preview_tools', () => {
  beforeEach(() => {
    document.body.innerHTML = ''
  })

  test('hydrateRawPreview fetches blob and sets object url on preview element', async () => {
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
    container.innerHTML = `<img data-preview-raw="1" alt="p" />`
    document.body.appendChild(container)

    const ok = await hydrateRawPreview({ container, rawPath: '/api/file/raw/a/b.png', apiFetch })
    expect(ok).toBe(true)
    expect(apiFetch).toHaveBeenCalledWith('/api/file/raw/a/b.png')
    expect(container.dataset.rawObjUrl).toBe('blob:mock')
    expect(container.querySelector('img').src).toBe('blob:mock')

    await hydrateRawPreview({ container, rawPath: '/api/file/raw/a/c.png', apiFetch })
    expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:mock')

    URL.createObjectURL = prevCreate
    URL.revokeObjectURL = prevRevoke
  })
})
