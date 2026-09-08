/**
 * 表单字段 composable
 * 读 EFormItem provide 的 id / name / 校验错误，给控件补 aria。
 * 不走 vee-validate FormField：eui 字段注册在 EFormItem 的 useField 上。
 * 控件在表单外使用时返回 null，不抛错。
 */
import { inject } from 'vue'
import type { ComputedRef, InjectionKey } from 'vue'

/** EFormItem 向下注入的字段上下文 */
export interface FormFieldContext {
  /** FormItem 实例 id，拼 aria id */
  id: string
  /** 对应 model 的字段名（prop） */
  name?: string
  /** 当前校验错误文案 */
  error: ComputedRef<string | undefined>
}

/** EFormItem 向下注入的 key */
export const FORM_ITEM_INJECTION_KEY = Symbol() as InjectionKey<FormFieldContext>

/**
 * 读取所属 EFormItem 上下文。
 * @returns 在 FormItem 内返回 aria id 与错误；独立使用控件时为 null
 */
export function useFormField(): {
  id: string
  name?: string
  formItemId: string
  formDescriptionId: string
  formMessageId: string
  error: ComputedRef<string | undefined>
} | null {
  const ctx = inject(FORM_ITEM_INJECTION_KEY, null)
  if (!ctx) return null

  return {
    id: ctx.id,
    name: ctx.name,
    formItemId: `${ctx.id}-form-item`,
    formDescriptionId: `${ctx.id}-form-item-description`,
    formMessageId: `${ctx.id}-form-item-message`,
    error: ctx.error,
  }
}
