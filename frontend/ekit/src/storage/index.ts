/**
 * localStorage 读写封装
 * useStorage 直接再导出 @vueuse/core 的实现：自动 JSON 序列化、跨标签页同步、SSR-safe
 * 静态 storage 对象保留用于非组件场景，内部走原生 localStorage + JSON
 */
export { useStorage } from '@vueuse/core'

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
