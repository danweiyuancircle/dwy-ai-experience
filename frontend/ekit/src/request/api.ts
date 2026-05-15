/**
 * 后端 dwyeapi 统一响应信封契约
 *
 * 对齐 dwyeapi v0.7.0 的 ApiResponse / PageData / 异常 handler 响应格式。
 * 字段命名保持与后端 JSON 1:1 对应(如 page_size 不做驼峰化),消费侧运行时零序列化开销。
 *
 * 本文件只定义接口/类型/常量,不引入任何运行时依赖。
 */

/** 业务成功的固定 code 值 */
export const SUCCESS_CODE = 'SUCCESS' as const

/**
 * dwyeapi 统一响应信封。
 *
 * 所有后端接口(成功或失败)都返回此结构。code === "SUCCESS" 表示业务成功,
 * 其他值为业务错误码;message 可直接展示给用户;data 失败时为 null。
 */
export interface ApiResponse<T = unknown> {
  /** 业务状态码,成功固定为 "SUCCESS",失败为业务错误码(如 "NOT_FOUND") */
  code: string
  /** 提示信息,可直接展示给用户 */
  message: string
  /** 响应数据载荷,错误时为 null */
  data: T | null
  /** Unix 秒级时间戳 */
  timestamp: number
}

/**
 * 分页数据载荷,配合 ApiResponse 组成分页响应。
 *
 * 完整响应类型为 ApiResponse<PageData<T>>,字段与后端 PaginationParams 对齐。
 */
export interface PageData<T = unknown> {
  /** 当前页的数据列表 */
  items: T[]
  /** 匹配条件的数据总数 */
  total: number
  /** 当前页码(从 1 开始) */
  page: number
  /** 每页条数 */
  page_size: number
}

/** 校验错误的单个字段详情 */
export interface ValidationFieldError {
  /** 字段路径,包含来源前缀,如 "body.email"、"query.page_size"、"body.items.0.name" */
  field: string
  /** 校验错误消息 */
  message: string
}

/** VALIDATION_ERROR 响应的 data 载荷 */
export interface ValidationErrorData {
  errors: ValidationFieldError[]
}

/**
 * dwyeapi 内置的业务错误码。
 *
 * 业务码 → HTTP 状态 → 含义 → 典型处理：
 *
 * - `'SUCCESS'`               → 200 → 业务成功（不会进 catch；unwrapPlugin 自动解包 data）
 * - `'NOT_FOUND'`             → 404 → 资源不存在 → 提示用户或跳 404 页
 * - `'BUSINESS_ERROR'`        → 422 → 业务规则不允许 → 基础码；业务常自定义如 `'INSUFFICIENT_BALANCE'` / `'STOCK_EMPTY'`，按 code 分支显示对应交互
 * - `'PERMISSION_DENIED'`     → 403 → 无权限 → 提示无权限或跳无权限页
 * - `'AUTHENTICATION_FAILED'` → 401 → 认证失败 → 由 refreshTokenPlugin 处理；不会到业务 catch
 * - `'VALIDATION_ERROR'`      → 422 → 请求参数校验失败 → data 为 ValidationErrorData，用 extractValidationErrors 提取后 setErrors 回填表单
 * - `'INTERNAL_ERROR'`        → 500 → 服务器错误 → 提示用户稍后重试 + 上报
 * - `` `HTTP_${number}` ``    → 原状态 → 第三方 HTTPException 透传（如 OAuth2 的 `'HTTP_401'`）
 *
 * BusinessCode = CommonBusinessCode | (string & {})：既保留常见码自动补全，又允许业务通过 BusinessError(code="CUSTOM") 自定义任意字符串。
 */
export type CommonBusinessCode =
  | 'NOT_FOUND'
  | 'BUSINESS_ERROR'
  | 'PERMISSION_DENIED'
  | 'AUTHENTICATION_FAILED'
  | 'VALIDATION_ERROR'
  | 'INTERNAL_ERROR'
  | `HTTP_${number}`

/**
 * 业务错误码类型。
 *
 * 使用 `CommonBusinessCode | (string & {})` 既保留对常见码的自动补全,
 * 又允许业务通过 BusinessError(code="CUSTOM") 自定义任意字符串。
 */
export type BusinessCode = CommonBusinessCode | (string & {})
