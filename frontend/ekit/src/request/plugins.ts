/**
 * 内置 HTTP 插件：token / header / unwrap / refreshToken
 * 只依赖 ekit 自己的 HttpPlugin / HttpConfig / HttpResponse / HttpError 契约，不依赖 axios
 */
import type { HttpConfig, HttpPlugin, HttpResponse } from './types'

/**
 * Token 注入插件：为每个请求附加 Authorization: Bearer <token>
 * @param options.getToken 取 token 的函数；返回 null 时不注入
 */
export function tokenPlugin(options: { getToken: () => string | null }): HttpPlugin {
  return {
    onRequest(config) {
      const token = options.getToken()
      if (token) {
        config.headers = { ...config.headers, Authorization: `Bearer ${token}` }
      }
      return config
    },
  }
}

/**
 * 自定义请求头注入插件：为每个请求附加一个动态 header
 * @param options.name header 名称
 * @param options.getValue 取值函数；返回 null 时不注入
 */
export function headerPlugin(options: { name: string; getValue: () => string | null }): HttpPlugin {
  return {
    onRequest(config) {
      const value = options.getValue()
      if (value) {
        config.headers = { ...config.headers, [options.name]: value }
      }
      return config
    },
  }
}

/**
 * 响应解包插件：将后端统一格式 { code, data, message } 中 code !== 200 的情况转为 reject
 * 解包后 response.data 直接是业务数据；不是该格式的响应原样透传，兼容第三方接口
 */
export function unwrapPlugin(): HttpPlugin {
  return {
    onResponse(response) {
      const payload = response.data as any
      if (payload && typeof payload === 'object' && 'code' in payload) {
        if (payload.code !== 200) {
          return Promise.reject(new Error(payload.message || 'Error')) as any
        }
        // 把 response.data 替换为业务数据（payload.data），保留 response 壳
        return { ...response, data: payload.data }
      }
      return response
    },
  }
}

/**
 * 401 自动刷新 token 插件：捕获 401 后调用 refreshFn 换新 token 并重放原请求
 * @param options.isLoginUrl 判断是否为登录接口（避免无限刷新）；缺省时按 url 含 '/auth/login' 判断
 * @param options.getRefreshToken 取 refresh token 的函数
 * @param options.refreshFn 调后端换 access token 的函数，返回新 token
 * @param options.onRefreshFail 刷新失败（如 refresh token 也过期）时的回调，通常跳登录页
 * @param options.retry 刷新成功后重放原请求的函数。典型用法：
 *   ```
 *   let client: HttpClient
 *   client = createRequest({ plugins: [refreshTokenPlugin({ ..., retry: cfg => client.request(cfg) })] })
 *   ```
 */
export function refreshTokenPlugin(options: {
  isLoginUrl?: (url: string) => boolean
  getRefreshToken: () => string | null
  refreshFn: (refreshToken: string) => Promise<string>
  onRefreshFail: () => void
  retry: (config: HttpConfig) => Promise<HttpResponse>
}): HttpPlugin {
  return {
    async onResponseError(error) {
      // 登录接口本身 401 不刷新，避免死循环
      const url = error.config?.url ?? ''
      const isLogin = options.isLoginUrl?.(url) ?? url.includes('/auth/login')
      if (error.response?.status === 401 && !isLogin) {
        const refreshToken = options.getRefreshToken()
        if (refreshToken) {
          try {
            const newToken = await options.refreshFn(refreshToken)
            if (error.config) {
              const retryCfg: HttpConfig = {
                ...error.config,
                headers: { ...error.config.headers, Authorization: `Bearer ${newToken}` },
              }
              return await options.retry(retryCfg)
            }
          } catch {
            options.onRefreshFail()
          }
        } else {
          options.onRefreshFail()
        }
      }
      // 统一错误消息：优先后端 detail/message，再退回 HttpError.message
      const data = error.response?.data as Record<string, any> | undefined
      const msg = data?.detail || data?.message || error.message || 'Error'
      return Promise.reject(new Error(msg))
    },
  }
}
