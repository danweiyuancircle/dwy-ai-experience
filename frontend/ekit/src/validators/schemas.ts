import { z } from 'zod'

/** Chinese mobile phone number */
export const phoneSchema = z.string().regex(/^1[3-9]\d{9}$/, '请输入正确的手机号')

/** Email — uses regex to match legacy behavior (accepts short TLDs like a.b@c.d) */
export const emailSchema = z.string().regex(/^[^\s@]+@[^\s@]+\.[^\s@]+$/, '请输入正确的邮箱')

/** Chinese ID card (18 digits) */
export const idCardSchema = z.string().regex(/^\d{17}[\dXx]$/, '请输入正确的身份证号')

/** URL — uses new URL() to match legacy behavior (supports ftp://, custom schemes, etc.) */
export const urlSchema = z.string().refine(
  (val) => {
    try { new URL(val); return true } catch { return false }
  },
  { message: '请输入正确的 URL' },
)

/** Non-empty (string / array / any truthy value) */
export const requiredSchema = z.any().refine(
  (val) => {
    if (val === null || val === undefined) return false
    if (typeof val === 'string') return val.trim().length > 0
    if (Array.isArray(val)) return val.length > 0
    return true
  },
  { message: '此项为必填' },
)

/** Min length factory */
export function minLengthSchema(min: number) {
  return z.string().min(min, `最少 ${min} 个字符`)
}

/** Max length factory */
export function maxLengthSchema(max: number) {
  return z.string().max(max, `最多 ${max} 个字符`)
}
