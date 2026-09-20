<!--
  EForm 表单组件
  基于 vee-validate + zod 实现，rules 同时支持 zod schema 与"字段 → 规则"映射
  通过 provide 向下分发 labelWidth / labelPosition / disabled 等布局配置
  暴露 validate / validateField / resetFields / clearValidate 四个实例方法
-->
<script setup lang="ts">
import { provide, computed, toRef } from 'vue'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { cn } from '@/utils/cn'
import { FORM_CONTEXT_KEY } from './context'
import type { EFormProps, EFormEmits, EFormExpose } from './types'
import type { FormRule } from '@/types'
import type { ZodType } from 'zod'

const props = withDefaults(defineProps<EFormProps>(), {
  labelPosition: 'right',
  size: 'default',
  disabled: false,
  inline: false,
})

const emit = defineEmits<EFormEmits>()

// 通过是否存在 _def 属性判断 rules 是否为 zod schema
const isZodSchema = computed(() => {
  if (!props.rules) return false
  return typeof (props.rules as ZodType)._def !== 'undefined'
})

/**
 * 把业务校验返回值收成 vee-validate 认的 `true | string`。
 * vee-validate 把非 string 的 truthy 当通过，直接 return Error 会静默成功。
 */
function toVeeValidateResult(raw: unknown, fallback?: string): true | string {
  if (raw === true || raw === undefined || raw === null) return true
  if (raw === false) return fallback || '校验失败'
  if (typeof raw === 'string') return raw || fallback || '校验失败'
  if (raw instanceof Error) return raw.message || fallback || '校验失败'
  return true
}

/**
 * 跑自定义 validator：同步 return、callback、Promise 三种 Element Plus 写法都收。
 */
function runCustomValidator(rule: FormRule, value: unknown): Promise<true | string> {
  return new Promise((resolve) => {
    let settled = false
    const finish = (raw: unknown) => {
      if (settled) return
      settled = true
      resolve(toVeeValidateResult(raw, rule.message))
    }
    try {
      const ret = rule.validator!(rule, value, (err?: Error) => {
        finish(err ?? true)
      })
      if (ret instanceof Promise) {
        void ret.then(
          (resolved) => finish(resolved === undefined ? true : resolved),
          (err: unknown) => finish(err),
        )
        return
      }
      if (ret !== undefined) finish(ret)
    } catch (err) {
      finish(err)
    }
  })
}

/**
 * 将单个 FormRule 转换为 vee-validate 可识别的校验函数。
 * 支持 required / min / max / type=email / pattern / 自定义 validator。
 */
function ruleToValidator(rule: FormRule) {
  return (value: unknown) => {
    if (rule.required && (value === undefined || value === null || value === '')) {
      return rule.message || '此字段为必填项'
    }
    if (typeof value === 'string') {
      if (rule.min !== undefined && value.length < rule.min) {
        return rule.message || `最少 ${rule.min} 个字符`
      }
      if (rule.max !== undefined && value.length > rule.max) {
        return rule.message || `最多 ${rule.max} 个字符`
      }
    }
    if (rule.type === 'email' && value) {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(String(value))) {
        return rule.message || '请输入有效的邮箱地址'
      }
    }
    if (rule.pattern && value && !rule.pattern.test(String(value))) {
      return rule.message || '格式不正确'
    }
    if (rule.validator) {
      return runCustomValidator(rule, value)
    }
    return true
  }
}

/**
 * 将"字段 → 规则"映射构建为 vee-validate 兼容的字段级校验 schema。
 * 组合函数必须 async：自定义 validator 可能返回 Promise。
 */
function buildPlainSchema(rules: Record<string, FormRule | FormRule[]>) {
  const schema: Record<string, (value: unknown) => Promise<true | string>> = {}
  for (const [field, fieldRules] of Object.entries(rules)) {
    const ruleArray = Array.isArray(fieldRules) ? fieldRules : [fieldRules]
    const validators = ruleArray.map(ruleToValidator)
    schema[field] = async (value: unknown) => {
      for (const validator of validators) {
        const result = await validator(value)
        if (result !== true) return result
      }
      return true
    }
  }
  return schema
}

// 统一 rules 为 vee-validate schema（zod 走 toTypedSchema，其他走字段级校验）
const validationSchema = computed(() => {
  if (!props.rules) return undefined
  if (isZodSchema.value) {
    return toTypedSchema(props.rules as ZodType)
  }
  return buildPlainSchema(props.rules as Record<string, FormRule | FormRule[]>)
})

// 深拷贝初始值快照，保证 resetFields 能恢复到表单挂载时的状态
const initialSnapshot = JSON.parse(JSON.stringify(props.model ?? {}))

const { handleSubmit, resetForm, setErrors, validate: veeValidate, validateField: veeValidateField, setFieldValue } = useForm({
  validationSchema,
  initialValues: initialSnapshot,
  // 进页空表不能出红字；提交 / 值变化再校
  validateOnMount: false,
})

const onSubmit = handleSubmit((values) => {
  emit('submit', values)
})

/** 整体校验表单，返回是否通过 */
async function validate(): Promise<boolean> {
  const result = await veeValidate()
  return result.valid
}

/** 单字段校验 */
async function validateField(name: string): Promise<boolean> {
  const result = await veeValidateField(name)
  return result.valid
}

/**
 * 重置字段为初始值：同时同步外部 model，避免 v-model 绑定的响应式对象脱节
 */
function resetFields() {
  resetForm({ values: JSON.parse(JSON.stringify(initialSnapshot)) })
  if (props.model) {
    for (const key of Object.keys(initialSnapshot)) {
      props.model[key] = initialSnapshot[key]
    }
  }
}

/** 清空所有字段的校验错误 */
function clearValidate() {
  setErrors({})
}

provide(FORM_CONTEXT_KEY, {
  labelWidth: toRef(() => props.labelWidth),
  labelPosition: toRef(() => props.labelPosition),
  size: toRef(() => props.size),
  disabled: toRef(() => props.disabled),
  model: toRef(() => props.model),
})

defineExpose<EFormExpose>({
  validate,
  validateField,
  resetFields,
  clearValidate,
})
</script>

<template>
  <form
    data-slot="form"
    :class="cn(
      props.inline ? 'flex flex-wrap gap-4 items-start' : 'space-y-4',
      props.class,
    )"
    @submit.prevent="onSubmit"
  >
    <slot />
  </form>
</template>
