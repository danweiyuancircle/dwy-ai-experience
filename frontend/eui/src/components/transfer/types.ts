/**
 * ETransfer 穿梭框组件类型定义
 */

/** 穿梭框单项数据 */
export interface TransferItem {
  /** 显示文本 */
  label: string
  /** 唯一值 */
  value: string | number
  /** 是否禁用该项（不可勾选/移动） */
  disabled?: boolean
}

/** ETransfer Props */
export interface ETransferProps {
  /** 自定义类名 */
  class?: string
  /** 右侧（已选择）的 value 数组，v-model 绑定 */
  modelValue?: (string | number)[]
  /** 全部候选项的数据源 */
  data?: TransferItem[]
  /** 是否显示搜索框 */
  filterable?: boolean
  /** 左右两列的标题 [左, 右] */
  titles?: [string, string]
}

/** ETransfer Emits */
export interface ETransferEmits {
  /** 右侧已选 value 数组更新，用于 v-model */
  (e: 'update:modelValue', value: (string | number)[]): void
  /** 变更事件：返回最终值、移动方向及本次被移动的 value */
  (e: 'change', value: (string | number)[], direction: 'right' | 'left', moved: (string | number)[]): void
}
