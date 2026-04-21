/**
 * Axios 请求工厂，封装插件式拦截器体系（token/header/unwrap/refreshToken）
 * 业务不直接用 axios，统一通过 createRequest(options) 生成实例，按需组合内置插件
 * 拦截器按 plugins 数组顺序串联执行，前一个插件的产出作为下一个插件的输入
 */
import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'

/**
 * 请求插件契约：可选实现请求前/响应后/响应错误三个钩子
 * 所有内置插件（token/header/unwrap/refreshToken）均实现此接口
 */
export interface RequestPlugin {
  /** 请求发出前对 config 做变换（如注入 header） */
  onRequest?: (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>
  /** 成功响应后对 response 做变换（如解包业务数据） */
  onResponse?: (response: AxiosResponse) => AxiosResponse | Promise<AxiosResponse>
  /** 响应错误时处理（如 401 刷新 token）；返回非 undefined 则视为恢复成功，终止后续插件 */
  onResponseError?: (error: AxiosError) => any
}

/**
 * createRequest 选项
 */
export interface CreateRequestOptions {
  /** 接口基础路径，默认 '/api' */
  baseURL?: string
  /** 请求超时时间（毫秒），默认 30000 */
  timeout?: number
  /** 启用的插件列表，按数组顺序执行拦截器 */
  plugins?: RequestPlugin[]
}

/**
 * 创建装配好拦截器的 Axios 实例
 * @param options 基础配置与插件列表
 * @returns 可直接使用的 AxiosInstance
 */
export function createRequest(options: CreateRequestOptions = {}): AxiosInstance {
  const { baseURL = '/api', timeout = 30000, plugins = [] } = options

  const instance = axios.create({ baseURL, timeout })

  // 请求拦截器：顺序执行所有插件的 onRequest
  instance.interceptors.request.use(
    async (config) => {
      let cfg = config
      for (const plugin of plugins) {
        if (plugin.onRequest) {
          cfg = await plugin.onRequest(cfg)
        }
      }
      return cfg
    },
    (error) => Promise.reject(error)
  )

  // 响应拦截器：成功走 onResponse 链；失败轮询 onResponseError，任一插件返回非 undefined 即视为恢复
  instance.interceptors.response.use(
    async (response) => {
      let res = response
      for (const plugin of plugins) {
        if (plugin.onResponse) {
          res = await plugin.onResponse(res)
        }
      }
      return res
    },
    async (error) => {
      for (const plugin of plugins) {
        if (plugin.onResponseError) {
          const result = await plugin.onResponseError(error)
          // 插件返回非 undefined = 已处理/已恢复，直接把结果当成响应
          if (result !== undefined) return result
        }
      }
      return Promise.reject(error)
    }
  )

  return instance
}

// 内置插件

/**
 * Token 注入插件：为每个请求附加 Authorization: Bearer <token>
 * @param options.getToken 取 token 的函数；返回 null 时不注入
 */
export function tokenPlugin(options: { getToken: () => string | null }): RequestPlugin {
  return {
    onRequest(config) {
      const token = options.getToken()
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
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
export function headerPlugin(options: { name: string; getValue: () => string | null }): RequestPlugin {
  return {
    onRequest(config) {
      const value = options.getValue()
      if (value) {
        config.headers[options.name] = value
      }
      return config
    },
  }
}

/**
 * 响应解包插件：将后端统一格式 { code, data, message } 中 code !== 200 的情况转为 reject
 * 不是该格式的响应原样透传，兼容第三方接口
 */
export function unwrapPlugin(): RequestPlugin {
  return {
    onResponse(response) {
      const res = response.data
      if (res && typeof res === 'object' && 'code' in res) {
        if (res.code !== 200) {
          return Promise.reject(new Error(res.message || 'Error')) as any
        }
        // 直接返回 { code, data, message }，业务代码拿 .data 即可
        return res
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
 */
export function refreshTokenPlugin(options: {
  isLoginUrl?: (url: string) => boolean
  getRefreshToken: () => string | null
  refreshFn: (refreshToken: string) => Promise<string>
  onRefreshFail: () => void
}): RequestPlugin {
  return {
    async onResponseError(error) {
      // 登录接口本身 401 不刷新，避免死循环
      const isLogin = options.isLoginUrl?.(error.config?.url || '') ?? error.config?.url?.includes('/auth/login')
      if (error.response?.status === 401 && !isLogin) {
        const refreshToken = options.getRefreshToken()
        if (refreshToken) {
          try {
            const newToken = await options.refreshFn(refreshToken)
            if (error.config) {
              error.config.headers.Authorization = `Bearer ${newToken}`
              // 用新 token 重放原请求
              return axios(error.config)
            }
          } catch {
            options.onRefreshFail()
          }
        } else {
          options.onRefreshFail()
        }
      }
      // 统一错误消息：优先后端 detail/message，再退回 axios 默认
      const data = error.response?.data as Record<string, any> | undefined
      const msg = data?.detail || data?.message || error.message || 'Error'
      return Promise.reject(new Error(msg))
    },
  }
}
