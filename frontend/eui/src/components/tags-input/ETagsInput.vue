<!--
  ETagsInput 标签输入组件
  基于 reka-ui TagsInput 封装，回车分词为标签
  重复添加触发 invalid 事件时，在底部显示 2 秒错误提示
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { X } from 'lucide-vue-next'
import {
  TagsInputRoot,
  TagsInputItem,
  TagsInputItemDelete,
  TagsInputItemText,
  TagsInputInput,
} from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ETagsInputProps, ETagsInputEmits } from './types'

const props = withDefaults(defineProps<ETagsInputProps>(), {
  modelValue: () => [],
  disabled: false,
})

const emit = defineEmits<ETagsInputEmits>()

const invalidMessage = ref('')
let invalidTimer: ReturnType<typeof setTimeout> | null = null

const inputSizeClass = computed(() => {
  if (props.size === 'sm') return 'text-xs min-h-8'
  if (props.size === 'lg') return 'text-base min-h-10'
  return 'text-sm min-h-9'
})

function onUpdate(value: string[]) {
  emit('update:modelValue', value)
  emit('change', value)
}

/**
 * 重复添加时显示临时错误提示，2 秒后自动清除
 */
function onInvalid(payload: string) {
  invalidMessage.value = `"${payload}" 已存在`
  if (invalidTimer) clearTimeout(invalidTimer)
  invalidTimer = setTimeout(() => {
    invalidMessage.value = ''
  }, 2000)
}
</script>

<template>
  <TagsInputRoot
    data-slot="tags-input"
    :model-value="modelValue"
    :max="max"
    :disabled="disabled"
    :class="cn(
      'flex flex-wrap gap-2 items-center rounded-md border border-input bg-background px-2 py-1 shadow-xs transition-[color,box-shadow] outline-none',
      'focus-within:border-ring focus-within:ring-ring/50 focus-within:ring-[3px]',
      'aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 aria-invalid:border-destructive',
      inputSizeClass,
      props.class,
    )"
    @update:model-value="onUpdate"
    @invalid="onInvalid"
  >
    <TagsInputItem
      v-for="item in modelValue"
      :key="item"
      :value="item"
      class="flex h-5 items-center rounded-md bg-secondary data-[state=active]:ring-ring/50 data-[state=active]:ring-[3px]"
    >
      <TagsInputItemText class="py-0.5 px-2 text-sm rounded bg-transparent" />
      <TagsInputItemDelete class="flex rounded bg-transparent mr-1">
        <X class="w-3 h-3" />
      </TagsInputItemDelete>
    </TagsInputItem>
    <TagsInputInput
      :placeholder="placeholder"
      class="text-sm min-h-5 focus:outline-none flex-1 bg-transparent px-1"
    />
  </TagsInputRoot>
  <p v-if="invalidMessage" class="mt-1 text-xs text-destructive">{{ invalidMessage }}</p>
</template>
