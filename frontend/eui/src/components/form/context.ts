/**
 * EForm 表单的跨组件上下文定义
 * EForm 通过 provide 向子级 EFormItem 注入布局/模型/禁用等共享配置
 */
import type { InjectionKey, Ref } from 'vue'

/**
 * EForm 向下注入的上下文
 */
export interface FormContext {
  /** label 宽度（字符串 CSS 值），provide 后子组件可覆盖 */
  labelWidth?: Ref<string | undefined>
  /** label 对齐位置 */
  labelPosition: Ref<'left' | 'right' | 'top'>
  /** 默认尺寸 */
  size: Ref<string>
  /** 是否整表禁用 */
  disabled: Ref<boolean>
  /** 共享的表单数据模型 */
  // 表单模型形状由业务决定
  model: Ref<Record<string, any> | undefined>
}

/** FormContext 的 InjectionKey */
export const FORM_CONTEXT_KEY = Symbol() as InjectionKey<FormContext>
