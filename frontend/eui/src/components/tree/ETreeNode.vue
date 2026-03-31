<script setup lang="ts">
import { ChevronRight } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { TreeNode } from './types'

const props = defineProps<{
  node: TreeNode
  checkedKeys: (string | number)[]
  expandedKeys: (string | number)[]
  checkable: boolean
  depth: number
}>()

const emit = defineEmits<{
  (e: 'toggle-expand', key: string | number): void
  (e: 'toggle-check', key: string | number): void
  (e: 'select', key: string | number): void
}>()

const isExpanded = () => props.expandedKeys.includes(props.node.key)
const isChecked = () => props.checkedKeys.includes(props.node.key)
const hasChildren = () => !!props.node.children?.length
</script>

<template>
  <li :class="cn('select-none')">
    <!-- Node row -->
    <div
      :class="cn(
        'flex items-center gap-1 rounded-sm px-2 py-1 text-sm cursor-pointer',
        'hover:bg-accent hover:text-accent-foreground',
        node.disabled && 'pointer-events-none opacity-50',
      )"
      :style="{ paddingLeft: `${depth * 16 + 8}px` }"
      @click="$emit('select', node.key)"
    >
      <!-- Expand toggle -->
      <button
        v-if="hasChildren()"
        class="shrink-0 rounded-sm p-0.5 hover:bg-accent"
        @click.stop="$emit('toggle-expand', node.key)"
      >
        <ChevronRight
          :class="cn('size-3.5 transition-transform', isExpanded() && 'rotate-90')"
        />
      </button>
      <span v-else class="w-5 shrink-0" />

      <!-- Checkbox -->
      <input
        v-if="checkable"
        type="checkbox"
        :checked="isChecked()"
        :disabled="node.disabled"
        class="size-4 shrink-0 rounded border-input accent-primary"
        @click.stop
        @change="$emit('toggle-check', node.key)"
      />

      <!-- Label -->
      <span class="flex-1 truncate">{{ node.label }}</span>
    </div>

    <!-- Children (recursive) -->
    <ul v-if="hasChildren() && isExpanded()" class="list-none">
      <ETreeNode
        v-for="child in node.children"
        :key="child.key"
        :node="child"
        :checked-keys="checkedKeys"
        :expanded-keys="expandedKeys"
        :checkable="checkable"
        :depth="depth + 1"
        @toggle-expand="$emit('toggle-expand', $event)"
        @toggle-check="$emit('toggle-check', $event)"
        @select="$emit('select', $event)"
      />
    </ul>
  </li>
</template>
