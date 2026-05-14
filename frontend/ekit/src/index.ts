/**
 * @danweiyuan/ekit 工具库统一出口
 * 按模块分组导出：request（HTTP 请求）、storage（本地存储）、cookie、date（日期格式化）、
 * validators（表单校验）、copy（剪贴板）、qs（查询字符串）、file（文件下载）、hooks（Vue 组合式函数）、
 * masking（PII 数据脱敏）。业务代码统一从此入口导入。
 *
 * 所有对外契约均为 ekit 自有类型，不导出底层库（axios / dayjs / qs / js-cookie 等）的实例、命名空间、类型别名
 */

// Request
export {
  createRequest,
  tokenPlugin,
  headerPlugin,
  unwrapPlugin,
  refreshTokenPlugin,
  SUCCESS_CODE,
  extractValidationErrors,
  isApiBusinessError,
} from './request'
export type {
  HttpMethod,
  HttpResponseType,
  HttpConfig,
  HttpResponse,
  HttpError,
  HttpClient,
  HttpPlugin,
  CreateRequestOptions,
  ApiResponse,
  PageData,
  ValidationFieldError,
  ValidationErrorData,
  CommonBusinessCode,
  BusinessCode,
  ApiBusinessError,
} from './request'

// Storage
export { useStorage, storage } from './storage'

// Cookie
export { useCookie, cookie } from './cookie'
export type { CookieOptions } from './cookie'

// Date
export {
  now,
  formatTimestamp,
  formatInTimezone,
  formatRelativeTime,
  formatDate,
  formatDateTime,
  formatTime,
  formatBy,
} from './date'

// Validators
export { isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength } from './validators'
export { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './validators/schemas'

// Copy
export { copyText, useClipboard } from './copy'

// QS
export { stringify, parse } from './qs'
export type { StringifyOptions, ParseOptions } from './qs'

// File
export { downloadFile, saveBlob, formatFileSize } from './file'
export type { DownloadOptions, FileRequester } from './file'

// Hooks
export { useDebounce, useClickOutside, useEventListener, useFormPersist, DEFAULT_SENSITIVE_FIELDS } from './hooks'
export type { UseFormPersistOptions, UseFormPersistReturn } from './hooks'

// Hooks (vueuse)
export { useThrottle, useWindowSize, useMediaQuery, useIntersectionObserver, useResizeObserver } from './hooks/vueuse'

// Masking
export { maskPhone, maskEmail, maskIdCard, maskBankCard, maskName, maskAddress, maskIp, maskLicensePlate, maskText } from './masking'
