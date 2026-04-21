/**
 * ETree 树形组件类型定义
 */
import type { HTMLAttributes } from 'vue'

/** 树节点定义 */
export interface TreeNode {
  /** 唯一标识 */
  key: string | number
  /** 显示文本 */
  label: string
  /** 子节点（懒加载模式下未加载时为 undefined） */
  children?: TreeNode[]
  /** 是否禁用勾选/选择 */
  disabled?: boolean
  /** 懒加载模式标记：true 表示明确是叶子不再加载子节点 */
  isLeaf?: boolean
}

/** ETree Props */
export interface ETreeProps {
  /** 自定义类名 */
  class?: HTMLAttributes['class']
  /** 树数据 */
  data?: TreeNode[]
  /** 已勾选节点 key 数组，v-model 绑定 */
  modelValue?: (string | number)[]
  /** 是否显示复选框 */
  checkable?: boolean
  /** 已展开节点 key 数组，v-model:expandedKeys 绑定 */
  expandedKeys?: (string | number)[]
  /** 是否默认展开所有节点 */
  defaultExpandAll?: boolean
  /** 是否开启懒加载；开启时 children 未定义的节点会在展开时调用 loadFn */
  lazy?: boolean
  /** 懒加载用的异步函数，返回指定节点的子节点列表 */
  loadFn?: (node: TreeNode) => Promise<TreeNode[]>
  /** 是否允许拖拽重排 */
  draggable?: boolean
  /** 自定义过滤方法，返回 true 保留节点；配合 filterQuery 触发 */
  filterMethod?: (query: string, node: TreeNode) => boolean
  /** 当前过滤关键词 */
  filterQuery?: string
  /** true 时勾选父节点不级联子节点（互相独立） */
  checkStrictly?: boolean
}

/** ETree Emits */
export interface ETreeEmits {
  /** 勾选 key 变化，用于 v-model */
  (e: 'update:modelValue', keys: (string | number)[]): void
  /** 展开 key 变化，用于 v-model:expandedKeys */
  (e: 'update:expandedKeys', keys: (string | number)[]): void
  /** 单个节点勾选状态变化事件 */
  (e: 'check', key: string | number, checked: boolean): void
  /** 节点点击事件 */
  (e: 'select', key: string | number): void
  /** 拖拽完成事件，提供被拖/投放节点以及相对位置 */
  (e: 'node-drop', dragNode: TreeNode, dropNode: TreeNode, position: 'before' | 'inner' | 'after'): void
}
