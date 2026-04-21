<!--
  ETree 树形组件
  支持勾选（可级联）、受控展开、懒加载子节点、拖拽排序、过滤搜索
  拖拽移动通过 DOM 位置计算「前/内/后」三种投放位置；懒加载通过 loadFn 异步返回子节点
  级联勾选：勾一个节点 → 联动所有后代；后代全选 → 自动回填父节点勾选状态
-->
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

/** 内部深拷贝的数据副本，用于懒加载时向节点写入 children 而不污染外部数据 */
const internalData = ref<TreeNode[]>([])

watch(() => props.data, (val) => {
  internalData.value = JSON.parse(JSON.stringify(val))
}, { immediate: true, deep: true })

/** 正在懒加载中的节点 key 集合，用于展开图标切换为 loading */
const loadingKeys = ref(new Set<string | number>())

/** 递归收集所有节点的 key（用于 defaultExpandAll） */
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

// --- 级联勾选所需的辅助映射 ---

/** 构建 key → 父 key 的映射，用于从子节点反向查找祖先 */
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

/** 构建 key → 节点对象 的映射，供 O(1) 查询 */
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

/** 获取某节点下所有后代节点的 key */
function getDescendantKeys(node: TreeNode): (string | number)[] {
  if (!node.children?.length) return []
  return node.children.flatMap((child) => [child.key, ...getDescendantKeys(child)])
}

/** 按 key 在树中查找节点 */
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

/**
 * 切换节点展开/折叠状态
 * 懒加载模式下展开未加载子节点时，先调用 loadFn 拉取子节点
 */
async function toggleExpand(key: string | number) {
  const idx = internalExpandedKeys.value.indexOf(key)
  if (idx >= 0) {
    internalExpandedKeys.value.splice(idx, 1)
  } else {
    // 懒加载：节点 children 未定义且非叶子，触发异步加载
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

/**
 * 切换节点勾选状态
 * 非严格模式下会级联所有后代；同时根据兄弟节点勾选情况回填祖先
 */
function toggleCheck(key: string | number) {
  const current = new Set(props.modelValue ?? [])
  const isChecked = !current.has(key)

  if (isChecked) {
    current.add(key)
  } else {
    current.delete(key)
  }

  // 非严格勾选：级联到后代，再根据状态回填祖先
  if (!props.checkStrictly) {
    const nodeMap = buildNodeMap(internalData.value)
    const parentMap = buildParentMap(internalData.value)
    const targetNode = nodeMap.get(key)

    // 向下级联：所有后代跟随当前节点
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

    // 向上回填：若父节点的所有子节点都被勾选则父节点也勾选，否则取消
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

// --- 拖拽排序 ---

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

/**
 * 拖拽结束：按投放位置（before/inner/after）重新排列节点
 */
function onDragEnd() {
  if (dragNodeKey.value !== null && dropNodeKey.value !== null && dropPosition.value !== null) {
    const dragNode = findNode(internalData.value, dragNodeKey.value)
    const dropNode = findNode(internalData.value, dropNodeKey.value)
    if (dragNode && dropNode && dragNodeKey.value !== dropNodeKey.value) {
      // 先从原父节点下移除
      removeNodeFromTree(internalData.value, dragNodeKey.value)

      // 再按投放位置插入
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

/**
 * 在目标节点附近插入被拖拽节点
 * inner 模式会自动展开目标节点，便于看到新插入的子节点
 */
function insertNode(nodes: TreeNode[], targetKey: string | number, node: TreeNode, position: 'before' | 'inner' | 'after'): boolean {
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].key === targetKey) {
      if (position === 'before') {
        nodes.splice(i, 0, node)
      } else if (position === 'after') {
        nodes.splice(i + 1, 0, node)
      } else {
        // inner：作为子节点插入
        if (!nodes[i].children) nodes[i].children = []
        nodes[i].children!.push(node)
        // 自动展开父节点以呈现新加入的子节点
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

// --- 过滤 ---

/** 收集匹配过滤条件的节点及其所有祖先 key（祖先也需显示才能看到子节点） */
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
