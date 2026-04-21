/**
 * EForm 表单组件族的类型定义
 */
import type { HTMLAttributes } from 'vue'
import type { Size, FormRule } from '@/types'
import type { ZodType } from 'zod'

/**
 * EForm 表单 Props
 */
export interface EFormProps {
  /** 自定义 class，透传到 <form> 元素 */
  class?: HTMLAttributes['class']
  /** 表单数据模型，响应式对象 */
  // 表单模型形状由业务决定
  model?: Record<string, any>
  /** 校验规则：可传 zod schema 或"字段 → 规则"映射 */
  rules?: ZodType | Record<string, FormRule | FormRule[]>
  /** label 固定宽度 */
  labelWidth?: string
  /** label 对齐位置 */
  labelPosition?: 'left' | 'right' | 'top'
  /** 子组件默认尺寸 */
  size?: Size
  /** 是否禁用整个表单 */
  disabled?: boolean
  /** 是否行内布局（多字段横向排列） */
  inline?: boolean
}

/**
 * EForm 表单事件
 */
export interface EFormEmits {
  /** 校验通过并提交时触发，携带当前表单值 */
  submit: [values: Record<string, any>]
}

/**
 * EForm 表单对外暴露的实例方法
 */
export interface EFormExpose {
  /** 触发整体校验，返回是否通过 */
  validate: () => Promise<boolean>
  /** 触发单字段校验 */
  validateField: (name: string) => Promise<boolean>
  /** 重置表单字段为初始值 */
  resetFields: () => void
  /** 清空所有校验错误 */
  clearValidate: () => void
}

/**
 * EFormItem 表单字段 Props
 */
export interface EFormItemProps {
  /** 自定义 class */
  class?: HTMLAttributes['class']
  /** label 文本 */
  label?: string
  /** 对应 model 中的字段名，用于绑定校验 */
  prop?: string
  /** 是否必填（仅显示红星，不替代 rules） */
  required?: boolean
  /** 局部 label 宽度覆盖 */
  labelWidth?: string
}
