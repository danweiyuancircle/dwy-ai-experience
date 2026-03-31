<script setup lang="ts">
import { computed, ref, onMounted, onBeforeUnmount } from 'vue'
import { LoaderCircle, ArrowUpDown, ArrowUp, ArrowDown, ChevronRight } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
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
})

const emit = defineEmits<ETableEmits>()

const sortState = ref<{ key: string; direction: 'asc' | 'desc' | null }>({
  key: '',
  direction: null,
})

// Sorted data — sort locally, also emit for parent override
const sortedData = computed(() => {
  if (!sortState.value.key || !sortState.value.direction) return props.data
  const key = sortState.value.key
  const dir = sortState.value.direction
  return [...props.data].sort((a, b) => {
    const va = a[key]
    const vb = b[key]
    if (va == null && vb == null) return 0
    if (va == null) return 1
    if (vb == null) return -1
    if (typeof va === 'number' && typeof vb === 'number') {
      return dir === 'asc' ? va - vb : vb - va
    }
    const sa = String(va)
    const sb = String(vb)
    return dir === 'asc' ? sa.localeCompare(sb) : sb.localeCompare(sa)
  })
})

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

// --- Fixed columns ---

/** Resolve a column width to a numeric pixel value for sticky offset calculation */
function resolveWidth(width: number | string | undefined): number {
  if (width == null) return 0
  if (typeof width === 'number') return width
  const num = parseFloat(width)
  return Number.isNaN(num) ? 0 : num
}

/** Columns fixed to the left, in their original order */
const leftFixedColumns = computed(() =>
  props.columns.filter((c) => c.fixed === 'left'),
)

/** Columns fixed to the right, in their original order */
const rightFixedColumns = computed(() =>
  props.columns.filter((c) => c.fixed === 'right'),
)

/** Map column key -> sticky left/right offset in px */
const fixedOffsets = computed(() => {
  const map: Record<string, { side: 'left' | 'right'; offset: number }> = {}

  // Left fixed: accumulate from left to right
  let leftAcc = 0
  // Account for selectable checkbox column (w-10 = 40px) before left-fixed columns
  if (props.selectable) {
    leftAcc += 40
  }
  // Account for expandable column (w-10 = 40px) before left-fixed columns
  if (props.expandable) {
    leftAcc += 40
  }
  for (const col of leftFixedColumns.value) {
    map[col.key] = { side: 'left', offset: leftAcc }
    leftAcc += resolveWidth(col.width)
  }

  // Right fixed: accumulate from right to left
  let rightAcc = 0
  // Account for actions column if present — placed after right-fixed columns
  // Actions column is after data columns, so it doesn't shift right-fixed offsets
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
    // Last left-fixed column gets the right shadow
    const leftCols = leftFixedColumns.value
    const isLast = leftCols[leftCols.length - 1]?.key === column.key
    return cn('bg-background', isLast && 'shadow-[2px_0_5px_-2px_rgba(0,0,0,0.1)]')
  }

  // First right-fixed column (in original order) gets the left shadow
  const rightCols = rightFixedColumns.value
  const isFirst = rightCols[0]?.key === column.key
  return cn('bg-background', isFirst && 'shadow-[-2px_0_5px_-2px_rgba(0,0,0,0.1)]')
}

// --- Expandable rows ---

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

// --- Row class name ---

function getRowClassName(row: Record<string, any>, index: number): string {
  if (!props.rowClassName) return ''
  if (typeof props.rowClassName === 'function') return props.rowClassName(row, index)
  return props.rowClassName
}

// --- Summary row ---

const summaryValues = computed<(string | number)[]>(() => {
  if (!props.showSummary) return []

  if (props.summaryMethod) {
    return props.summaryMethod(props.data, props.columns)
  }

  // Auto-sum: for each column, sum numeric values; first column shows "合计"
  return props.columns.map((col, colIndex) => {
    if (colIndex === 0) return '合计'
    const values = props.data.map((row) => row[col.key])
    const isNumeric = values.length > 0 && values.every((v) => v == null || typeof v === 'number')
    if (!isNumeric) return ''
    return values.reduce((sum: number, v) => sum + (v ?? 0), 0) as number
  })
})

// --- Virtual scrolling ---

const virtualContainerRef = ref<HTMLElement | null>(null)
const scrollTop = ref(0)
const containerHeight = ref(0)
const VIRTUAL_BUFFER = 5

function handleVirtualScroll(event: Event) {
  scrollTop.value = (event.target as HTMLElement).scrollTop
}

const totalHeight = computed(() => {
  if (!props.virtual) return 0
  return sortedData.value.length * props.virtualRowHeight
})

const virtualStartIndex = computed(() => {
  if (!props.virtual) return 0
  return Math.max(0, Math.floor(scrollTop.value / props.virtualRowHeight) - VIRTUAL_BUFFER)
})

const virtualEndIndex = computed(() => {
  if (!props.virtual) return sortedData.value.length
  const visibleCount = Math.ceil(containerHeight.value / props.virtualRowHeight)
  return Math.min(sortedData.value.length, Math.floor(scrollTop.value / props.virtualRowHeight) + visibleCount + VIRTUAL_BUFFER)
})

const visibleRows = computed(() => {
  if (!props.virtual) return sortedData.value
  return sortedData.value.slice(virtualStartIndex.value, virtualEndIndex.value)
})

const virtualOffsetY = computed(() => {
  return virtualStartIndex.value * props.virtualRowHeight
})

function initVirtualContainer() {
  if (!props.virtual || !virtualContainerRef.value) return
  containerHeight.value = virtualContainerRef.value.clientHeight
}

let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  if (props.virtual && virtualContainerRef.value) {
    initVirtualContainer()
    resizeObserver = new ResizeObserver(() => {
      if (virtualContainerRef.value) {
        containerHeight.value = virtualContainerRef.value.clientHeight
      }
    })
    resizeObserver.observe(virtualContainerRef.value)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

// --- Column resize ---

const columnWidths = ref<Record<string, number>>({})

/** Get effective column width — local override or from column config */
function getColumnWidth(column: TableColumn): number | string | undefined {
  if (props.resizable && columnWidths.value[column.key]) {
    return columnWidths.value[column.key]
  }
  return column.width
}

function getColumnStyle(column: TableColumn): Record<string, string | undefined> {
  const w = getColumnWidth(column)
  return {
    width: w ? (typeof w === 'number' ? `${w}px` : w) : undefined,
    minWidth: column.minWidth ? `${column.minWidth}px` : undefined,
    ...getFixedStyle(column),
  }
}

let resizeCol: string | null = null
let resizeStartX = 0
let resizeStartWidth = 0

function onResizeMouseDown(event: MouseEvent, column: TableColumn) {
  event.preventDefault()
  event.stopPropagation()
  resizeCol = column.key

  // Determine current width
  const currentWidth = columnWidths.value[column.key]
  if (currentWidth) {
    resizeStartWidth = currentWidth
  } else if (column.width) {
    resizeStartWidth = typeof column.width === 'number' ? column.width : parseFloat(column.width) || 100
  } else {
    // Measure actual rendered width from the th element
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
      'relative w-full overflow-auto',
      bordered && 'rounded-md border',
    )"
    v-on="virtual ? { scroll: handleVirtualScroll } : {}"
  >
    <!-- Loading overlay -->
    <div
      v-if="loading"
      class="absolute inset-0 z-10 flex items-center justify-center bg-background/80"
    >
      <LoaderCircle class="size-6 animate-spin text-muted-foreground" />
    </div>

    <table
      data-slot="table"
      :class="cn(
        'w-full caption-bottom text-sm',
        bordered && '[&_th]:border [&_td]:border',
        resizable && 'table-fixed',
        props.class,
      )"
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
          :key="getRowKey(row, virtual ? virtualStartIndex + idx : idx)"
        >
          <tr
            data-slot="table-row"
            :data-state="isRowSelected(row, virtual ? virtualStartIndex + idx : idx) ? 'selected' : undefined"
            :class="cn(
              'hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors',
              striped && (virtual ? virtualStartIndex + idx : idx) % 2 === 1 && 'bg-muted/40',
              getRowClassName(row, virtual ? virtualStartIndex + idx : idx),
            )"
            :style="virtual ? { height: `${virtualRowHeight}px` } : undefined"
            @click="handleRowClick(row, virtual ? virtualStartIndex + idx : idx)"
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
                :checked="isRowSelected(row, virtual ? virtualStartIndex + idx : idx)"
                class="size-4 rounded border border-primary accent-primary"
                @change="handleSelectRow(row, virtual ? virtualStartIndex + idx : idx)"
              />
            </td>

            <!-- Expand toggle -->
            <td
              v-if="expandable"
              data-slot="table-cell"
              :class="cn('w-10 px-2 text-center align-middle whitespace-nowrap bg-background')"
              :style="{ position: 'sticky', left: selectable ? '40px' : '0px', zIndex: 1 }"
              @click.stop="toggleRowExpand(row, virtual ? virtualStartIndex + idx : idx)"
            >
              <button
                type="button"
                class="inline-flex items-center justify-center rounded p-0.5 hover:bg-muted transition-transform duration-200"
                :class="isRowExpanded(row, virtual ? virtualStartIndex + idx : idx) && 'rotate-90'"
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
                :index="virtual ? virtualStartIndex + idx : idx"
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
              <slot name="actions" :row="row" :index="virtual ? virtualStartIndex + idx : idx" />
            </td>
          </tr>

          <!-- Expanded content row -->
          <tr
            v-if="expandable && isRowExpanded(row, virtual ? virtualStartIndex + idx : idx)"
            data-slot="table-row-expanded"
            :class="cn('border-b bg-muted/30')"
          >
            <td
              :colspan="(selectable ? 1 : 0) + 1 + columns.length + ($slots.actions ? 1 : 0)"
              :class="cn('p-4')"
            >
              <slot name="expand" :row="row" :index="virtual ? virtualStartIndex + idx : idx" />
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
  </div>
</template>
