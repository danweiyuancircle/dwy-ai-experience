/**
 * EAccordion 折叠面板组件的类型定义
 * 描述折叠项配置、Props、Emits 等类型契约
 */
import type { HTMLAttributes } from 'vue'

/**
 * 折叠项配置
 */
export interface AccordionItemOption {
  /** 唯一标识，对应 modelValue 中的值 */
  key: string
  /** 折叠项标题文本 */
  title: string
  /** 是否禁用该折叠项 */
  disabled?: boolean
}

/**
 * EAccordion 折叠面板 Props
 */
export interface EAccordionProps {
  /** 自定义 class，透传到根元素 */
  class?: HTMLAttributes['class']
  /** 当前展开项的 key，multiple 模式下为数组 */
  modelValue?: string | string[]
  /** 折叠项数据源，为空时渲染默认插槽 */
  items?: AccordionItemOption[]
  /** 是否允许多项同时展开 */
  multiple?: boolean
  /** 单选模式下是否允许收起所有项 */
  collapsible?: boolean
}

/**
 * EAccordion 折叠面板事件
 */
export interface EAccordionEmits {
  /** 展开项变化时触发 */
  (e: 'update:modelValue', value: string | string[] | undefined): void
}
