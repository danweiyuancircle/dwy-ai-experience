import { afterEach, describe, expect, it, vi } from 'vitest'
import { createAdminAuthApi } from '../src/api'

const ok = (data: unknown) => new Response(JSON.stringify({ code: 'SUCCESS', data }))
afterEach(() => vi.unstubAllGlobals())

describe('管理员 Cookie API', () => {
  it('使用注入的同源地址与 Cookie，禁止重定向和缓存，不携带 Bearer', async () => {
    const fetcher = vi.fn().mockResolvedValue(ok({ username: 'operator' }))
    vi.stubGlobal('fetch', fetcher)
    const api = createAdminAuthApi({ baseURL: '/control/api' })
    expect(await api.login(' operator ', 'test-only-password')).toEqual({ username: 'operator' })
    const [url, options] = fetcher.mock.calls[0]
    expect(url).toBe(`${location.origin}/control/api/auth/login`)
    expect(options).toMatchObject({ method: 'POST', credentials: 'same-origin', mode: 'same-origin', redirect: 'error', cache: 'no-store' })
    expect(options.headers).not.toHaveProperty('Authorization')
    expect(JSON.parse(options.body)).toEqual({ username: 'operator', password: 'test-only-password' })
  })
  it.each(['https://foreign.invalid/api', '//foreign.invalid/api', '/api?redirect=1', '/api#fragment'])('拒绝不安全 backend 地址 %s，发送凭据前失败', baseURL => {
    const fetcher = vi.fn(); vi.stubGlobal('fetch', fetcher)
    expect(() => createAdminAuthApi({ baseURL })).toThrow()
    expect(fetcher).not.toHaveBeenCalled()
  })
  it.each([['', 'x'], ['a'.repeat(65), 'x'], ['admin', ''], ['admin', 'x'.repeat(257)]])('拒绝空值或超限输入', async (username, password) => {
    const fetcher = vi.fn(); vi.stubGlobal('fetch', fetcher)
    await expect(createAdminAuthApi({ baseURL: '/api/admin' }).login(username, password)).rejects.toThrow()
    expect(fetcher).not.toHaveBeenCalled()
  })
  it('接受长度上界并且只 POST 密码', async () => {
    const fetcher = vi.fn().mockResolvedValue(ok({ username: 'a'.repeat(64) })); vi.stubGlobal('fetch', fetcher)
    await createAdminAuthApi({ baseURL: '/api/admin' }).login('a'.repeat(64), 'x'.repeat(256))
    expect(fetcher.mock.calls[0][0]).not.toContain('xxx')
    expect(JSON.parse(fetcher.mock.calls[0][1].body).password).toHaveLength(256)
  })
  it('401 只在会话 API 触发失效回调，保留登录错误消息', async () => {
    const fetcher = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ message: '用户名或密码错误' }), { status: 401 })))
    vi.stubGlobal('fetch', fetcher)
    const onSessionExpired = vi.fn(), api = createAdminAuthApi({ baseURL: '/api/admin', onSessionExpired })
    await expect(api.login('admin', 'wrong')).rejects.toThrow('用户名或密码错误')
    expect(onSessionExpired).not.toHaveBeenCalled()
    await expect(api.me()).rejects.toMatchObject({ response: { status: 401 } })
    expect(onSessionExpired).toHaveBeenCalledOnce()
  })
  it('拒绝业务错误、无效响应和网络失败，退出失败不报成功', async () => {
    const fetcher = vi.fn().mockResolvedValueOnce(new Response(JSON.stringify({ code: 'INVALID', message: '拒绝' })))
      .mockResolvedValueOnce(ok({ username: 123 })).mockResolvedValueOnce(new Response('not json'))
      .mockRejectedValueOnce(new TypeError('offline')).mockResolvedValueOnce(new Response('{}', { status: 503 }))
    vi.stubGlobal('fetch', fetcher)
    const api = createAdminAuthApi({ baseURL: '/api/admin' })
    await expect(api.me()).rejects.toThrow('拒绝')
    await expect(api.me()).rejects.toThrow('响应')
    await expect(api.me()).rejects.toThrow('响应')
    await expect(api.me()).rejects.toThrow('offline')
    await expect(api.logout()).rejects.toMatchObject({ response: { status: 503 } })
  })
  it('退出使用 POST 与同源 Cookie', async () => {
    const fetcher = vi.fn().mockResolvedValue(ok(null)); vi.stubGlobal('fetch', fetcher)
    await createAdminAuthApi({ baseURL: `${location.origin}/api/admin/` }).logout()
    expect(fetcher.mock.calls[0][0]).toBe(`${location.origin}/api/admin/auth/logout`)
    expect(fetcher.mock.calls[0][1]).toMatchObject({ method: 'POST', credentials: 'same-origin' })
  })
})
