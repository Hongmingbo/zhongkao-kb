(function (global) {
  function ok(value) {
    return { ok: true, value }
  }

  function bad(reason) {
    return { ok: false, reason: String(reason || '') }
  }

  function validateUsername(input) {
    const value = String(input == null ? '' : input).trim()
    if (value.length < 3 || value.length > 32) return bad('用户名长度需为 3-32')
    if (value.includes('/') || value.includes('\\')) return bad('用户名仅允许中文、英文、数字、_、-')
    if (!/^[\p{Script=Han}A-Za-z0-9_-]+$/u.test(value)) return bad('用户名仅允许中文、英文、数字、_、-')
    return ok(value)
  }

  function validatePassword(input) {
    const value = String(input == null ? '' : input).trim()
    if (value.length < 6) return bad('密码至少 6 位')
    return ok(value)
  }

  function validateRename(input) {
    const value = String(input == null ? '' : input).trim()
    if (!value) return bad('文件名不能为空')
    if (value.includes('/') || value.includes('\\')) return bad('文件名不能包含 / 或 \\')
    return ok(value)
  }

  async function withDisabled(btn, fn) {
    if (!btn || typeof fn !== 'function') return fn()
    const prev = !!btn.disabled
    btn.disabled = true
    if (btn.classList) btn.classList.add('is-disabled')
    try {
      return await fn()
    } finally {
      btn.disabled = prev
      if (btn.classList) btn.classList.remove('is-disabled')
    }
  }

  global.validateUsername = validateUsername
  global.validatePassword = validatePassword
  global.validateRename = validateRename
  global.withDisabled = withDisabled

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = { validateUsername, validatePassword, validateRename, withDisabled }
  }
})(typeof window !== 'undefined' ? window : globalThis)

