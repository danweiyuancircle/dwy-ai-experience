/**
 * dwyeapi 响应处理辅助工具
 *
 * 提供针对 unwrapPlugin 抛出的业务错误的类型守卫和结构化解包函数,
 * 让业务 catch 分支和 vee-validate 表单联动写起来更简单。
 */
import type { ApiResponse, ValidationErrorData, ValidationFieldError } from './api'
import type { HttpError } from './types'

/** 类型收紧:表明这是一个 ApiResponse 形态的业务错误,businessCode 与 apiResponse 必然存在 */
export type ApiBusinessError<T = unknown> = HttpError & {
  businessCode: string
  apiResponse: ApiResponse<T>
}

/**
 * 类型守卫:判断 catch 到的错误是否为 dwyeapi 的业务错误(由 unwrapPlugin 附加了 businessCode 和 apiResponse)。
 *
 * @example
 * ```ts
 * try {
 *   await http.post('/orders', body)
 * } catch (err) {
 *   if (isApiBusinessError(err)) {
 *     if (err.businessCode === 'INSUFFICIENT_BALANCE') showRecharge()
 *     else if (err.businessCode === 'VALIDATION_ERROR') form.setErrors(extractValidationErrors(err))
 *     else message.error(err.message)
 *   }
 * }
 * ```
 */
export function isApiBusinessError(err: unknown): err is ApiBusinessError {
  return (
    err instanceof Error
    && typeof (err as ApiBusinessError).businessCode === 'string'
    && typeof (err as ApiBusinessError).apiResponse === 'object'
    && (err as ApiBusinessError).apiResponse !== null
  )
}

const FIELD_PREFIXES = ['body.', 'query.', 'path.', 'header.', 'cookie.']

/** 剥离 field 的来源前缀(body./query./path./header./cookie.),让 key 更适合 vee-validate */
function stripFieldPrefix(field: string): string {
  for (const prefix of FIELD_PREFIXES) {
    if (field.startsWith(prefix)) {
      return field.slice(prefix.length)
    }
  }
  return field
}

/**
 * 把 dwyeapi 的 VALIDATION_ERROR 响应中 data.errors 数组转成 { field: message } 扁平对象。
 *
 * 自动剥离 body./query./path./header./cookie. 前缀,便于 vee-validate 的 form.setErrors 直接使用。
 * 同一字段多条错误时,后出现的覆盖先出现的(与 vee-validate 显示语义一致)。
 *
 * 输入容忍多种来源:
 * - unwrapPlugin 抛出的 HttpError(带 apiResponse)
 * - 完整的 ApiResponse 信封(比如直接从 HTTP 响应拿到的 body)
 * - 裸的 ValidationErrorData(已经解包出 data 的情况)
 *
 * 不是 VALIDATION_ERROR 形态时返回空对象,调用方无需额外判空。
 *
 * @example
 * ```ts
 * const { handleSubmit, setErrors } = useForm(...)
 * const submit = handleSubmit(async values => {
 *   try { await createUser(values) }
 *   catch (err) {
 *     if (isApiBusinessError(err)) setErrors(extractValidationErrors(err))
 *   }
 * })
 * ```
 */
export function extractValidationErrors(
  input: unknown,
): Record<string, string> {
  const data = resolveValidationErrorData(input)
  if (!data || !Array.isArray(data.errors)) {
    return {}
  }
  const result: Record<string, string> = {}
  for (const item of data.errors as ValidationFieldError[]) {
    if (!item || typeof item.field !== 'string') continue
    result[stripFieldPrefix(item.field)] = String(item.message ?? '')
  }
  return result
}

function resolveValidationErrorData(input: unknown): ValidationErrorData | null {
  if (!input || typeof input !== 'object') return null

  // HttpError 形态:从 apiResponse.data 取
  const asError = input as ApiBusinessError
  if (asError.apiResponse && typeof asError.apiResponse === 'object') {
    const payload = asError.apiResponse.data
    if (isValidationErrorData(payload)) return payload
  }

  // 完整 ApiResponse 形态:{ code, data, ... }
  const asResponse = input as ApiResponse<ValidationErrorData | null>
  if ('code' in asResponse && 'data' in asResponse) {
    if (isValidationErrorData(asResponse.data)) return asResponse.data
  }

  // 裸 ValidationErrorData 形态:{ errors: [...] }
  if (isValidationErrorData(input)) return input

  return null
}

function isValidationErrorData(value: unknown): value is ValidationErrorData {
  return (
    !!value
    && typeof value === 'object'
    && Array.isArray((value as ValidationErrorData).errors)
  )
}
