import { ref, watch, type Ref } from 'vue'

/**
 * Reactive localStorage wrapper with JSON serialization.
 */
export function useStorage<T>(key: string, defaultValue: T): Ref<T> {
  const stored = localStorage.getItem(key)
  const data = ref<T>(stored ? JSON.parse(stored) : defaultValue) as Ref<T>

  watch(data, (val) => {
    if (val === null || val === undefined) {
      localStorage.removeItem(key)
    } else {
      localStorage.setItem(key, JSON.stringify(val))
    }
  }, { deep: true })

  return data
}

/**
 * Simple get/set/remove for localStorage with JSON support.
 */
export const storage = {
  get<T>(key: string, defaultValue?: T): T | undefined {
    const val = localStorage.getItem(key)
    if (val === null) return defaultValue
    try { return JSON.parse(val) } catch { return val as unknown as T }
  },
  set(key: string, value: any): void {
    localStorage.setItem(key, JSON.stringify(value))
  },
  remove(key: string): void {
    localStorage.removeItem(key)
  },
  clear(): void {
    localStorage.clear()
  },
}
