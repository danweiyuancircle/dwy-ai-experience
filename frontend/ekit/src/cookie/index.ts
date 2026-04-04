import { ref, watch } from 'vue'
import type { Ref } from 'vue'
import Cookies from 'js-cookie'
import type { CookieAttributes } from 'js-cookie'

export type { CookieAttributes }

/**
 * Simple get/set/remove for cookies with JSON support.
 */
export const cookie = {
  get<T = string>(key: string): T | undefined {
    const value = Cookies.get(key)
    if (value === undefined) return undefined
    try { return JSON.parse(value) as T } catch { return value as unknown as T }
  },
  set(key: string, value: any, options?: CookieAttributes): void {
    const v = typeof value === 'string' ? value : JSON.stringify(value)
    Cookies.set(key, v, options)
  },
  remove(key: string, options?: CookieAttributes): void {
    Cookies.remove(key, options)
  },
}

/**
 * Reactive cookie wrapper with JSON serialization.
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
