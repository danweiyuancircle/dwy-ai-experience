import { afterEach, expect, it, vi } from 'vitest'
import { createAdminSession } from '../src/session'
import { createAdminAuthApi } from '../src/api'

afterEach(() => { vi.unstubAllGlobals(); vi.restoreAllMocks(); localStorage.clear() })
it('只在内存保存服务端身份；实例隔离且不写入任何浏览器凭据', async () => {
  const write = vi.spyOn(Storage.prototype, 'setItem')
  const fetcher = vi.fn().mockImplementation(() => Promise.resolve(new Response(JSON.stringify({ code: 'SUCCESS', data: { username: 'admin' } }))))
  vi.stubGlobal('fetch', fetcher)
  const api = createAdminAuthApi({ baseURL: '/api/admin' }), session = createAdminSession(api)
  await session.login('admin', 'test-only-password')
  expect(session.administrator.value).toEqual({ username: 'admin' })
  expect(createAdminSession(api).administrator.value).toBeNull()
  expect(write).not.toHaveBeenCalled()
  expect(localStorage.length).toBe(0)
  expect(JSON.stringify(session.administrator.value)).not.toContain('password')
})
it('服务端退出失败时保留身份以便重试；成功才清空', async () => {
  const api = { login: vi.fn().mockResolvedValue({ username: 'admin' }), me: vi.fn(), logout: vi.fn().mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(undefined) }
  const session = createAdminSession(api)
  await session.login('admin', 'test-only-password')
  await expect(session.logout()).rejects.toThrow('offline')
  expect(session.administrator.value?.username).toBe('admin')
  await session.logout()
  expect(session.administrator.value).toBeNull()
})
it('刷新向服务器恢复身份，失效后迟到响应不能恢复已退出身份', async () => {
  let finish!: (value: { username: string }) => void
  const api = { login: vi.fn(), me: vi.fn().mockReturnValue(new Promise(resolve => { finish = resolve })), logout: vi.fn() }
  const session = createAdminSession(api), pending = session.restore()
  session.invalidate()
  finish({ username: 'admin' })
  await pending
  expect(session.administrator.value).toBeNull()
})
