import axios, { type AxiosInstance, type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from 'axios'

export interface RequestPlugin {
  onRequest?: (config: InternalAxiosRequestConfig) => InternalAxiosRequestConfig | Promise<InternalAxiosRequestConfig>
  onResponse?: (response: AxiosResponse) => AxiosResponse | Promise<AxiosResponse>
  onResponseError?: (error: AxiosError) => any
}

export interface CreateRequestOptions {
  baseURL?: string
  timeout?: number
  plugins?: RequestPlugin[]
}

export function createRequest(options: CreateRequestOptions = {}): AxiosInstance {
  const { baseURL = '/api', timeout = 30000, plugins = [] } = options

  const instance = axios.create({ baseURL, timeout })

  // Apply request interceptor plugins
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

  // Apply response interceptor plugins
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
          if (result !== undefined) return result
        }
      }
      return Promise.reject(error)
    }
  )

  return instance
}

// Built-in plugins

/** Inject Authorization Bearer token into every request */
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

/** Inject a custom header into every request */
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

/** Unwrap { code, data, message } response format — reject if code !== 200 */
export function unwrapPlugin(): RequestPlugin {
  return {
    onResponse(response) {
      const res = response.data
      if (res && typeof res === 'object' && 'code' in res) {
        if (res.code !== 200) {
          return Promise.reject(new Error(res.message || 'Error')) as any
        }
        return res // Return unwrapped { code, data, message }
      }
      return response
    },
  }
}

/** Handle 401 by calling a refresh function, then retry the original request */
export function refreshTokenPlugin(options: {
  isLoginUrl?: (url: string) => boolean
  getRefreshToken: () => string | null
  refreshFn: (refreshToken: string) => Promise<string>
  onRefreshFail: () => void
}): RequestPlugin {
  return {
    async onResponseError(error) {
      const isLogin = options.isLoginUrl?.(error.config?.url || '') ?? error.config?.url?.includes('/auth/login')
      if (error.response?.status === 401 && !isLogin) {
        const refreshToken = options.getRefreshToken()
        if (refreshToken) {
          try {
            const newToken = await options.refreshFn(refreshToken)
            if (error.config) {
              error.config.headers.Authorization = `Bearer ${newToken}`
              return axios(error.config)
            }
          } catch {
            options.onRefreshFail()
          }
        } else {
          options.onRefreshFail()
        }
      }
      const data = error.response?.data as Record<string, any> | undefined
      const msg = data?.detail || data?.message || error.message || 'Error'
      return Promise.reject(new Error(msg))
    },
  }
}
