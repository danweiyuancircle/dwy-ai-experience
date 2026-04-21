/**
 * ECommand 命令面板组件的上下文定义
 * 提供根组件向子组件（Item / Group / Input / Empty）传递搜索与过滤状态的能力
 */
import type { Ref } from 'vue'
import { createContext } from 'reka-ui'

/**
 * 根 Command 上下文：维护全量条目、分组映射与搜索过滤状态
 */
export const [useCommand, provideCommandContext] = createContext<{
  /** 所有 item 的 id → 文本内容映射 */
  allItems: Ref<Map<string, string>>
  /** 所有 group 的 id → 包含 item id 集合映射 */
  allGroups: Ref<Map<string, Set<string>>>
  /** 当前搜索值与过滤结果 */
  filterState: {
    search: string
    filtered: { count: number; items: Map<string, number>; groups: Set<string> }
  }
}>('ECommand')

/**
 * CommandGroup 上下文：仅暴露 group id，供 Item 挂靠所属分组
 */
export const [useCommandGroup, provideCommandGroupContext] = createContext<{
  /** 当前分组的唯一 id */
  id?: string
}>('ECommandGroup')
