/**
 * 表单字段 composable
 * 桥接 vee-validate 的 FieldContext 与 EFormItem 注入的 id，
 * 供控件组件生成 aria id、读取校验状态、展示错误信息
 */
import { FieldContextKey } from 'vee-validate'
import { computed, inject } from 'vue'
import type { InjectionKey } from 'vue'

/** EFormItem 向下注入的 field id（用于生成 aria 关联属性） */
export const FORM_ITEM_INJECTION_KEY = Symbol() as InjectionKey<string>

/**
 * 获取表单字段上下文（必须包裹在 vee-validate 的 <FormField> 内部使用）
 * @returns 字段 id、name、aria 相关 id、校验/脏值/触碰状态及错误信息
 * @throws 未包裹在 FormField 内时抛错，避免静默失效
 */
export function useFormField() {
  const fieldContext = inject(FieldContextKey)
  const fieldItemContext = inject(FORM_ITEM_INJECTION_KEY)

  if (!fieldContext)
    throw new Error('useFormField should be used within <FormField>')

  const { name, errorMessage: error, meta } = fieldContext
  const id = fieldItemContext

  return {
    id,
    name,
    formItemId: `${id}-form-item`,
    formDescriptionId: `${id}-form-item-description`,
    formMessageId: `${id}-form-item-message`,
    valid: computed(() => meta.valid),
    isDirty: computed(() => meta.dirty),
    isTouched: computed(() => meta.touched),
    error,
  }
}
