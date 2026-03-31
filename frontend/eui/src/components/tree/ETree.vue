<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { cn } from '@/utils/cn'
import type { ETreeProps, ETreeEmits, TreeNode } from './types'
import ETreeNode from './ETreeNode.vue'

const props = withDefaults(defineProps<ETreeProps>(), {
  data: () => [],
  modelValue: () => [],
  checkable: false,
  expandedKeys: () => [],
  defaultExpandAll: false,
})

const emit = defineEmits<ETreeEmits>()

/** Collect all keys recursively */
function getAllKeys(nodes: TreeNode[]): (string | number)[] {
  return nodes.flatMap((n) => [n.key, ...getAllKeys(n.children ?? [])])
}

const internalExpandedKeys = ref<(string | number)[]>([])

onMounted(() => {
  if (props.defaultExpandAll) {
    internalExpandedKeys.value = getAllKeys(props.data)
  } else {
    internalExpandedKeys.value = [...props.expandedKeys]
  }
})

watch(() => props.expandedKeys, (val) => {
  internalExpandedKeys.value = [...val]
})

function toggleExpand(key: string | number) {
  const idx = internalExpandedKeys.value.indexOf(key)
  if (idx >= 0) {
    internalExpandedKeys.value.splice(idx, 1)
  } else {
    internalExpandedKeys.value.push(key)
  }
  emit('update:expandedKeys', [...internalExpandedKeys.value])
}

function toggleCheck(key: string | number) {
  const current = [...(props.modelValue ?? [])]
  const idx = current.indexOf(key)
  let isChecked: boolean
  if (idx >= 0) {
    current.splice(idx, 1)
    isChecked = false
  } else {
    current.push(key)
    isChecked = true
  }
  emit('update:modelValue', current)
  emit('check', key, isChecked)
}

function onSelect(key: string | number) {
  emit('select', key)
}
</script>

<template>
  <ul
    data-slot="tree"
    :class="cn('list-none space-y-0.5', props.class)"
    role="tree"
  >
    <ETreeNode
      v-for="node in data"
      :key="node.key"
      :node="node"
      :checked-keys="modelValue ?? []"
      :expanded-keys="internalExpandedKeys"
      :checkable="checkable"
      :depth="0"
      @toggle-expand="toggleExpand"
      @toggle-check="toggleCheck"
      @select="onSelect"
    />
  </ul>
</template>
