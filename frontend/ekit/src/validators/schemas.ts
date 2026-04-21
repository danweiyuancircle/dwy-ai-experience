/**
 * 表单校验 zod schema 集合
 * 直接配合 vee-validate + zod 做表单级校验；错误消息用中文，可直接展示在 UI 上
 * 需要 boolean 接口请使用 validators/index.ts 导出的 isXxx 函数
 */
import { z } from 'zod'

/** 中国大陆手机号：1 开头，第二位 3-9，总 11 位 */
export const phoneSchema = z.string().regex(/^1[3-9]\d{9}$/, '请输入正确的手机号')

/**
 * 邮箱校验
 * 用正则而非 z.string().email()，兼容历史行为：允许短 TLD（如 a.b@c.d）
 */
export const emailSchema = z.string().regex(/^[^\s@]+@[^\s@]+\.[^\s@]+$/, '请输入正确的邮箱')

/** 18 位身份证号，最后一位允许 X/x */
export const idCardSchema = z.string().regex(/^\d{17}[\dXx]$/, '请输入正确的身份证号')

/**
 * URL 校验
 * 用 new URL() 而非 z.string().url()，兼容历史行为：支持 ftp:// 和自定义协议
 */
export const urlSchema = z.string().refine(
  (val) => {
    try { new URL(val); return true } catch { return false }
  },
  { message: '请输入正确的 URL' },
)

/**
 * 必填校验
 * 字符串：trim 后非空；数组：长度 > 0；其他 truthy 值视为已填
 */
export const requiredSchema = z.any().refine(
  (val) => {
    if (val === null || val === undefined) return false
    if (typeof val === 'string') return val.trim().length > 0
    if (Array.isArray(val)) return val.length > 0
    return true
  },
  { message: '此项为必填' },
)

/**
 * 最小长度 schema 工厂
 * @param min 最小字符数（含）
 */
export function minLengthSchema(min: number) {
  return z.string().min(min, `最少 ${min} 个字符`)
}

/**
 * 最大长度 schema 工厂
 * @param max 最大字符数（含）
 */
export function maxLengthSchema(max: number) {
  return z.string().max(max, `最多 ${max} 个字符`)
}
