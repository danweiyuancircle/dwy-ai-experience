<!--
  ECascader 级联选择器组件
  支持单选/多选、搜索过滤、懒加载子节点、标签折叠等
  使用 reka-ui Popover 展示多列级联面板
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { ChevronDown, ChevronRight, X, Check, LoaderCircle } from 'lucide-vue-next'
import { PopoverContent, PopoverPortal, PopoverRoot, PopoverTrigger } from 'reka-ui'
import { cn } from '@/utils/cn'
import type { ECascaderProps, ECascaderEmits, CascaderOption } from './types'

const props = withDefaults(defineProps<ECascaderProps>(), {
  options: () => [],
  placeholder: 'Select...',
  disabled: false,
  clearable: false,
  filterable: false,
  lazy: false,
  multiple: false,
  collapseTags: false,
})

const emit = defineEmits<ECascaderEmits>()

const open = ref(false)
const searchQuery = ref('')

/** 当前正在异步加载子节点的 value 集合 */
const loadingValues = ref(new Set<string | number>())

/** 按层级记录的已选路径，用于面板展开导航 */
const activePath = ref<CascaderOption[]>([])

/** 当前要渲染的级联列（第一列为根，其后每列跟随 activePath） */
const columns = computed((): CascaderOption[][] => {
  const cols: CascaderOption[][] = [getFilteredRoots()]
  for (const option of activePath.value) {
    if (option.children?.length) {
      cols.push(option.children)
    }
  }
  return cols
})

/** 过滤后的根列（filterable + 搜索关键词时触发） */
function getFilteredRoots(): CascaderOption[] {
  if (!props.filterable || !searchQuery.value) return props.options
  return filterOptions(props.options, searchQuery.value)
}

/** 递归过滤选项树：节点自身或后代 label 命中都保留 */
function filterOptions(options: CascaderOption[], query: string): CascaderOption[] {
  return options.filter((o) => {
    const matchSelf = o.label.toLowerCase().includes(query.toLowerCase())
    const matchChildren = o.children ? filterOptions(o.children, query).length > 0 : false
    return matchSelf || matchChildren
  })
}

/** 判断选项是否位于当前激活路径的指定层级 */
function isInPath(option: CascaderOption, level: number): boolean {
  return activePath.value[level]?.value === option.value
}

/**
 * 判断选项是否为叶子节点
 * lazy 模式下优先读取 isLeaf 标记，再看 children 是否已加载
 */
function isLeaf(option: CascaderOption): boolean {
  if (props.lazy) {
    if (option.isLeaf) return true
    // lazy 模式下 children 未加载时不能判定为叶子
    if (option.children === undefined) return false
    return option.children.length === 0
  }
  return !option.children?.length
}

/** 判断指定选项是否正在异步加载子节点 */
function isOptionLoading(option: CascaderOption): boolean {
  return loadingValues.value.has(option.value)
}

/**
 * 点击选项的综合处理：
 * 1. 更新 activePath；2. lazy 需要则加载子节点；3. 叶子节点触发选中逻辑
 */
async function onOptionClick(option: CascaderOption, level: number) {
  if (option.disabled) return

  // 截断 activePath 到当前层级并追加当前选项
  activePath.value = [...activePath.value.slice(0, level), option]

  // 懒加载：子节点未加载且非叶子时调用 loadFn
  if (props.lazy && props.loadFn && option.children === undefined && !option.isLeaf) {
    loadingValues.value.add(option.value)
    try {
      const children = await props.loadFn(option)
      option.children = children
    } finally {
      loadingValues.value.delete(option.value)
    }
    // 加载后若无子节点，视为叶子并触发选中
    if (!option.children?.length) {
      handleLeafSelection(option)
    }
    return
  }

  if (isLeaf(option)) {
    handleLeafSelection(option)
  }
}

/**
 * 叶子节点选中处理：单选直接派发并关闭；多选切换选中状态且不关闭面板
 */
function handleLeafSelection(option: CascaderOption) {
  const values = activePath.value.map((o) => o.value)

  if (props.multiple) {
    const current = getMultipleModelValue()
    const existingIdx = current.findIndex(
      (path) => path.length === values.length && path.every((v, i) => v === values[i])
    )

    if (existingIdx >= 0) {
      // 已选则取消
      const next = [...current]
      next.splice(existingIdx, 1)
      emit('update:modelValue', next)
      emit('change', next)
    } else {
      // 未选则加入
      const next = [...current, values]
      emit('update:modelValue', next)
      emit('change', next)
    }
    // 多选模式保持面板打开
  } else {
    emit('update:modelValue', values)
    emit('change', values)
    open.value = false
    searchQuery.value = ''
  }
}

// --- 多选模式辅助函数 ---

/** 将 modelValue 规范化为多选模式下的路径数组的数组 */
function getMultipleModelValue(): (string | number)[][] {
  if (!props.multiple) return []
  if (!props.modelValue || !Array.isArray(props.modelValue)) return []
  // Check if it's already an array of arrays
  if (props.modelValue.length === 0) return []
  if (Array.isArray(props.modelValue[0])) {
    return props.modelValue as (string | number)[][]
  }
  return []
}

/** 判断叶子节点的完整路径是否已被选中 */
function isPathSelected(option: CascaderOption, level: number): boolean {
  if (!props.multiple) return false
  // Build the path to this option using activePath up to level, then this option
  const pathValues = [...activePath.value.slice(0, level).map((o) => o.value), option.value]
  const selected = getMultipleModelValue()
  return selected.some(
    (path) => path.length === pathValues.length && path.every((v, i) => v === pathValues[i])
  )
}

/** 将 value 路径解析为对应的 label 路径并以 " / " 拼接 */
function pathToLabels(path: (string | number)[]): string {
  let nodes = props.options
  const labels: string[] = []
  for (const val of path) {
    const found = nodes.find((o) => o.value === val)
    if (!found) break
    labels.push(found.label)
    nodes = found.children ?? []
  }
  return labels.join(' / ')
}

/** 获取路径最末节点的 label，用于多选 tag 显示 */
function pathToLastLabel(path: (string | number)[]): string {
  let nodes = props.options
  let lastLabel = ''
  for (const val of path) {
    const found = nodes.find((o) => o.value === val)
    if (!found) break
    lastLabel = found.label
    nodes = found.children ?? []
  }
  return lastLabel
}

/** 多选模式下触发区展示的已选路径集合 */
const selectedPaths = computed((): (string | number)[][] => {
  return getMultipleModelValue()
})

/** 触发区可见的 tag（collapseTags 开启时仅展示第一项） */
const visibleTags = computed(() => {
  if (props.collapseTags) return selectedPaths.value.slice(0, 1)
  return selectedPaths.value
})

/** 被折叠隐藏的 tag 数量，用于 "+N" 提示 */
const hiddenTagCount = computed(() => {
  if (!props.collapseTags) return 0
  return Math.max(0, selectedPaths.value.length - 1)
})

/** 根据索引移除某条已选路径 */
function removeTag(e: MouseEvent, index: number) {
  e.stopPropagation()
  const current = getMultipleModelValue()
  const next = [...current]
  next.splice(index, 1)
  emit('update:modelValue', next)
  emit('change', next)
}

/** 单选模式下根据 modelValue 解析出完整 label 路径字符串 */
const displayLabel = computed(() => {
  if (props.multiple) return ''
  const mv = props.modelValue as (string | number)[] | undefined
  if (!mv?.length) return ''
  return pathToLabels(mv)
})

/** 清空所有已选值并重置激活路径 */
function onClear(e: MouseEvent) {
  e.stopPropagation()
  activePath.value = []
  if (props.multiple) {
    emit('update:modelValue', [])
    emit('change', [])
  } else {
    emit('update:modelValue', [])
    emit('change', [])
  }
}

/** 面板开关变化：关闭时清空搜索关键词 */
function onOpenChange(val: boolean) {
  open.value = val
  if (!val) {
    searchQuery.value = ''
  }
}

/** 是否展示清空按钮（有值且允许清空） */
const showClear = computed(() => {
  if (!props.clearable) return false
  if (props.multiple) {
    return selectedPaths.value.length > 0
  }
  const mv = props.modelValue as (string | number)[] | undefined
  return !!mv?.length
})

/** 是否有有效选中值（用于占位符样式判断） */
const hasValue = computed(() => {
  if (props.multiple) return selectedPaths.value.length > 0
  return !!displayLabel.value
})
</script>

<template>
  <PopoverRoot :open="open" @update:open="onOpenChange">
    <PopoverTrigger as-child>
      <button
        :disabled="disabled"
        :class="cn(
          'flex w-full items-center justify-between rounded-md border border-input bg-transparent px-3 py-2 text-sm shadow-xs transition-[color,box-shadow]',
          'outline-none focus-visible:border-ring focus-visible:ring-ring/50 focus-visible:ring-[3px]',
          'disabled:cursor-not-allowed disabled:opacity-50',
          multiple ? 'min-h-9 py-1.5' : 'h-9',
          !hasValue && 'text-muted-foreground',
          props.class,
        )"
      >
        <!-- Multiple mode: tags -->
        <div v-if="multiple" class="flex flex-1 flex-wrap items-center gap-1 overflow-hidden">
          <template v-if="selectedPaths.length > 0">
            <span
              v-for="(path, idx) in visibleTags"
              :key="idx"
              :class="cn(
                'inline-flex items-center gap-1 rounded bg-secondary text-secondary-foreground px-1.5 py-0.5 text-xs font-medium max-w-[120px]',
              )"
            >
              <span class="truncate" :title="pathToLabels(path)">{{ pathToLastLabel(path) }}</span>
              <button
                type="button"
                tabindex="-1"
                class="flex shrink-0 items-center text-muted-foreground hover:text-foreground transition-colors pointer-events-auto"
                @click="removeTag($event, idx)"
                @pointerdown.stop
              >
                <X class="size-3" />
              </button>
            </span>
            <span
              v-if="hiddenTagCount > 0"
              class="inline-flex items-center rounded bg-muted text-muted-foreground px-1.5 py-0.5 text-xs font-medium"
            >
              +{{ hiddenTagCount }}
            </span>
          </template>
          <span v-else class="text-muted-foreground">{{ placeholder }}</span>
        </div>

        <!-- Single mode: label -->
        <span v-else class="flex-1 truncate text-left">{{ displayLabel || placeholder }}</span>

        <div class="flex items-center gap-1">
          <X
            v-if="showClear"
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
          'z-50 rounded-md border bg-popover text-popover-foreground shadow-md outline-none p-0',
          'data-[state=open]:animate-in data-[state=closed]:animate-out',
          'data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0',
          'data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95',
        )"
      >
        <!-- Search input -->
        <div v-if="filterable" class="border-b p-2">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search..."
            class="w-full rounded-sm bg-transparent text-sm outline-none placeholder:text-muted-foreground"
          />
        </div>

        <!-- Cascading columns -->
        <div class="flex">
          <div
            v-for="(colOptions, colIdx) in columns"
            :key="colIdx"
            class="max-h-[240px] min-w-[140px] overflow-y-auto border-r last:border-r-0"
          >
            <button
              v-for="option in colOptions"
              :key="String(option.value)"
              :disabled="option.disabled"
              :class="cn(
                'flex w-full items-center justify-between gap-2 px-3 py-1.5 text-sm',
                'hover:bg-accent hover:text-accent-foreground',
                'disabled:pointer-events-none disabled:opacity-50',
                isInPath(option, colIdx) && 'bg-accent text-accent-foreground font-medium',
              )"
              @click="onOptionClick(option, colIdx)"
            >
              <!-- Checkbox for multiple mode -->
              <span v-if="multiple && isLeaf(option)" class="shrink-0 flex items-center">
                <Check
                  v-if="isPathSelected(option, colIdx)"
                  class="size-3.5 text-primary"
                />
                <span v-else class="size-3.5 rounded-sm border border-input" />
              </span>

              <span class="flex-1 truncate text-left">{{ option.label }}</span>

              <LoaderCircle
                v-if="isOptionLoading(option)"
                class="size-3.5 shrink-0 animate-spin text-muted-foreground"
              />
              <ChevronRight
                v-else-if="!isLeaf(option)"
                class="size-3.5 shrink-0 opacity-50"
              />
            </button>
            <div v-if="colOptions.length === 0" class="px-3 py-4 text-center text-xs text-muted-foreground">
              No options
            </div>
          </div>
        </div>
      </PopoverContent>
    </PopoverPortal>
  </PopoverRoot>
</template>
