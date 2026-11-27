/** 列表动效的输入，排序和数据更新由调用方控制。 */
export interface EMotionListProps<T extends object> {
  /** 每条记录通过 itemKey 标识。 */
  items: readonly T[]
  /** 指向稳定、唯一且值为字符串或数字的字段，重排时保持不变。 */
  itemKey: {
    [K in keyof T]-?: T[K] extends string | number ? K : never
  }[keyof T]
}
