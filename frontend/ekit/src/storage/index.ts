/**
 * localStorage 读写封装
 * 提供 JSON 自动序列化/反序列化和 Vue 响应式包装；业务不直接用 localStorage，统一走本模块避免序列化不一致
 */
import { ref, watch, type Ref } from 'vue'

/**
 * 响应式 localStorage composable，值变化时自动同步到 localStorage
 * 设为 null/undefined 会自动移除对应 key
 * @param key localStorage 键名
 * @param defaultValue 首次无值时的默认值
 * @returns 与 localStorage 双向绑定的 ref
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
 * localStorage 同步读写对象，支持 JSON 自动序列化
 * 写入时统一 JSON.stringify；读取时尝试 JSON.parse，失败退回原字符串（兼容历史非 JSON 字面量）
 */
export const storage = {
  /**
   * 读取指定 key 的值
   * @param key 键名
   * @param defaultValue 不存在时的默认值
   */
  get<T>(key: string, defaultValue?: T): T | undefined {
    const val = localStorage.getItem(key)
    if (val === null) return defaultValue
    try { return JSON.parse(val) } catch { return val as unknown as T }
  },
  /**
   * 写入值，自动 JSON 序列化
   * @param key 键名
   * @param value 要写入的值
   */
  set(key: string, value: any): void {
    localStorage.setItem(key, JSON.stringify(value))
  },
  /**
   * 删除指定 key
   */
  remove(key: string): void {
    localStorage.removeItem(key)
  },
  /**
   * 清空整个 localStorage（慎用，会清掉其他模块的数据）
   */
  clear(): void {
    localStorage.clear()
  },
}
