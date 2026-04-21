/**
 * Cookie 读写封装
 * 基于 js-cookie，提供 JSON 自动序列化/反序列化和 Vue 响应式包装
 * 业务不直接用 document.cookie 或 js-cookie，统一走本模块保证序列化一致
 */
import { ref, watch } from 'vue'
import type { Ref } from 'vue'
import Cookies from 'js-cookie'

/** Cookie 属性配置，透传自 js-cookie（如 expires、path、domain、secure、sameSite 等） */
export type CookieAttributes = Cookies.CookieAttributes

/**
 * Cookie 同步读写对象，支持 JSON 自动序列化
 * 非字符串值写入时自动 JSON.stringify，读取时尝试 JSON.parse（失败时按字符串返回）
 */
export const cookie = {
  /**
   * 读取指定 key 的 cookie 值
   * @param key cookie 键名
   * @returns 反序列化后的值，不存在时返回 undefined
   */
  get<T = string>(key: string): T | undefined {
    const value = Cookies.get(key)
    if (value === undefined) return undefined
    // 尝试按 JSON 解析，失败说明本身就是字符串字面量，直接返回原值
    try { return JSON.parse(value) as T } catch { return value as unknown as T }
  },
  /**
   * 写入 cookie；非字符串值会被 JSON.stringify
   * @param key cookie 键名
   * @param value 要写入的值
   * @param options cookie 属性（过期时间、作用域等）
   */
  set(key: string, value: any, options?: CookieAttributes): void {
    const v = typeof value === 'string' ? value : JSON.stringify(value)
    Cookies.set(key, v, options)
  },
  /**
   * 删除指定 cookie
   * @param key cookie 键名
   * @param options 删除时需匹配 path/domain（与写入时保持一致）
   */
  remove(key: string, options?: CookieAttributes): void {
    Cookies.remove(key, options)
  },
}

/**
 * 响应式 cookie composable，值变化时自动同步到 cookie
 * 设为 null/undefined 会自动删除 cookie
 * @param key cookie 键名
 * @param defaultValue cookie 不存在时的默认值
 * @returns 与 cookie 双向绑定的 ref
 */
export function useCookie<T = string>(key: string, defaultValue?: T): Ref<T | undefined> {
  const data = ref<T | undefined>(cookie.get<T>(key) ?? defaultValue) as Ref<T | undefined>

  watch(data, (val) => {
    if (val === undefined || val === null) {
      cookie.remove(key)
    } else {
      cookie.set(key, val)
    }
  }, { deep: true })

  return data
}
