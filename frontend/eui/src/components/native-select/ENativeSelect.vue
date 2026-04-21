<!--
  ENativeSelect 原生 Select 下拉组件
  基于浏览器原生 <select> 封装，保留操作系统样式的下拉体验，比 ESelect 更轻量
  适用于移动端或不需要自定义选项样式的场景
-->
<script setup lang="ts">
import { ChevronDown } from 'lucide-vue-next'
import { useVModel } from '@vueuse/core'
import { cn } from '@/utils/cn'
import type { ENativeSelectProps, ENativeSelectEmits } from './types'

const props = withDefaults(defineProps<ENativeSelectProps>(), {
  options: () => [],
  disabled: false,
})

const emit = defineEmits<ENativeSelectEmits>()

const modelValue = useVModel(props, 'modelValue', emit, {
  passive: true,
  defaultValue: '',
})

function handleChange(event: Event) {
  emit('change', event)
}
</script>

<template>
  <div
    class="group/native-select relative w-fit has-[select:disabled]:opacity-50"
    data-slot="native-select-wrapper"
  >
    <select
      v-model="modelValue"
      data-slot="native-select"
      :disabled="props.disabled"
      :class="cn(
        'border-input placeholder:text-muted-foreground dark:bg-input/30 h-9 w-full min-w-0 appearance-none rounded-md border bg-transparent px-3 py-2 pr-9 text-sm shadow-xs transition-[color,box-shadow] outline-none disabled:pointer-events-none disabled:cursor-not-allowed',
        'focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
        props.class,
      )"
      @change="handleChange"
    >
      <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
      <slot />
    </select>
    <ChevronDown
      class="text-muted-foreground pointer-events-none absolute top-1/2 right-3.5 size-4 -translate-y-1/2 opacity-50 select-none"
      aria-hidden="true"
      data-slot="native-select-icon"
    />
  </div>
</template>
