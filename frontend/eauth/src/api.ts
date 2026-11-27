import type { AdminAuthApi, AdminAuthOptions, AdminIdentity } from './types'

/** 管理认证错误保留 HTTP 状态，兼容宿主既有 response.status 判断。 */
export class AdminAuthError extends Error {
  readonly response: { status: number }
  constructor(message: string, status: number) {
    super(message)
    this.name = 'AdminAuthError'
    this.response = { status }
  }
}

/** 创建浏览器管理员 API；只发送同源 HttpOnly Cookie，不读写浏览器存储。 */
export function createAdminAuthApi(options: AdminAuthOptions): AdminAuthApi {
  const base = new URL(options.baseURL, `${location.origin}/`)
  if (base.origin !== location.origin || base.username || base.password || base.search || base.hash) {
    throw new Error('管理 API 必须使用不含凭据、查询或片段的同源地址')
  }
  const baseURL = base.href.replace(/\/$/, '')

  async function request(path: string, method: 'GET' | 'POST', body?: unknown): Promise<unknown> {
    const response = await fetch(`${baseURL}/auth/${path}`, {
      method, credentials: 'same-origin', mode: 'same-origin', redirect: 'error', cache: 'no-store',
      headers: body === undefined ? { Accept: 'application/json' } : { Accept: 'application/json', 'Content-Type': 'application/json' },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(15000),
    })
    if (response.status === 401 && path !== 'login') options.onSessionExpired?.()
    let payload: unknown
    try { payload = await response.json() }
    catch (cause) {
      if (!(cause instanceof SyntaxError)) throw cause
      throw new AdminAuthError('管理服务响应无效，请重试', response.status)
    }
    const envelope = payload && typeof payload === 'object' ? payload as Record<string, unknown> : null
    if (!response.ok || envelope?.code !== 'SUCCESS') {
      throw new AdminAuthError(typeof envelope?.message === 'string' ? envelope.message : '请求失败，请稍后重试', response.status)
    }
    return envelope.data
  }
  return {
    async login(username, password) {
      const normalized = username.trim()
      validateCredentials(normalized, password)
      return identity(await request('login', 'POST', { username: normalized, password }))
    },
    async me() { return identity(await request('me', 'GET')) },
    async logout() { await request('logout', 'POST') },
  }
}

/** 与服务端输入上界一致；组件和 API 两个入口都必须阻止脚本绕过表单约束。 */
export function validateCredentials(username: string, password: string): void {
  if (!username.trim() || username.trim().length > 64) throw new Error('用户名长度须为 1–64 个字符')
  if (!password || password.length > 256) throw new Error('密码长度须为 1–256 个字符')
}

function identity(data: unknown): AdminIdentity {
  if (!data || typeof data !== 'object' || !('username' in data) || typeof data.username !== 'string' || !data.username || data.username.length > 64) {
    throw new AdminAuthError('管理服务身份响应无效，请重试', 200)
  }
  // 只复制公开字段，即使服务端误加字段也不会将原始凭据留在会话中。
  return { username: data.username }
}
