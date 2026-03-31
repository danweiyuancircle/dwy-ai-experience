<script setup lang="ts">
import { ref, computed } from 'vue'
import { ChevronRight, LoaderCircle, Minus } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { TreeNode } from './types'

const props = defineProps<{
  node: TreeNode
  checkedKeys: (string | number)[]
  expandedKeys: (string | number)[]
  checkable: boolean
  depth: number
  lazy: boolean
  loadingKeys: Set<string | number>
  draggableTree: boolean
  dragNodeKey: string | number | null
  dropNodeKey: string | number | null
  dropPosition: 'before' | 'inner' | 'after' | null
  visibleKeys: Set<string | number> | null
  checkStrictly: boolean
  internalData: TreeNode[]
}>()

const emit = defineEmits<{
  (e: 'toggle-expand', key: string | number): void
  (e: 'toggle-check', key: string | number): void
  (e: 'select', key: string | number): void
  (e: 'drag-start', key: string | number): void
  (e: 'drag-over', key: string | number, position: 'before' | 'inner' | 'after'): void
  (e: 'drag-end'): void
}>()

const isExpanded = () => props.expandedKeys.includes(props.node.key)
const isChecked = () => props.checkedKeys.includes(props.node.key)
const isLoading = () => props.loadingKeys.has(props.node.key)

const hasChildren = () => {
  if (props.lazy) {
    // In lazy mode, show expand arrow for nodes that are not explicitly leaf
    // and either have children loaded or have undefined children (not yet loaded)
    if (props.node.isLeaf) return false
    return props.node.children === undefined || (props.node.children?.length ?? 0) > 0
  }
  return !!props.node.children?.length
}

const hasLoadedChildren = () => !!props.node.children?.length

/** Determine if node is visible based on filter */
const isVisible = computed(() => {
  if (!props.visibleKeys) return true
  return props.visibleKeys.has(props.node.key)
})

// --- Indeterminate (half-check) state for cascading mode ---

/** Get all descendant keys of a node */
function getDescendantKeys(node: TreeNode): (string | number)[] {
  if (!node.children?.length) return []
  return node.children.flatMap((child) => [child.key, ...getDescendantKeys(child)])
}

const isIndeterminate = computed(() => {
  if (props.checkStrictly) return false
  if (!props.checkable) return false
  if (!props.node.children?.length) return false

  const descendantKeys = getDescendantKeys(props.node)
  if (descendantKeys.length === 0) return false

  const checkedSet = new Set(props.checkedKeys)
  const someChecked = descendantKeys.some((k) => checkedSet.has(k))
  const allChecked = descendantKeys.every((k) => checkedSet.has(k))

  return someChecked && !allChecked
})

// --- Drag & drop ---

const nodeRef = ref<HTMLElement | null>(null)

function onDragStart(e: DragEvent) {
  if (!props.draggableTree) return
  e.dataTransfer?.setData('text/plain', String(props.node.key))
  emit('drag-start', props.node.key)
}

function onDragOver(e: DragEvent) {
  if (!props.draggableTree || props.dragNodeKey === null) return
  if (props.dragNodeKey === props.node.key) return
  e.preventDefault()

  const rect = (e.currentTarget as HTMLElement).getBoundingClientRect()
  const y = e.clientY - rect.top
  const height = rect.height
  const quarter = height / 4

  let position: 'before' | 'inner' | 'after'
  if (y < quarter) {
    position = 'before'
  } else if (y > height - quarter) {
    position = 'after'
  } else {
    position = 'inner'
  }

  emit('drag-over', props.node.key, position)
}

function onDrop(e: DragEvent) {
  if (!props.draggableTree) return
  e.preventDefault()
  emit('drag-end')
}

function onDragEndNative() {
  if (!props.draggableTree) return
  emit('drag-end')
}

/** Check if the drop indicator should show for this node */
const showDropBefore = computed(() =>
  props.dropNodeKey === props.node.key && props.dropPosition === 'before'
)
const showDropAfter = computed(() =>
  props.dropNodeKey === props.node.key && props.dropPosition === 'after'
)
const showDropInner = computed(() =>
  props.dropNodeKey === props.node.key && props.dropPosition === 'inner'
)

/** Reference to the checkbox for indeterminate state */
const checkboxRef = ref<HTMLInputElement | null>(null)
</script>

<template>
  <li v-if="isVisible" :class="cn('select-none relative')">
    <!-- Drop indicator line - before -->
    <div
      v-if="draggableTree && showDropBefore"
      class="absolute left-0 right-0 top-0 h-0.5 bg-primary z-10"
      :style="{ marginLeft: `${depth * 16 + 8}px` }"
    />

    <!-- Node row -->
    <div
      ref="nodeRef"
      :class="cn(
        'flex items-center gap-1 rounded-sm px-2 py-1 text-sm cursor-pointer',
        'hover:bg-accent hover:text-accent-foreground',
        node.disabled && 'pointer-events-none opacity-50',
        draggableTree && showDropInner && 'ring-2 ring-primary rounded-sm',
      )"
      :style="{ paddingLeft: `${depth * 16 + 8}px` }"
      :draggable="draggableTree"
      @click="$emit('select', node.key)"
      @dragstart="onDragStart"
      @dragover="onDragOver"
      @drop="onDrop"
      @dragend="onDragEndNative"
    >
      <!-- Expand toggle / Loading spinner -->
      <button
        v-if="hasChildren()"
        class="shrink-0 rounded-sm p-0.5 hover:bg-accent"
        @click.stop="$emit('toggle-expand', node.key)"
      >
        <LoaderCircle
          v-if="isLoading()"
          class="size-3.5 animate-spin text-muted-foreground"
        />
        <ChevronRight
          v-else
          :class="cn('size-3.5 transition-transform', isExpanded() && 'rotate-90')"
        />
      </button>
      <span v-else class="w-5 shrink-0" />

      <!-- Checkbox -->
      <span v-if="checkable" class="relative flex shrink-0 items-center justify-center">
        <input
          ref="checkboxRef"
          type="checkbox"
          :checked="isChecked()"
          :disabled="node.disabled"
          class="size-4 shrink-0 rounded border-input accent-primary"
          @click.stop
          @change="$emit('toggle-check', node.key)"
        />
        <!-- Indeterminate overlay -->
        <Minus
          v-if="isIndeterminate"
          class="absolute inset-0 size-4 text-primary pointer-events-none"
          :stroke-width="3"
        />
      </span>

      <!-- Label -->
      <span class="flex-1 truncate">{{ node.label }}</span>
    </div>

    <!-- Drop indicator line - after -->
    <div
      v-if="draggableTree && showDropAfter && (!hasLoadedChildren() || !isExpanded())"
      class="absolute left-0 right-0 bottom-0 h-0.5 bg-primary z-10"
      :style="{ marginLeft: `${depth * 16 + 8}px` }"
    />

    <!-- Children (recursive) -->
    <ul v-if="hasLoadedChildren() && isExpanded()" class="list-none">
      <ETreeNode
        v-for="child in node.children"
        :key="child.key"
        :node="child"
        :checked-keys="checkedKeys"
        :expanded-keys="expandedKeys"
        :checkable="checkable"
        :depth="depth + 1"
        :lazy="lazy"
        :loading-keys="loadingKeys"
        :draggable-tree="draggableTree"
        :drag-node-key="dragNodeKey"
        :drop-node-key="dropNodeKey"
        :drop-position="dropPosition"
        :visible-keys="visibleKeys"
        :check-strictly="checkStrictly"
        :internal-data="internalData"
        @toggle-expand="$emit('toggle-expand', $event)"
        @toggle-check="$emit('toggle-check', $event)"
        @select="$emit('select', $event)"
        @drag-start="$emit('drag-start', $event)"
        @drag-over="(key, pos) => $emit('drag-over', key, pos)"
        @drag-end="$emit('drag-end')"
      />
    </ul>

    <!-- Drop indicator line - after (when expanded with children, show at the end) -->
    <div
      v-if="draggableTree && showDropAfter && hasLoadedChildren() && isExpanded()"
      class="absolute left-0 right-0 bottom-0 h-0.5 bg-primary z-10"
      :style="{ marginLeft: `${depth * 16 + 8}px` }"
    />
  </li>
</template>
