/**
 * @danweiyuan/ekit 工具库统一出口
 * 按模块分组导出：request（HTTP 请求）、storage（本地存储）、cookie、date（日期格式化）、
 * validators（表单校验）、copy（剪贴板）、qs（查询字符串）、file（文件下载）、hooks（Vue 组合式函数）、
 * masking（PII 数据脱敏）。业务代码统一从此入口导入。
 */

// Request
export { createRequest, tokenPlugin, headerPlugin, unwrapPlugin, refreshTokenPlugin } from './request'
export type { RequestPlugin, CreateRequestOptions } from './request'

// Storage
export { useStorage, storage } from './storage'

// Cookie
export { useCookie, cookie } from './cookie'
export type { CookieAttributes } from './cookie'

// Date
export { formatRelativeTime, formatDate, formatDateTime, formatTime, formatBy, dayjs } from './date'

// Validators
export { isPhone, isEmail, isIdCard, isUrl, isRequired, minLength, maxLength } from './validators'
export { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './validators/schemas'

// Copy
export { copyText, useClipboard } from './copy'

// QS
export { stringify, parse } from './qs'
export type { IStringifyOptions, IParseOptions } from './qs'

// File
export { downloadFile, saveBlob, formatFileSize } from './file'
export type { DownloadOptions } from './file'

// Hooks
export { useDebounce, useClickOutside, useEventListener } from './hooks'

// Hooks (vueuse)
export { useThrottle, useWindowSize, useMediaQuery, useIntersectionObserver, useResizeObserver } from './hooks/vueuse'

// Masking
export { maskPhone, maskEmail, maskIdCard, maskBankCard, maskName, maskAddress, maskIp, maskLicensePlate, maskText } from './masking'
