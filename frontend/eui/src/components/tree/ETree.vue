<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { cn } from '@/utils/cn'
import type { ETreeProps, ETreeEmits, TreeNode } from './types'
import ETreeNode from './ETreeNode.vue'

const props = withDefaults(defineProps<ETreeProps>(), {
  data: () => [],
  modelValue: () => [],
  checkable: false,
  expandedKeys: () => [],
  defaultExpandAll: false,
  lazy: false,
  draggable: false,
  checkStrictly: false,
})

const emit = defineEmits<ETreeEmits>()

/** Internal reactive copy of tree data for lazy loading mutations */
const internalData = ref<TreeNode[]>([])

watch(() => props.data, (val) => {
  internalData.value = JSON.parse(JSON.stringify(val))
}, { immediate: true, deep: true })

/** Set of node keys currently loading children */
const loadingKeys = ref(new Set<string | number>())

/** Collect all keys recursively */
function getAllKeys(nodes: TreeNode[]): (string | number)[] {
  return nodes.flatMap((n) => [n.key, ...getAllKeys(n.children ?? [])])
}

const internalExpandedKeys = ref<(string | number)[]>([])

onMounted(() => {
  if (props.defaultExpandAll) {
    internalExpandedKeys.value = getAllKeys(internalData.value)
  } else {
    internalExpandedKeys.value = [...props.expandedKeys]
  }
})

watch(() => props.expandedKeys, (val) => {
  internalExpandedKeys.value = [...val]
})

// --- Helper maps for cascading check ---

/** Build a map of key -> parent key */
function buildParentMap(nodes: TreeNode[], parentKey?: string | number): Map<string | number, string | number> {
  const map = new Map<string | number, string | number>()
  for (const node of nodes) {
    if (parentKey !== undefined) {
      map.set(node.key, parentKey)
    }
    if (node.children?.length) {
      for (const [k, v] of buildParentMap(node.children, node.key)) {
        map.set(k, v)
      }
    }
  }
  return map
}

/** Build a map of key -> node */
function buildNodeMap(nodes: TreeNode[]): Map<string | number, TreeNode> {
  const map = new Map<string | number, TreeNode>()
  for (const node of nodes) {
    map.set(node.key, node)
    if (node.children?.length) {
      for (const [k, v] of buildNodeMap(node.children)) {
        map.set(k, v)
      }
    }
  }
  return map
}

/** Get all descendant keys of a node */
function getDescendantKeys(node: TreeNode): (string | number)[] {
  if (!node.children?.length) return []
  return node.children.flatMap((child) => [child.key, ...getDescendantKeys(child)])
}

/** Find a node by key in the tree */
function findNode(nodes: TreeNode[], key: string | number): TreeNode | undefined {
  for (const node of nodes) {
    if (node.key === key) return node
    if (node.children?.length) {
      const found = findNode(node.children, key)
      if (found) return found
    }
  }
  return undefined
}

async function toggleExpand(key: string | number) {
  const idx = internalExpandedKeys.value.indexOf(key)
  if (idx >= 0) {
    internalExpandedKeys.value.splice(idx, 1)
  } else {
    // Lazy loading: if node has no children and loadFn is provided
    if (props.lazy && props.loadFn) {
      const node = findNode(internalData.value, key)
      if (node && node.children === undefined && !node.isLeaf) {
        loadingKeys.value.add(key)
        try {
          const children = await props.loadFn(node)
          node.children = children
        } finally {
          loadingKeys.value.delete(key)
        }
      }
    }
    internalExpandedKeys.value.push(key)
  }
  emit('update:expandedKeys', [...internalExpandedKeys.value])
}

function toggleCheck(key: string | number) {
  const current = new Set(props.modelValue ?? [])
  const isChecked = !current.has(key)

  if (isChecked) {
    current.add(key)
  } else {
    current.delete(key)
  }

  // Cascading check (when checkStrictly is false)
  if (!props.checkStrictly) {
    const nodeMap = buildNodeMap(internalData.value)
    const parentMap = buildParentMap(internalData.value)
    const targetNode = nodeMap.get(key)

    // Cascade to descendants
    if (targetNode) {
      const descendantKeys = getDescendantKeys(targetNode)
      for (const dk of descendantKeys) {
        if (isChecked) {
          current.add(dk)
        } else {
          current.delete(dk)
        }
      }
    }

    // Cascade to ancestors: check parent if all its children are checked
    let parentKey = parentMap.get(key)
    while (parentKey !== undefined) {
      const parentNode = nodeMap.get(parentKey)
      if (parentNode?.children?.length) {
        const allChildrenChecked = parentNode.children.every((child) => current.has(child.key))
        if (allChildrenChecked) {
          current.add(parentKey)
        } else {
          current.delete(parentKey)
        }
      }
      parentKey = parentMap.get(parentKey)
    }
  }

  const keys = [...current]
  emit('update:modelValue', keys)
  emit('check', key, isChecked)
}

function onSelect(key: string | number) {
  emit('select', key)
}

// --- Drag & drop ---

const dragNodeKey = ref<string | number | null>(null)
const dropNodeKey = ref<string | number | null>(null)
const dropPosition = ref<'before' | 'inner' | 'after' | null>(null)

function onDragStart(key: string | number) {
  dragNodeKey.value = key
}

function onDragOver(key: string | number, position: 'before' | 'inner' | 'after') {
  dropNodeKey.value = key
  dropPosition.value = position
}

function onDragEnd() {
  if (dragNodeKey.value !== null && dropNodeKey.value !== null && dropPosition.value !== null) {
    const dragNode = findNode(internalData.value, dragNodeKey.value)
    const dropNode = findNode(internalData.value, dropNodeKey.value)
    if (dragNode && dropNode && dragNodeKey.value !== dropNodeKey.value) {
      // Remove drag node from its current parent
      removeNodeFromTree(internalData.value, dragNodeKey.value)

      // Insert at the new position
      insertNode(internalData.value, dropNodeKey.value, dragNode, dropPosition.value)

      emit('node-drop', dragNode, dropNode, dropPosition.value)
    }
  }
  dragNodeKey.value = null
  dropNodeKey.value = null
  dropPosition.value = null
}

function removeNodeFromTree(nodes: TreeNode[], key: string | number): boolean {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].key === key) {
      nodes.splice(i, 1)
      return true
    }
    if (nodes[i].children?.length) {
      if (removeNodeFromTree(nodes[i].children!, key)) return true
    }
  }
  return false
}

function insertNode(nodes: TreeNode[], targetKey: string | number, node: TreeNode, position: 'before' | 'inner' | 'after'): boolean {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].key === targetKey) {
      if (position === 'before') {
        nodes.splice(i, 0, node)
      } else if (position === 'after') {
        nodes.splice(i + 1, 0, node)
      } else {
        // inner
        if (!nodes[i].children) nodes[i].children = []
        nodes[i].children!.push(node)
        // Auto-expand the target node
        if (!internalExpandedKeys.value.includes(targetKey)) {
          internalExpandedKeys.value.push(targetKey)
        }
      }
      return true
    }
    if (nodes[i].children?.length) {
      if (insertNode(nodes[i].children!, targetKey, node, position)) return true
    }
  }
  return false
}

// --- Filtering ---

/** Collect keys of nodes matching the filter + their ancestors */
const visibleKeys = computed((): Set<string | number> | null => {
  if (!props.filterQuery || !props.filterMethod) return null

  const matchedKeys = new Set<string | number>()
  const parentMap = buildParentMap(internalData.value)

  function walkAndMatch(nodes: TreeNode[]) {
    for (const node of nodes) {
      if (props.filterMethod!(props.filterQuery!, node)) {
        // Add this node and all its ancestors
        matchedKeys.add(node.key)
        let parentKey = parentMap.get(node.key)
        while (parentKey !== undefined) {
          matchedKeys.add(parentKey)
          parentKey = parentMap.get(parentKey)
        }
      }
      if (node.children?.length) {
        walkAndMatch(node.children)
      }
    }
  }

  walkAndMatch(internalData.value)
  return matchedKeys
})
</script>

<template>
  <ul
    data-slot="tree"
    :class="cn('list-none space-y-0.5', props.class)"
    role="tree"
  >
    <ETreeNode
      v-for="node in internalData"
      :key="node.key"
      :node="node"
      :checked-keys="modelValue ?? []"
      :expanded-keys="internalExpandedKeys"
      :checkable="checkable"
      :depth="0"
      :lazy="lazy"
      :loading-keys="loadingKeys"
      :draggable-tree="draggable"
      :drag-node-key="dragNodeKey"
      :drop-node-key="dropNodeKey"
      :drop-position="dropPosition"
      :visible-keys="visibleKeys"
      :check-strictly="checkStrictly"
      :internal-data="internalData"
      @toggle-expand="toggleExpand"
      @toggle-check="toggleCheck"
      @select="onSelect"
      @drag-start="onDragStart"
      @drag-over="onDragOver"
      @drag-end="onDragEnd"
    />
  </ul>
</template>
