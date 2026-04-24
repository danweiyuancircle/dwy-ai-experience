/**
 * HTTP 请求模块统一出口
 * 对外只暴露 ekit 自己的 HTTP 契约（HttpClient / HttpConfig / HttpResponse / HttpError / HttpPlugin 等）
 * 底层当前用 axios 实现，但对外完全屏蔽，替换底层时消费者代码不用改
 *
 * 额外导出 dwyeapi 响应契约（ApiResponse / PageData 等）及配套 helper，
 * 业务代码接入 dwyeapi 后端时可直接使用，无需自己定义类型
 */
export { createRequest } from './client'
export { tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin } from './plugins'
export { SUCCESS_CODE } from './api'
export { extractValidationErrors, isApiBusinessError } from './helpers'
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
export type {
  ApiResponse,
  PageData,
  ValidationFieldError,
  ValidationErrorData,
  CommonBusinessCode,
  BusinessCode,
} from './api'
export type { ApiBusinessError } from './helpers'
