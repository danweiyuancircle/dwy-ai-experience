<script setup lang="ts">
import { computed, ref } from 'vue'
import { LoaderCircle, ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-vue-next'
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
</script>

<template>
  <div
    data-slot="table-container"
    :class="cn(
      'relative w-full overflow-auto',
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

    <table
      data-slot="table"
      :class="cn(
        'w-full caption-bottom text-sm',
        bordered && '[&_th]:border [&_td]:border',
        props.class,
      )"
    >
      <!-- Header -->
      <thead
        data-slot="table-header"
        :class="cn('[&_tr]:border-b')"
      >
        <tr
          data-slot="table-row"
          :class="cn('hover:bg-muted/50 border-b transition-colors')"
        >
          <!-- Selection checkbox header -->
          <th
            v-if="selectable"
            data-slot="table-head"
            :class="cn('text-muted-foreground h-10 w-10 px-2 text-center align-middle font-medium whitespace-nowrap')"
          >
            <input
              type="checkbox"
              :checked="isAllSelected"
              :indeterminate="isIndeterminate"
              class="size-4 rounded border border-primary accent-primary"
              @change="handleSelectAll"
            />
          </th>

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
            )"
            :style="{
              width: column.width ? (typeof column.width === 'number' ? `${column.width}px` : column.width) : undefined,
              minWidth: column.minWidth ? `${column.minWidth}px` : undefined,
            }"
            @click="handleSort(column)"
          >
            <span class="inline-flex items-center gap-1">
              {{ column.title }}
              <ArrowUp v-if="getSortDirection(column) === 'asc'" class="size-3.5 text-foreground" />
              <ArrowDown v-else-if="getSortDirection(column) === 'desc'" class="size-3.5 text-foreground" />
              <ArrowUpDown v-else-if="column.sortable" class="size-3.5 opacity-40" />
            </span>
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
            :colspan="(selectable ? 1 : 0) + columns.length + ($slots.actions ? 1 : 0)"
            :class="cn('p-4 whitespace-nowrap align-middle text-sm')"
          >
            <div class="flex items-center justify-center py-10 text-muted-foreground">
              <slot name="empty">{{ emptyText }}</slot>
            </div>
          </td>
        </tr>

        <!-- Data rows -->
        <tr
          v-for="(row, rowIndex) in sortedData"
          :key="getRowKey(row, rowIndex)"
          data-slot="table-row"
          :data-state="isRowSelected(row, rowIndex) ? 'selected' : undefined"
          :class="cn(
            'hover:bg-muted/50 data-[state=selected]:bg-muted border-b transition-colors',
            striped && rowIndex % 2 === 1 && 'bg-muted/40',
          )"
          @click="handleRowClick(row, rowIndex)"
        >
          <!-- Selection checkbox -->
          <td
            v-if="selectable"
            data-slot="table-cell"
            :class="cn('w-10 px-2 text-center align-middle whitespace-nowrap')"
            @click.stop
          >
            <input
              type="checkbox"
              :checked="isRowSelected(row, rowIndex)"
              class="size-4 rounded border border-primary accent-primary"
              @change="handleSelectRow(row, rowIndex)"
            />
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
            )"
          >
            <slot
              :name="`cell-${column.key}`"
              :row="row"
              :index="rowIndex"
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
            <slot name="actions" :row="row" :index="rowIndex" />
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
