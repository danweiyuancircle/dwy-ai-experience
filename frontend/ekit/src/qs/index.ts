/**
 * 查询字符串序列化/反序列化封装
 * 基于 qs；设置项目统一默认值（数组用 repeat 格式、parse 时自动剥去前导 '?'），避免各处配置不一致
 */
import QS from 'qs'
import type { IStringifyOptions, IParseOptions } from 'qs'

export type { IStringifyOptions, IParseOptions }

/** stringify 默认配置：数组重复 key、不自动拼 ? 前缀 */
const defaultStringifyOptions: IStringifyOptions = {
  arrayFormat: 'repeat',
  addQueryPrefix: false,
}

/** parse 默认配置：自动忽略前导 '?' */
const defaultParseOptions: IParseOptions = {
  ignoreQueryPrefix: true,
}

/**
 * 对象序列化为查询字符串
 * @param obj 待序列化的对象
 * @param options 覆盖默认 qs 选项（合并而非替换）
 * @returns 查询字符串，如 'a=1&b=2'
 */
export function stringify(obj: Record<string, any>, options?: IStringifyOptions): string {
  return QS.stringify(obj, { ...defaultStringifyOptions, ...options })
}

/**
 * 查询字符串解析为对象
 * @param str 查询字符串（可带或不带前导 '?'）
 * @param options 覆盖默认 qs 选项（合并而非替换）
 * @returns 解析后的对象
 */
export function parse(str: string, options?: IParseOptions): Record<string, any> {
  return QS.parse(str, { ...defaultParseOptions, ...options }) as Record<string, any>
}
