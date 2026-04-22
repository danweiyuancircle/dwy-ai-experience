/**
 * 查询字符串序列化/反序列化封装
 * 基于 qs；对外的 Options 契约由 ekit 自行定义，屏蔽底层库类型（方便以后替换）
 * 设置项目统一默认值（数组用 repeat 格式、parse 时自动剥去前导 '?'）
 */
import QS from 'qs'

/** stringify 选项（ekit 对外契约，不直接泄露 qs 类型） */
export interface StringifyOptions {
  /** 数组序列化格式：'repeat' → ids=1&ids=2；'brackets' → ids[]=1；'indices' → ids[0]=1；'comma' → ids=1,2 */
  arrayFormat?: 'repeat' | 'brackets' | 'indices' | 'comma'
  /** 是否自动添加 '?' 前缀 */
  addQueryPrefix?: boolean
  /** 是否跳过 null 值 */
  skipNulls?: boolean
}

/** parse 选项（ekit 对外契约，不直接泄露 qs 类型） */
export interface ParseOptions {
  /** 是否自动忽略字符串前导 '?' */
  ignoreQueryPrefix?: boolean
  /** 是否允许点表达式 a.b=1（解析为 { a: { b: '1' } }） */
  allowDots?: boolean
}

/** stringify 默认配置：数组重复 key、不自动拼 ? 前缀 */
const defaultStringifyOptions: StringifyOptions = {
  arrayFormat: 'repeat',
  addQueryPrefix: false,
}

/** parse 默认配置：自动忽略前导 '?' */
const defaultParseOptions: ParseOptions = {
  ignoreQueryPrefix: true,
}

/**
 * 对象序列化为查询字符串
 * @param obj 待序列化的对象
 * @param options 覆盖默认选项（合并而非替换）
 * @returns 查询字符串，如 'a=1&b=2'
 */
export function stringify(obj: Record<string, any>, options?: StringifyOptions): string {
  return QS.stringify(obj, { ...defaultStringifyOptions, ...options })
}

/**
 * 查询字符串解析为对象
 * @param str 查询字符串（可带或不带前导 '?'）
 * @param options 覆盖默认选项（合并而非替换）
 * @returns 解析后的对象
 */
export function parse(str: string, options?: ParseOptions): Record<string, any> {
  return QS.parse(str, { ...defaultParseOptions, ...options }) as Record<string, any>
}
