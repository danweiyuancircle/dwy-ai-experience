<!--
  ETable 数据表格组件
  排序/行模型走 @tanstack/vue-table；virtual 走 @tanstack/vue-virtual。
  对外仍是 TableColumn / #cell-* / @sort，不泄露 TanStack 类型。
  mobileLayout=stack 且窄屏时改渲染卡片，不藏列。
-->
<script setup lang="ts">
import { computed, ref } from 'vue'
import { LoaderCircle, ArrowUpDown, ArrowUp, ArrowDown, ChevronRight } from 'lucide-vue-next'
import {
  useVueTable,
  getCoreRowModel,
  getSortedRowModel,
  type ColumnDef,
  type SortingState,
} from '@tanstack/vue-table'
import { useVirtualizer } from '@tanstack/vue-virtual'
import { cn } from '@/utils/cn'
import { useEuiMobile } from '@/composables/useEuiMobile'
import type { ETableProps, ETableEmits } from './types'
import type { TableColumn } from '@/types'

const props = withDefaults(defineProps<ETableProps>(), {
  data: () => [],
  columns: () => [],
  loading: false,
  rowKey: 'id',
  striped: false,
  bordered: false,
  emptyText: '暂无数据',
  selectable: false,
  selectedKeys: () => [],
  expandable: false,
  expandedRowKeys: () => [],
  showSummary: false,
  virtual: false,
  virtualRowHeight: 48,
  resizable: false,
  mobileLayout: 'scroll',
})

const emit = defineEmits<ETableEmits>()

/** 与壳 / 分页同一 767 断点。stack 只在窄屏切卡片，避免后台宽表被默认改掉。 */
const isMobile = useEuiMobile()
const isStack = computed(
  () => props.mobileLayout === 'stack' && isMobile.value,
)

const sortState = ref<{ key: string; direction: 'asc' | 'desc' | null }>({
  key: '',
  direction: null,
})

/** 把 eui TableColumn 映射成 TanStack ColumnDef，只给排序/行模型用 */
const tanstackColumns = computed<ColumnDef<Record<string, any>>[]>(() =>
  props.columns.map((col) => ({
    id: col.key,
    accessorKey: col.key,
    header: col.title,
    enableSorting: Boolean(col.sortable),
  })),
)

const sorting = computed<SortingState>(() => {
  if (!sortState.value.direction || !sortState.value.key) return []
  return [{ id: sortState.value.key, desc: sortState.value.direction === 'desc' }]
})

const table = useVueTable({
  get data() {
    return props.data
  },
  get columns() {
    return tanstackColumns.value
  },
  getCoreRowModel: getCoreRowModel(),
  getSortedRowModel: getSortedRowModel(),
  state: {
    get sorting() {
      return sorting.value
    },
  },
  getRowId: (row, index) => String(row[props.rowKey] ?? index),
})

/** 排序后的行数据（original），模板仍按 eui 行对象渲染插槽 */
const sortedData = computed(() =>
  table.getRowModel().rows.map((row) => row.original as Record<string, any>),
)

function getRowKey(row: Record<string, any>, index: number): string | number {
  return row[props.rowKey] ?? index
}

function handleRowClick(row: Record<string, any>, index: number) {
  emit('row-click', row, index)
}

function handleSort(column: TableColumn) {
  if (!column.sortable) return

  let direction: 'asc' | 'desc' | null = 'asc'
  if (sortState.value.key === column.key) {
    if (sortState.value.direction === 'asc') {
      direction = 'desc'
    } else if (sortState.value.direction === 'desc') {
      direction = null
    }
  }

  sortState.value = { key: column.key, direction }
  if (direction) {
    emit('sort', column.key, direction)
  }
}

function getSortDirection(column: TableColumn): 'asc' | 'desc' | null {
  if (!column.sortable) return null
  if (sortState.value.key !== column.key) return null
  return sortState.value.direction
}

const isAllSelected = computed(() => {
  if (!props.data || props.data.length === 0) return false
  return props.data.every((row, index) =>
    props.selectedKeys.includes(getRowKey(row, index)),
  )
})

const isIndeterminate = computed(() => {
  if (!props.data || props.data.length === 0) return false
  const selectedCount = props.data.filter((row, index) =>
    props.selectedKeys.includes(getRowKey(row, index)),
  ).length
  return selectedCount > 0 && selectedCount < props.data.length
})

function handleSelectAll() {
  if (isAllSelected.value) {
    emit('update:selectedKeys', [])
  } else {
    const allKeys = props.data.map((row, index) => getRowKey(row, index))
    emit('update:selectedKeys', allKeys)
  }
}

function handleSelectRow(row: Record<string, any>, index: number) {
  const key = getRowKey(row, index)
  const current = [...props.selectedKeys]
  const idx = current.indexOf(key)
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(key)
  }
  emit('update:selectedKeys', current)
}

function isRowSelected(row: Record<string, any>, index: number): boolean {
  return props.selectedKeys.includes(getRowKey(row, index))
}

// --- 固定列逻辑 ---

/** 将列宽统一解析为像素数值，用于计算 sticky 偏移 */
function resolveWidth(width: number | string | undefined): number {
  if (width == null) return 0
  if (typeof width === 'number') return width
  const num = parseFloat(width)
  return Number.isNaN(num) ? 0 : num
}

/** 所有左固定列（保持原顺序） */
const leftFixedColumns = computed(() =>
  props.columns.filter((c) => c.fixed === 'left'),
)

/** 所有右固定列（保持原顺序） */
const rightFixedColumns = computed(() =>
  props.columns.filter((c) => c.fixed === 'right'),
)

/** 每列对应的 sticky 偏移量映射（key → 侧 + px 偏移） */
const fixedOffsets = computed(() => {
  const map: Record<string, { side: 'left' | 'right'; offset: number }> = {}

  // 左固定列：从左到右累加偏移
  let leftAcc = 0
  // 选择列宽度 40px，需计入偏移
  if (props.selectable) {
    leftAcc += 40
  }
  // 展开列宽度 40px，需计入偏移
  if (props.expandable) {
    leftAcc += 40
  }
  for (const col of leftFixedColumns.value) {
    map[col.key] = { side: 'left', offset: leftAcc }
    leftAcc += resolveWidth(col.width)
  }

  // 右固定列：从右到左累加偏移
  let rightAcc = 0
  // 操作列在数据列之后，不影响右固定偏移
  const reversed = [...rightFixedColumns.value].reverse()
  for (const col of reversed) {
    map[col.key] = { side: 'right', offset: rightAcc }
    rightAcc += resolveWidth(col.width)
  }

  return map
})

function getFixedStyle(column: TableColumn): Record<string, string> | undefined {
  const info = fixedOffsets.value[column.key]
  if (!info) return undefined
  return {
    position: 'sticky',
    [info.side]: `${info.offset}px`,
    zIndex: '1',
  }
}

function getFixedClass(column: TableColumn): string {
  const info = fixedOffsets.value[column.key]
  if (!info) return ''

  if (info.side === 'left') {
    // 最后一个左固定列加右侧阴影，提示可滚动内容
    const leftCols = leftFixedColumns.value
    const isLast = leftCols[leftCols.length - 1]?.key === column.key
    return cn('bg-background', isLast && 'shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]')
  }

  // 第一个右固定列加左侧阴影，提示左侧存在被遮挡内容
  const rightCols = rightFixedColumns.value
  const isFirst = rightCols[0]?.key === column.key
  return cn('bg-background', isFirst && 'shadow-[-2px_0_5px_-2px_rgba(0,0,0,0.1)]')
}

// --- 行展开 ---

function isRowExpanded(row: Record<string, any>, index: number): boolean {
  return props.expandedRowKeys.includes(getRowKey(row, index))
}

function toggleRowExpand(row: Record<string, any>, index: number) {
  const key = getRowKey(row, index)
  const current = [...props.expandedRowKeys]
  const idx = current.indexOf(key)
  if (idx >= 0) {
    current.splice(idx, 1)
  } else {
    current.push(key)
  }
  emit('update:expandedRowKeys', current)
}

// --- 行 class 支持函数式 ---

function getRowClassName(row: Record<string, any>, index: number): string {
  if (!props.rowClassName) return ''
  if (typeof props.rowClassName === 'function') return props.rowClassName(row, index)
  return props.rowClassName
}

// --- 汇总行 ---

const summaryValues = computed<(string | number)[]>(() => {
  if (!props.showSummary) return []

  if (props.summaryMethod) {
    return props.summaryMethod(props.data, props.columns)
  }

  // 默认汇总：第一列显示「合计」，其余列对纯数字列求和
  return props.columns.map((col, colIndex) => {
    if (colIndex === 0) return '合计'
    const values = props.data.map((row) => row[col.key])
    const isNumeric = values.length > 0 && values.every((v) => v == null || typeof v === 'number')
    if (!isNumeric) return ''
    return values.reduce((sum: number, v) => sum + (v ?? 0), 0) as number
  })
})

// --- 虚拟滚动（@tanstack/vue-virtual）---

const virtualContainerRef = ref<HTMLElement | null>(null)

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: props.virtual ? sortedData.value.length : 0,
    estimateSize: () => props.virtualRowHeight,
    getScrollElement: () => virtualContainerRef.value,
    overscan: 5,
  })),
)

const virtualItems = computed(() =>
  props.virtual ? rowVirtualizer.value.getVirtualItems() : [],
)

const visibleRows = computed(() => {
  if (isStack.value || !props.virtual) return sortedData.value
  return virtualItems.value.map((item) => sortedData.value[item.index]).filter(Boolean)
})

const virtualOffsetY = computed(() => virtualItems.value[0]?.start ?? 0)

const totalHeight = computed(() =>
  props.virtual ? rowVirtualizer.value.getTotalSize() : 0,
)

/** 当前渲染行在全量数据中的下标（virtual 用 virtualizer index；stack 已禁用窗口） */
function dataIndex(idx: number): number {
  if (isStack.value || !props.virtual) return idx
  return virtualItems.value[idx]?.index ?? idx
}

// --- 列宽拖拽 ---

const columnWidths = ref<Record<string, number>>({})

/** 获取最终列宽：本地拖拽后的宽度优先于列配置声明 */
function getColumnWidth(column: TableColumn): number | string | undefined {
  if (props.resizable && columnWidths.value[column.key]) {
    return columnWidths.value[column.key]
  }
  return column.width
}

function getColumnStyle(column: TableColumn): Record<string, string | undefined> {
  const w = getColumnWidth(column)
  const widthPx = w ? (typeof w === 'number' ? `${w}px` : w) : undefined
  // 数字 width 同时当下限：table-fixed + 100% 时列不会被压到比声明更窄，窄屏才能横滑
  return {
    width: widthPx,
    minWidth: column.minWidth
      ? `${column.minWidth}px`
      : (typeof w === 'number' ? `${w}px` : undefined),
    ...getFixedStyle(column),
  }
}

/**
 * 声明了数字列宽时，表 min-width 取列宽之和。
 * 宽于容器 → 横滑；窄于容器 → width 100% 把余量分给各列。
 * 不用 w-max：长单元格会把表撑出视口，末列（如结束日期）默认看不见。
 */
const tableMinWidth = computed(() => {
  let sum = 0
  for (const column of props.columns ?? []) {
    const w = getColumnWidth(column)
    if (typeof w === 'number') sum += w
  }
  return sum > 0 ? `${sum}px` : undefined
})

let resizeCol: string | null = null
let resizeStartX = 0
let resizeStartWidth = 0

/**
 * 列宽拖拽开始：记录起始位置与宽度，注册全局 mousemove/mouseup 监听
 */
function onResizeMouseDown(event: MouseEvent, column: TableColumn) {
  event.preventDefault()
  event.stopPropagation()
  resizeCol = column.key

  // 读取初始宽度：优先本地拖拽值 → 配置值 → 实际渲染宽度
  const currentWidth = columnWidths.value[column.key]
  if (currentWidth) {
    resizeStartWidth = currentWidth
  } else if (column.width) {
    resizeStartWidth = typeof column.width === 'number' ? column.width : parseFloat(column.width) || 100
  } else {
    const th = (event.target as HTMLElement).closest('th')
    resizeStartWidth = th ? th.offsetWidth : 100
  }

  resizeStartX = event.clientX
  document.addEventListener('mousemove', onResizeMouseMove)
  document.addEventListener('mouseup', onResizeMouseUp)
  document.body.style.cursor = 'col-resize'
  document.body.style.userSelect = 'none'
}

function onResizeMouseMove(event: MouseEvent) {
  if (!resizeCol) return
  const delta = event.clientX - resizeStartX
  const newWidth = Math.max(50, resizeStartWidth + delta)
  columnWidths.value[resizeCol] = newWidth
}

function onResizeMouseUp() {
  resizeCol = null
  document.removeEventListener('mousemove', onResizeMouseMove)
  document.removeEventListener('mouseup', onResizeMouseUp)
  document.body.style.cursor = ''
  document.body.style.userSelect = ''
}
</script>

<template>
  <div
    ref="virtualContainerRef"
    data-slot="table-container"
    :class="cn(
      'relative w-full overflow-auto overscroll-x-contain',
      bordered && 'rounded-md border',
    )"
  >
    <!-- Loading overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 z-10 flex items-center justify-center bg-background/80"
    >
      <LoaderCircle class="size-6 animate-spin text-muted-foreground" />
    </div>

    <template v-if="!isStack">
    <table
      data-slot="table"
      :class="cn(
        'w-full caption-bottom text-sm',
        bordered && '[&_th]:border [&_td]:border',
        resizable && 'table-fixed',
        props.class,
      )"
      :style="tableMinWidth ? { minWidth: tableMinWidth } : undefined"
    >
      <!-- Header -->
      <thead
        data-slot="table-header"
        :class="cn('[&_tr]:border-b', virtual && 'sticky top-0 z-[2] bg-background')"
      >
        <tr
          data-slot="table-row"
          :class="cn('hover:bg-muted/50 border-b transition-colors')"
        >
          <!-- Selection checkbox header -->
          <th
            v-if="selectable"
            data-slot="table-head"
            :class="cn('text-muted-foreground h-10 w-10 px-2 text-center align-middle font-medium whitespace-nowrap bg-background')"
            :style="expandable ? undefined : { position: 'sticky', left: '0px', zIndex: 1 }"
          >
            <input
              type="checkbox"
              :checked="isAllSelected"
              :indeterminate="isIndeterminate"
              class="size-4 rounded border border-primary accent-primary"
              @change="handleSelectAll"
            />
          </th>

          <!-- Expandable header (empty placeholder) -->
          <th
            v-if="expandable"
            data-slot="table-head"
            :class="cn('text-muted-foreground h-10 w-10 px-2 text-center align-middle font-medium whitespace-nowrap bg-background')"
            :style="{ position: 'sticky', left: selectable ? '40px' : '0px', zIndex: 1 }"
          />

          <th
            v-for="column in columns"
            :key="column.key"
            data-slot="table-head"
            :class="cn(
              'text-muted-foreground h-10 px-2 align-middle font-medium whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]',
              column.align === 'center' && 'text-center',
              column.align === 'right' && 'text-right',
              !column.align && 'text-left',
              column.sortable && 'cursor-pointer select-none hover:text-foreground',
              resizable && 'relative',
              getFixedClass(column),
            )"
            :style="getColumnStyle(column)"
            @click="handleSort(column)"
          >
            <span class="inline-flex items-center gap-1">
              {{ column.title }}
              <ArrowUp v-if="getSortDirection(column) === 'asc'" class="size-3.5 text-foreground" />
              <ArrowDown v-else-if="getSortDirection(column) === 'desc'" class="size-3.5 text-foreground" />
              <ArrowUpDown v-else-if="column.sortable" class="size-3.5 opacity-40" />
            </span>
            <!-- Column resize handle -->
            <span
              v-if="resizable"
              class="absolute right-0 top-0 bottom-0 w-1 cursor-col-resize hover:bg-primary/30"
              @mousedown="onResizeMouseDown($event, column)"
              @click.stop
            />
          </th>

          <!-- Actions header -->
          <th
            v-if="$slots.actions"
            data-slot="table-head"
            :class="cn('text-muted-foreground h-10 px-2 text-right align-middle font-medium whitespace-nowrap')"
          >
            操作
          </th>
        </tr>
      </thead>

      <!-- Body -->
      <tbody
        data-slot="table-body"
        :class="cn('[&_tr:last-child]:border-0')"
      >
        <!-- Empty state -->
        <tr v-if="!sortedData || sortedData.length === 0">
          <td
            :colspan="(selectable ? 1 : 0) + (expandable ? 1 : 0) + columns.length + ($slots.actions ? 1 : 0)"
            :class="cn('p-4 whitespace-nowrap align-middle text-sm')"
          >
            <div class="flex items-center justify-center py-10 text-muted-foreground">
              <slot name="empty">{{ emptyText }}</slot>
            </div>
          </td>
        </tr>

        <!-- Virtual scrolling spacer top -->
        <tr v-if="virtual && sortedData.length > 0" aria-hidden="true">
          <td
            :colspan="(selectable ? 1 : 0) + (expandable ? 1 : 0) + columns.length + ($slots.actions ? 1 : 0)"
            :style="{ height: `${virtualOffsetY}px`, padding: 0, border: 'none' }"
          />
        </tr>

        <!-- Data rows (visible rows when virtual, all rows when not) -->
        <template
          v-for="(row, idx) in visibleRows"
          :key="getRowKey(row, dataIndex(idx))"
        >
          <tr
            data-slot="table-row"
            :data-state="isRowSelected(row, dataIndex(idx)) ? 'selected' : undefined"
            :class="cn(
              'hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors',
              striped && (dataIndex(idx)) % 2 === 1 && 'bg-muted/40',
              getRowClassName(row, dataIndex(idx)),
            )"
            :style="virtual ? { height: `${virtualRowHeight}px` } : undefined"
            @click="handleRowClick(row, dataIndex(idx))"
          >
            <!-- Selection checkbox -->
            <td
              v-if="selectable"
              data-slot="table-cell"
              :class="cn('w-10 px-2 text-center align-middle whitespace-nowrap bg-background')"
              :style="expandable ? undefined : { position: 'sticky', left: '0px', zIndex: 1 }"
              @click.stop
            >
              <input
                type="checkbox"
                :checked="isRowSelected(row, dataIndex(idx))"
                class="size-4 rounded border border-primary accent-primary"
                @change="handleSelectRow(row, dataIndex(idx))"
              />
            </td>

            <!-- Expand toggle -->
            <td
              v-if="expandable"
              data-slot="table-cell"
              :class="cn('w-10 px-2 text-center align-middle whitespace-nowrap bg-background')"
              :style="{ position: 'sticky', left: selectable ? '40px' : '0px', zIndex: 1 }"
              @click.stop="toggleRowExpand(row, dataIndex(idx))"
            >
              <button
                type="button"
                class="inline-flex items-center justify-center rounded p-0.5 hover:bg-muted transition-transform duration-200"
                :class="isRowExpanded(row, dataIndex(idx)) && 'rotate-90'"
              >
                <ChevronRight class="size-4 text-muted-foreground" />
              </button>
            </td>

            <!-- Data cells -->
            <td
              v-for="column in columns"
              :key="column.key"
              data-slot="table-cell"
              :class="cn(
                'p-2 align-middle whitespace-nowrap [&:has([role=checkbox])]:pr-0 [&>[role=checkbox]]:translate-y-[2px]',
                column.align === 'center' && 'text-center',
                column.align === 'right' && 'text-right',
                getFixedClass(column),
              )"
              :style="getFixedStyle(column)"
            >
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :index="dataIndex(idx)"
                :value="row[column.key]"
              >
                {{ row[column.key] }}
              </slot>
            </td>

            <!-- Actions cell -->
            <td
              v-if="$slots.actions"
              data-slot="table-cell"
              :class="cn('p-2 text-right align-middle whitespace-nowrap')"
              @click.stop
            >
              <slot name="actions" :row="row" :index="dataIndex(idx)" />
            </td>
          </tr>

          <!-- Expanded content row -->
          <tr
            v-if="expandable && isRowExpanded(row, dataIndex(idx))"
            data-slot="table-row-expanded"
            :class="cn('border-b bg-muted/30')"
          >
            <td
              :colspan="(selectable ? 1 : 0) + 1 + columns.length + ($slots.actions ? 1 : 0)"
              :class="cn('p-4')"
            >
              <slot name="expand" :row="row" :index="dataIndex(idx)" />
            </td>
          </tr>
        </template>

        <!-- Virtual scrolling spacer bottom -->
        <tr v-if="virtual && sortedData.length > 0" aria-hidden="true">
          <td
            :colspan="(selectable ? 1 : 0) + (expandable ? 1 : 0) + columns.length + ($slots.actions ? 1 : 0)"
            :style="{ height: `${totalHeight - virtualOffsetY - (visibleRows.length * virtualRowHeight)}px`, padding: 0, border: 'none' }"
          />
        </tr>
      </tbody>

      <!-- Summary footer -->
      <tfoot
        v-if="showSummary && sortedData && sortedData.length > 0"
        data-slot="table-footer"
        :class="cn('sticky bottom-0 bg-background border-t font-medium')"
      >
        <tr data-slot="table-row">
          <!-- Selectable placeholder -->
          <td
            v-if="selectable"
            data-slot="table-cell"
            :class="cn('w-10 px-2 text-center align-middle whitespace-nowrap')"
          />

          <!-- Expandable placeholder -->
          <td
            v-if="expandable"
            data-slot="table-cell"
            :class="cn('w-10 px-2 text-center align-middle whitespace-nowrap')"
          />

          <!-- Summary cells -->
          <td
            v-for="(column, colIndex) in columns"
            :key="column.key"
            data-slot="table-cell"
            :class="cn(
              'p-2 align-middle whitespace-nowrap',
              column.align === 'center' && 'text-center',
              column.align === 'right' && 'text-right',
              getFixedClass(column),
            )"
            :style="getFixedStyle(column)"
          >
            {{ summaryValues[colIndex] }}
          </td>

          <!-- Actions placeholder -->
          <td
            v-if="$slots.actions"
            data-slot="table-cell"
            :class="cn('p-2 text-right align-middle whitespace-nowrap')"
          />
        </tr>
      </tfoot>
    </table>
    </template>
    <div
      v-else
      data-slot="table-stack"
      class="flex flex-col gap-3 p-1"
    >
      <div
        v-if="!sortedData || sortedData.length === 0"
        class="flex items-center justify-center py-10 text-muted-foreground"
      >
        <slot name="empty">{{ emptyText }}</slot>
      </div>
      <div
        v-for="(row, idx) in visibleRows"
        :key="getRowKey(row, dataIndex(idx))"
        data-slot="table-stack-item"
        :class="cn(
          'rounded-lg border bg-card p-4 text-left',
          getRowClassName(row, dataIndex(idx)),
        )"
        @click="handleRowClick(row, dataIndex(idx))"
      >
        <div
          v-if="selectable"
          class="mb-3"
          @click.stop
        >
          <input
            type="checkbox"
            :checked="isRowSelected(row, dataIndex(idx))"
            class="size-4 rounded border border-primary accent-primary"
            @change="handleSelectRow(row, dataIndex(idx))"
          />
        </div>
        <div class="flex flex-col gap-2">
          <div
            v-for="(column, colIndex) in columns"
            :key="column.key"
            class="flex items-start gap-3"
          >
            <div class="w-20 shrink-0 pt-0.5 text-xs text-muted-foreground">
              {{ column.title }}
            </div>
            <div
              :class="cn(
                'min-w-0 flex-1 break-words text-sm',
                colIndex === 0 && 'font-medium',
              )"
            >
              <slot
                :name="`cell-${column.key}`"
                :row="row"
                :index="dataIndex(idx)"
                :value="row[column.key]"
              >
                {{ row[column.key] }}
              </slot>
            </div>
          </div>
        </div>
        <div
          v-if="expandable"
          class="mt-2"
          @click.stop="toggleRowExpand(row, dataIndex(idx))"
        >
          <button
            type="button"
            class="inline-flex items-center justify-center rounded p-0.5 hover:bg-muted"
            :class="isRowExpanded(row, dataIndex(idx)) && 'rotate-90'"
          >
            <ChevronRight class="size-4 text-muted-foreground" />
          </button>
        </div>
        <div
          v-if="expandable && isRowExpanded(row, dataIndex(idx))"
          class="mt-2"
        >
          <slot name="expand" :row="row" :index="dataIndex(idx)" />
        </div>
        <div
          v-if="$slots.actions"
          class="mt-3 flex justify-end"
          @click.stop
        >
          <slot name="actions" :row="row" :index="dataIndex(idx)" />
        </div>
      </div>
    </div>
  </div>
</template>
