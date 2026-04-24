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
 * - NOT_FOUND / PERMISSION_DENIED / AUTHENTICATION_FAILED / VALIDATION_ERROR / INTERNAL_ERROR 由 handler 固定填入
 * - BUSINESS_ERROR 是基础码,业务常自定义(如 "INSUFFICIENT_BALANCE")
 * - HTTP_xxx 由 HTTPException handler 按原状态码生成(如 "HTTP_401")
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
