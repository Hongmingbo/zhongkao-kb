const {
  validateUsername,
  validatePassword,
  validateRename,
  withDisabled,
} = require('../safety')

describe('safety', () => {
  test('validateUsername allows cn/en/digits/_/- and enforces 3-32', () => {
    expect(validateUsername('张三_01')).toEqual({ ok: true, value: '张三_01' })
    expect(validateUsername('ab')).toEqual({ ok: false, reason: '用户名长度需为 3-32' })
    expect(validateUsername('a'.repeat(33))).toEqual({ ok: false, reason: '用户名长度需为 3-32' })
    expect(validateUsername('a/b')).toEqual({ ok: false, reason: '用户名仅允许中文、英文、数字、_、-' })
    expect(validateUsername('a\\\\b')).toEqual({ ok: false, reason: '用户名仅允许中文、英文、数字、_、-' })
  })

  test('validatePassword enforces >= 6', () => {
    expect(validatePassword('12345')).toEqual({ ok: false, reason: '密码至少 6 位' })
    expect(validatePassword('123456')).toEqual({ ok: true, value: '123456' })
  })

  test('validateRename rejects empty and slashes', () => {
    expect(validateRename('')).toEqual({ ok: false, reason: '文件名不能为空' })
    expect(validateRename('a/b')).toEqual({ ok: false, reason: '文件名不能包含 / 或 \\' })
    expect(validateRename('a\\\\b')).toEqual({ ok: false, reason: '文件名不能包含 / 或 \\' })
    expect(validateRename(' a.pdf ')).toEqual({ ok: true, value: 'a.pdf' })
  })

  test('withDisabled disables button during async fn', async () => {
    document.body.innerHTML = '<button id="b"></button>'
    const btn = document.getElementById('b')
    btn.disabled = false
    let inside = false
    const r = await withDisabled(btn, async () => { inside = btn.disabled; return 1 })
    expect(r).toBe(1)
    expect(inside).toBe(true)
    expect(btn.disabled).toBe(false)
  })
})

