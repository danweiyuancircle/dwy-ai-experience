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

/** Flatten tree to label map */
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
          'flex h-9 w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs',
          'focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2',
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
