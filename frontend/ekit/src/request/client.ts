/**
 * createRequest 实现 + axios 适配层
 * axios 类型仅出现在本文件，不外泄；对外只暴露 HttpClient 契约
 */
import axios, {
  type AxiosInstance,
  type InternalAxiosRequestConfig,
  type AxiosRequestConfig,
  type AxiosResponse,
  type AxiosError,
} from 'axios'
import type {
  HttpClient,
  HttpConfig,
  HttpError,
  HttpMethod,
  HttpResponse,
  CreateRequestOptions,
} from './types'

// ==================== axios ↔ ekit 适配 ====================

function headersToPlain(headers: any): Record<string, string> {
  if (!headers) return {}
  if (typeof headers.toJSON === 'function') return headers.toJSON() as Record<string, string>
  // 过滤函数类型的字段（如 axios headers 对象上的方法）
  const out: Record<string, string> = {}
  for (const k of Object.keys(headers)) {
    const v = headers[k]
    if (typeof v !== 'function') out[k] = v as string
  }
  return out
}

function toHttpConfig(axiosCfg: InternalAxiosRequestConfig | AxiosRequestConfig): HttpConfig {
  const { url, method, baseURL, headers, params, data, timeout, responseType } = axiosCfg as any
  return {
    url,
    method: method ? (String(method).toUpperCase() as HttpMethod) : undefined,
    baseURL,
    headers: headersToPlain(headers),
    params,
    data,
    timeout,
    responseType: responseType as HttpConfig['responseType'],
  }
}

function fromHttpConfig(cfg: HttpConfig, base?: InternalAxiosRequestConfig | AxiosRequestConfig): AxiosRequestConfig {
  const { extra, ...rest } = cfg
  return {
    ...(base ?? {}),
    ...rest,
    ...((extra as AxiosRequestConfig) ?? {}),
  } as AxiosRequestConfig
}

function toHttpResponse<T>(axiosRes: AxiosResponse<T>): HttpResponse<T> {
  return {
    data: axiosRes.data,
    status: axiosRes.status,
    statusText: axiosRes.statusText,
    headers: headersToPlain(axiosRes.headers),
    config: toHttpConfig(axiosRes.config ?? {}),
  }
}

function toHttpError(axiosErr: AxiosError): HttpError {
  const err = new Error(axiosErr.message) as HttpError
  err.name = axiosErr.name
  err.code = axiosErr.code
  err.stack = axiosErr.stack
  err.config = axiosErr.config ? toHttpConfig(axiosErr.config) : undefined
  err.response = axiosErr.response ? toHttpResponse(axiosErr.response) : undefined
  return err
}

// ==================== createRequest ====================

export function createRequest(options: CreateRequestOptions = {}): HttpClient {
  const { baseURL = '/api', timeout = 30000, headers, plugins = [] } = options

  const instance: AxiosInstance = axios.create({ baseURL, timeout, headers })

  // 请求拦截：axios config → HttpConfig → 依次跑插件 → 回写 axios config
  instance.interceptors.request.use(
    async (axiosCfg) => {
      let cfg = toHttpConfig(axiosCfg)
      for (const plugin of plugins) {
        if (plugin.onRequest) cfg = await plugin.onRequest(cfg)
      }
      const merged = fromHttpConfig(cfg, axiosCfg) as InternalAxiosRequestConfig
      return merged
    },
    (error) => Promise.reject(error),
  )

  // 响应拦截：axios response → HttpResponse → 依次跑插件 → 合并回 axios response
  instance.interceptors.response.use(
    async (axiosRes) => {
      let res = toHttpResponse(axiosRes)
      for (const plugin of plugins) {
        if (plugin.onResponse) res = await plugin.onResponse(res)
      }
      // 回写到 axios response 对象（保留原有 axios 字段，仅替换被插件改动的部分）
      return Object.assign(axiosRes, {
        data: res.data,
        status: res.status,
        statusText: res.statusText,
      }) as AxiosResponse
    },
    async (axiosErr: AxiosError) => {
      let err: HttpError = toHttpError(axiosErr)
      for (const plugin of plugins) {
        if (plugin.onResponseError) {
          const result = await plugin.onResponseError(err)
          // 插件返回非 undefined = 已处理/已恢复，直接把结果当成响应
          if (result !== undefined) return result
        }
      }
      return Promise.reject(err)
    },
  )

  // axios 的 .request/.get/.post/... 返回 AxiosResponse，在外层统一转成 HttpResponse
  const toEkit = async <T>(p: Promise<AxiosResponse<T>>): Promise<HttpResponse<T>> => {
    const axiosRes = await p
    return toHttpResponse<T>(axiosRes)
  }

  return {
    request: <T = any>(config: HttpConfig) => toEkit<T>(instance.request(fromHttpConfig(config))),
    get: <T = any>(url: string, config?: HttpConfig) => toEkit<T>(instance.get(url, fromHttpConfig(config ?? {}))),
    post: <T = any>(url: string, data?: any, config?: HttpConfig) =>
      toEkit<T>(instance.post(url, data, fromHttpConfig(config ?? {}))),
    put: <T = any>(url: string, data?: any, config?: HttpConfig) =>
      toEkit<T>(instance.put(url, data, fromHttpConfig(config ?? {}))),
    delete: <T = any>(url: string, config?: HttpConfig) => toEkit<T>(instance.delete(url, fromHttpConfig(config ?? {}))),
    patch: <T = any>(url: string, data?: any, config?: HttpConfig) =>
      toEkit<T>(instance.patch(url, data, fromHttpConfig(config ?? {}))),
    head: <T = any>(url: string, config?: HttpConfig) => toEkit<T>(instance.head(url, fromHttpConfig(config ?? {}))),
  }
}
