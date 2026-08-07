<!--
  ETreeSelect 树形下拉选择器
  下拉框展开后呈现 ETree，支持单选（select）、多选（multiple）、勾选（checkable）三种模式
  触发器显示所选节点 label，多个值用逗号分隔
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronDown, X } from 'lucide-vue-next'
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import ETree from '../tree/ETree.vue'
import type { TreeNode } from '../tree/types'
import type { ETreeSelectProps, ETreeSelectEmits } from './types'

const props = withDefaults(defineProps<ETreeSelectProps>(), {
  data: () => [],
  placeholder: 'Select...',
  multiple: false,
  checkable: false,
  disabled: false,
})

const emit = defineEmits<ETreeSelectEmits>()

const open = ref(false)

/** 将树扁平化为 key → label 映射，用于触发器显示文本 */
function buildLabelMap(nodes: TreeNode[], map: Map<string | number, string> = new Map()): Map<string | number, string> {
  for (const node of nodes) {
    map.set(node.key, node.label)
    if (node.children) buildLabelMap(node.children, map)
  }
  return map
}

const labelMap = computed(() => buildLabelMap(props.data))

const checkedKeys = computed((): (string | number)[] => {
  if (!props.modelValue) return []
  return Array.isArray(props.modelValue) ? props.modelValue : [props.modelValue]
})

const displayText = computed(() => {
  if (!props.modelValue || (Array.isArray(props.modelValue) && props.modelValue.length === 0)) return ''
  const keys = checkedKeys.value
  return keys.map((k) => labelMap.value.get(k) ?? String(k)).join(', ')
})

function onCheck(keys: (string | number)[]) {
  if (props.multiple || props.checkable) {
    emit('update:modelValue', keys)
    emit('change', keys)
  }
}

function onSelect(key: string | number) {
  if (!props.multiple && !props.checkable) {
    emit('update:modelValue', key)
    emit('change', key)
    open.value = false
  }
}

function onClear(e: MouseEvent) {
  e.stopPropagation()
  emit('update:modelValue', props.multiple ? [] : undefined)
  emit('change', props.multiple ? [] : undefined)
}
</script>

<template>
  <PopoverRoot v-model:open="open">
    <PopoverTrigger as-child>
      <button
        :disabled="disabled"
        :class="cn(
          'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs transition-[color,box-shadow]',
          'outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
          'disabled:cursor-not-allowed disabled:opacity-50',
          !displayText && 'text-muted-foreground',
          props.class,
        )"
      >
        <span class="flex-1 truncate text-left">{{ displayText || placeholder }}</span>
        <div class="flex items-center gap-1">
          <X
            v-if="displayText"
            class="size-4 opacity-50 hover:opacity-100"
            @click.stop="onClear"
          />
          <ChevronDown class="size-4 opacity-50" />
        </div>
      </button>
    </PopoverTrigger>

    <PopoverPortal>
      <PopoverContent
        :side-offset="4"
        align="start"
        :class="cn(
          'z-50 min-w-[200px] rounded-md border bg-popover p-1 text-popover-foreground shadow-md outline-none',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
          'max-h-[300px] overflow-y-auto',
        )"
      >
        <ETree
          :data="data"
          :model-value="checkedKeys"
          :checkable="checkable || multiple"
          default-expand-all
          @update:model-value="onCheck"
          @select="onSelect"
        />
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
