<!--
  EVirtualTable 简化版虚拟表格
  相比 ETable 更轻量，仅提供基础展示能力；通过固定容器高度 + 表头 sticky 实现可滚动区
  实际大数据量渲染推荐使用 ETable 的 virtual 开关；此组件保留作为独立视图
-->
<script setup lang="ts">
import { LoaderCircle } from 'lucide-vue-next'
import { cn } from '@/utils/cn'
import type { EVirtualTableProps, EVirtualTableEmits } from './types'

const props = withDefaults(defineProps<EVirtualTableProps>(), {
  columns: () => [],
  data: () => [],
  height: 400,
  estimateRowHeight: 40,
  rowKey: 'id',
  loading: false,
  emptyText: 'No data',
})

const emit = defineEmits<EVirtualTableEmits>()

/**
 * 根据列配置的对齐方向返回对应的 Tailwind class
 */
function getCellAlign(align?: string) {
  if (align === 'center') return 'text-center'
  if (align === 'right') return 'text-right'
  return 'text-left'
}
</script>

<template>
  <div
    :class="cn('relative rounded-md border overflow-hidden', props.class)"
    :style="{ height: `${props.height}px` }"
  >
    <!-- Loading overlay -->
    <div
      v-if="props.loading"
      class="absolute inset-0 z-10 flex items-center justify-center bg-background/60"
    >
      <LoaderCircle class="size-6 animate-spin text-muted-foreground" />
    </div>

    <div class="h-full overflow-auto">
      <table class="w-full caption-bottom text-sm">
        <thead class="sticky top-0 z-[1] bg-muted/50 backdrop-blur-sm">
          <tr class="border-b transition-colors">
            <th
              v-for="col in props.columns"
              :key="col.key"
              :style="col.width ? { width: typeof col.width === 'number' ? `${col.width}px` : col.width } : {}"
              :class="cn('h-10 px-4 font-medium text-muted-foreground', getCellAlign(col.align))"
            >
              {{ col.title }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(row, rowIndex) in props.data"
            :key="row[props.rowKey] ?? rowIndex"
            class="border-b transition-colors hover:bg-muted/50 cursor-pointer"
            @click="emit('row-click', row, rowIndex)"
          >
            <td
              v-for="col in props.columns"
              :key="col.key"
              :class="cn('p-4 align-middle', getCellAlign(col.align))"
            >
              <slot :name="`cell-${col.key}`" :row="row" :value="row[col.key]" :index="rowIndex">
                {{ row[col.key] }}
              </slot>
            </td>
          </tr>
          <tr v-if="props.data.length === 0">
            <td :colspan="props.columns.length" class="h-24 text-center text-muted-foreground">
              {{ props.emptyText }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
