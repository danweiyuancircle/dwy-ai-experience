/**
 * 表单校验工具的布尔接口
 * 对 schemas.ts 中的 zod schema 做一层包装，返回 boolean 方便在模板条件/v-if 中直接使用
 * 需要错误消息时请直接使用 schemas.ts 中的 zod schema（配合 vee-validate）
 */
import { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './schemas'

/**
 * 校验是否为中国大陆手机号
 * @param value 待校验字符串
 */
export function isPhone(value: string): boolean {
  return phoneSchema.safeParse(value).success
}

/**
 * 校验是否为合法邮箱
 * @param value 待校验字符串
 */
export function isEmail(value: string): boolean {
  return emailSchema.safeParse(value).success
}

/**
 * 校验是否为 18 位身份证号（最后一位允许 X/x）
 * @param value 待校验字符串
 */
export function isIdCard(value: string): boolean {
  return idCardSchema.safeParse(value).success
}

/**
 * 校验是否为合法 URL（支持 http/https/ftp 及自定义协议）
 * @param value 待校验字符串
 */
export function isUrl(value: string): boolean {
  return urlSchema.safeParse(value).success
}

/**
 * 校验是否为"非空值"：字符串非全空白、数组非空、其他 truthy 视为有值
 * @param value 任意值
 */
export function isRequired(value: any): boolean {
  return requiredSchema.safeParse(value).success
}

/**
 * 校验字符串最小长度
 * @param value 待校验字符串
 * @param min 最小长度（含）
 */
export function minLength(value: string, min: number): boolean {
  return minLengthSchema(min).safeParse(value).success
}

/**
 * 校验字符串最大长度
 * @param value 待校验字符串
 * @param max 最大长度（含）
 */
export function maxLength(value: string, max: number): boolean {
  return maxLengthSchema(max).safeParse(value).success
}

// 再导出 zod schema，方便业务直接配合 vee-validate 使用
export { phoneSchema, emailSchema, idCardSchema, urlSchema, requiredSchema, minLengthSchema, maxLengthSchema } from './schemas'
