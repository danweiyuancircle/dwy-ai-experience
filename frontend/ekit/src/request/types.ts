/**
 * ekit HTTP 抽象契约
 * 对外导出的类型全部定义在这里，createRequest 内部用 axios 实现，但对外不泄露 axios 任何类型
 * 以后要替换底层库（fetch / ofetch 等），消费者代码不用改
 */

/** 请求方法 */
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS'

/** 响应体类型 */
export type HttpResponseType = 'json' | 'blob' | 'text' | 'arraybuffer'

/** 请求配置 */
export interface HttpConfig {
  url?: string
  method?: HttpMethod
  baseURL?: string
  headers?: Record<string, string>
  params?: Record<string, any>
  data?: any
  timeout?: number
  responseType?: HttpResponseType
  /** 逃生舱：透传底层实现特有的配置选项；类型为 unknown，避免在契约层泄露具体库类型 */
  extra?: Record<string, unknown>
}

/** 请求响应 */
export interface HttpResponse<T = any> {
  data: T
  status: number
  statusText: string
  headers: Record<string, string>
  config: HttpConfig
}

/** 请求错误 */
export interface HttpError<T = any> extends Error {
  config?: HttpConfig
  response?: HttpResponse<T>
  code?: string
}

/** HTTP 客户端接口 */
export interface HttpClient {
  request<T = any>(config: HttpConfig): Promise<HttpResponse<T>>
  get<T = any>(url: string, config?: HttpConfig): Promise<HttpResponse<T>>
  post<T = any>(url: string, data?: any, config?: HttpConfig): Promise<HttpResponse<T>>
  put<T = any>(url: string, data?: any, config?: HttpConfig): Promise<HttpResponse<T>>
  delete<T = any>(url: string, config?: HttpConfig): Promise<HttpResponse<T>>
  patch<T = any>(url: string, data?: any, config?: HttpConfig): Promise<HttpResponse<T>>
  head<T = any>(url: string, config?: HttpConfig): Promise<HttpResponse<T>>
}

/**
 * 请求插件契约
 * 可选实现请求前 / 响应后 / 响应错误三个钩子；所有内置插件（token/header/unwrap/refreshToken）均实现此接口
 */
export interface HttpPlugin {
  /** 请求发出前对 config 做变换（如注入 header） */
  onRequest?: (config: HttpConfig) => HttpConfig | Promise<HttpConfig>
  /** 成功响应后对 response 做变换（如解包业务数据） */
  onResponse?: (response: HttpResponse) => HttpResponse | Promise<HttpResponse>
  /** 响应错误时处理（如 401 刷新 token）；返回非 undefined 则视为恢复成功，终止后续插件 */
  onResponseError?: (error: HttpError) => any
}

/** createRequest 选项 */
export interface CreateRequestOptions {
  /** 接口基础路径，默认 '/api' */
  baseURL?: string
  /** 请求超时时间（毫秒），默认 30000 */
  timeout?: number
  /** 所有请求共享的默认请求头 */
  headers?: Record<string, string>
  /** 启用的插件列表，按数组顺序执行 */
  plugins?: HttpPlugin[]
}
