/**
 * ESelect 下拉选择器组件类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Size, Option, GroupedOption } from '@/types'

/** ESelect Props */
export interface ESelectProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 当前选中值；多选模式下为数组 */
  modelValue?: string | number | (string | number)[]
  /** 选项列表，可传扁平数组或带分组的数组 */
  options?: Option[] | GroupedOption[]
  /** 占位文本 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 尺寸变体 */
  size?: Size
  /** 是否显示清除按钮 */
  clearable?: boolean
  /** 选项对象中代表值的字段名，默认 'value' */
  valueKey?: string
  /** 选项对象中代表文本的字段名，默认 'label' */
  labelKey?: string
  /** 是否可搜索（下拉顶部显示搜索框） */
  filterable?: boolean
  /** 是否多选（modelValue 为数组） */
  multiple?: boolean
  /** 多选时是否折叠标签为「第一个 + N」形式 */
  collapseTags?: boolean
  /** 是否启用远程搜索；配合 remoteMethod 使用，禁用本地过滤 */
  remote?: boolean
  /** 远程搜索回调，外部据此更新 options */
  remoteMethod?: (query: string) => Promise<void>
  /** 下拉 loading 状态，远程加载时显示旋转指示器 */
  loading?: boolean
}

/** ESelect Emits */
export interface ESelectEmits {
  /** 值变更，用于 v-model */
  'update:modelValue': [value: string | number | (string | number)[] | undefined]
  /** 值变化事件 */
  change: [value: string | number | (string | number)[] | undefined]
  /** 下拉显示/隐藏变化事件 */
  'visible-change': [visible: boolean]
}
