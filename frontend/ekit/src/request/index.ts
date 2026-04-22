/**
 * HTTP 请求模块统一出口
 * 对外只暴露 ekit 自己的 HTTP 契约（HttpClient / HttpConfig / HttpResponse / HttpError / HttpPlugin 等）
 * 底层当前用 axios 实现，但对外完全屏蔽，替换底层时消费者代码不用改
 */
export { createRequest } from './client'
export { tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin } from './plugins'
export type {
  HttpMethod,
  HttpResponseType,
  HttpConfig,
  HttpResponse,
  HttpError,
  HttpClient,
  HttpPlugin,
  CreateRequestOptions,
} from './types'
