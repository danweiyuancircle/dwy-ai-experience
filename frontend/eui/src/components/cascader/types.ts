/**
 * ECascader 级联选择器组件的类型定义
 */
import type { HTMLAttributes } from 'vue'

/**
 * 级联选项节点
 */
export interface CascaderOption {
  /** 显示文本 */
  label: string
  /** 唯一值 */
  value: string | number
  /** 子节点数组，不存在表示叶子或待 lazy 加载 */
  children?: CascaderOption[]
  /** 是否禁用该节点 */
  disabled?: boolean
  /** lazy 模式下显式标记为叶子节点，避免展开时触发加载 */
  isLeaf?: boolean
}

/**
 * ECascader 级联选择器 Props
 */
export interface ECascaderProps {
  /** 自定义 class，透传到触发按钮 */
  class?: HTMLAttributes['class']
  /** 选中值：单选为路径数组，多选为路径数组的数组 */
  modelValue?: (string | number)[] | (string | number)[][]
  /** 级联数据源 */
  options?: CascaderOption[]
  /** 占位文本 */
  placeholder?: string
  /** 是否禁用 */
  disabled?: boolean
  /** 是否显示清空按钮 */
  clearable?: boolean
  /** 是否启用搜索过滤 */
  filterable?: boolean
  /** 懒加载模式：children 为 undefined 的节点展开时触发 loadFn */
  lazy?: boolean
  /** 懒加载用的子节点获取函数 */
  loadFn?: (option: CascaderOption) => Promise<CascaderOption[]>
  /** 是否启用多选，modelValue 变为路径数组的数组 */
  multiple?: boolean
  /** 多选模式下是否折叠多余 tag 为 "+N" */
  collapseTags?: boolean
}

/**
 * ECascader 级联选择器事件
 */
export interface ECascaderEmits {
  /** 选中路径变化 */
  (e: 'update:modelValue', value: (string | number)[] | (string | number)[][]): void
  /** 业务 change 事件（与 update:modelValue 并发） */
  (e: 'change', value: (string | number)[] | (string | number)[][]): void
}
