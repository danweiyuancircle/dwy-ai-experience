<!--
  列表关键词框。
  回车和按钮都只抛 search，不发请求。字数上限由页面按接口约束传入。
-->
<script setup lang="ts">
import { EButton, EInput } from '@dwydev/eui'
import { ref, useId } from 'vue'

defineOptions({ name: 'RecordSearch' })

const props = withDefaults(
  defineProps<{
    /** 当前关键词。示例：``'alice'``。 */
    modelValue: string
    /** 输入框提示。示例：``'用户名或邮箱'``。 */
    placeholder: string
    /** 持久输入标签；不传时使用 placeholder，视觉隐藏但仍供辅助技术读取。 */
    label?: string
    /** 最大字数。取值范围 ``[1, 500]``，与接口字段对齐。示例：``64``。 */
    maxlength: number
    /** 按钮文案。默认 ``'查询'``。示例：``'搜索'``。 */
    buttonText?: string
    /** 查询进行中时按钮转圈。 */
    loading?: boolean
    /** 输入框宽度类。默认 ``w-64``。示例：``'w-80'``。 */
    inputClass?: string
  }>(),
  { buttonText: '查询', loading: false, inputClass: 'w-64' },
)

const emit = defineEmits<{
  /** 输入变化。 */
  'update:modelValue': [value: string]
  /** 回车或点按钮。 */
  search: []
  /** 用户清空原有关键词。仅作状态通知；请求统一由 search 事件触发。 */
  clear: []
}>()

const inputId = `record-search-${useId()}`
const composing = ref(false)

/**
 * 输入框的值收成字符串再抛出。
 * @param value 输入框当前值。
 */
function onInput(value: string | number) {
  const keyword = String(value ?? '')
  emit('update:modelValue', keyword)
  // EInput 清空按钮也先抛 update，统一在此处理，避免 clear + update 发两次请求。
  if (keyword === '' && props.modelValue !== '') {
    emit('clear')
    emit('search')
  }
}

function onEnter(event: KeyboardEvent) {
  if (composing.value || event.isComposing || event.keyCode === 229) return
  emit('search')
}
</script>

<template>
  <label :for="inputId" class="sr-only">{{ label || placeholder || '搜索关键词' }}</label>
  <EInput
    :id="inputId"
    :model-value="modelValue"
    :class="inputClass"
    :placeholder="placeholder"
    :maxlength="maxlength"
    clearable
    @update:model-value="onInput"
    @compositionstart="composing = true"
    @compositionend="composing = false"
    @keydown.enter="onEnter"
  />
  <EButton size="sm" type="button" :loading="loading" @click="emit('search')">
    {{ buttonText }}
  </EButton>
</template>
